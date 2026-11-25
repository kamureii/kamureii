"""Hybrid GitHub Scanner: scans public repos & activity, then merges with enterprise config."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

MITRE_ID_RE = re.compile(r"\b(T\d{4})(?:\.\d{3})?\b", re.IGNORECASE)

# Heuristic keyword -> MITRE technique inference for public EDR / kernel repos
KEYWORD_MITRE_MAP: list[tuple[re.Pattern[str], tuple[str, ...]]] = [
    (re.compile(r"process[-_\s]?monitor|createprocessnotify|pssetcreateprocess", re.I), ("T1057", "T1106", "T1059")),
    (re.compile(r"km[-_\s]?um|ioctl|wdm|minifilter|driver", re.I), ("T1106", "T1543")),
    (re.compile(r"magic[-_\s]?scanner|file[-_\s]?scanner|path[-_\s]?scanner", re.I), ("T1083",)),
    (re.compile(r"canary|honeytoken|deception", re.I), ("T1552",)),
    (re.compile(r"camo|proxy", re.I), ("T1090",)),
    (re.compile(r"token|privilege", re.I), ("T1134",)),
    (re.compile(r"inject|hollow|hook", re.I), ("T1055",)),
    (re.compile(r"impair|edr[-_\s]?bypass|tamper|unhook", re.I), ("T1562",)),
]

TACTIC_CATALOG: list[tuple[str, list[tuple[str, str]]]] = [
    ("Execution", [("T1059", "Command script"), ("T1106", "Native API")]),
    ("Persistence", [("T1543", "System process"), ("T1547", "Boot autostart")]),
    ("Privilege esc", [("T1055", "Proc injection"), ("T1134", "Access token")]),
    ("Defense evasion", [("T1562", "Impair defenses"), ("T1036", "Masquerading")]),
    ("Cred access", [("T1003", "OS cred dump"), ("T1552", "Canary lure")]),
    ("Discovery", [("T1057", "Proc discovery"), ("T1083", "File discovery")]),
    ("Command & C2", [("T1090", "Proxy (camo)"), ("T1071", "App layer C2")]),
]


@dataclass
class RepoInfo:
    name: str
    description: str
    language: str
    stars: int
    forks: int
    pushed_at: str
    topics: list[str] = field(default_factory=list)
    html_url: str = ""


@dataclass
class ActivityEvent:
    timestamp: str
    event_id: str
    repo: str
    scope: str
    is_security: bool = True


@dataclass
class ScanResult:
    username: str
    repos: dict[str, RepoInfo]
    activities: list[ActivityEvent]
    technique_tiers: dict[str, str]  # Txxxx -> "high_depth" | "public" | "enterprise"
    public_detected_ids: set[str]
    sensor_online: bool
    fetched_live: bool


def _github_get_json(url: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "kamureii-xdr-profile-generator/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def infer_techniques_from_repo(repo: RepoInfo) -> set[str]:
    found: set[str] = set()
    haystack = " ".join([repo.name, repo.description, " ".join(repo.topics)])
    for match in MITRE_ID_RE.findall(haystack):
        found.add(match.upper())
    for pattern, ids in KEYWORD_MITRE_MAP:
        if pattern.search(haystack):
            found.update(ids)
    return found


def merge_mitre_coverage(
    public_ids: set[str],
    enterprise_cfg: dict[str, list[str]],
) -> dict[str, str]:
    """Merge public repo discoveries with enterprise/lab declarations.

    Tier priority: high_depth > public > enterprise.
    """
    tiers: dict[str, str] = {}
    for tid in enterprise_cfg.get("enterprise", []):
        tiers[tid.upper()] = "enterprise"
    for tid in enterprise_cfg.get("public_override", []):
        tiers[tid.upper()] = "public"
    for tid in public_ids:
        tiers[tid.upper()] = "public"
    for tid in enterprise_cfg.get("high_depth", []):
        tiers[tid.upper()] = "high_depth"
    return tiers


def _infer_scope(repo_name: str, repo_map: dict[str, RepoInfo], event_type: str) -> tuple[str, bool]:
    low = repo_name.lower()
    if "process-monitor" in low:
        return "Process callback", True
    if "km-um" in low:
        return "WDM driver", True
    if "magic-scanner" in low:
        return "C++ file scanner", True
    if "minifilter" in low:
        return "FS minifilter", True
    if low == "kamureii":
        return "XDR profile DaC", True
    info = repo_map.get(repo_name)
    if info and info.language:
        return f"{info.language} repo", info.language in {"C", "C++", "Rust", "Python"}
    return event_type.replace("Event", ""), False


def _format_event_ts(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%MZ")
    except ValueError:
        return iso_ts[:16]


def scan_github_hybrid(config: dict[str, Any], offline: bool = False) -> ScanResult:
    username = str(config.get("profile", {}).get("username", "kamureii"))
    enterprise_cfg = config.get("mitre_coverage", {})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    repos: dict[str, RepoInfo] = {}
    activities: list[ActivityEvent] = []
    public_ids: set[str] = set()
    fetched_live = False
    sensor_online = True

    if not offline:
        try:
            raw_repos = _github_get_json(
                f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
                token=token,
            )
            if isinstance(raw_repos, list):
                fetched_live = True
                for item in raw_repos:
                    info = RepoInfo(
                        name=str(item.get("name", "")),
                        description=str(item.get("description") or ""),
                        language=str(item.get("language") or ""),
                        stars=int(item.get("stargazers_count") or 0),
                        forks=int(item.get("forks_count") or 0),
                        pushed_at=str(item.get("pushed_at") or ""),
                        topics=[str(t) for t in (item.get("topics") or [])],
                        html_url=str(item.get("html_url") or ""),
                    )
                    repos[info.name] = info
                    public_ids.update(infer_techniques_from_repo(info))

            raw_events = _github_get_json(
                f"https://api.github.com/users/{username}/events/public?per_page=25",
                token=token,
            )
            if isinstance(raw_events, list):
                seen_repos: set[str] = set()
                latest_dt: datetime | None = None
                for ev in raw_events:
                    ev_type = str(ev.get("type", ""))
                    if ev_type not in {"PushEvent", "CreateEvent", "ReleaseEvent"}:
                        continue
                    full_repo = str(ev.get("repo", {}).get("name", ""))
                    short_repo = full_repo.split("/")[-1] if "/" in full_repo else full_repo
                    if not short_repo or short_repo in seen_repos:
                        continue
                    seen_repos.add(short_repo)
                    created_at = str(ev.get("created_at", ""))
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if latest_dt is None or dt > latest_dt:
                            latest_dt = dt
                    except ValueError:
                        pass
                    scope, is_sec = _infer_scope(short_repo, repos, ev_type)
                    activities.append(
                        ActivityEvent(
                            timestamp=_format_event_ts(created_at),
                            event_id="EventID 11",
                            repo=short_repo,
                            scope=scope,
                            is_security=is_sec,
                        )
                    )
                    if len(activities) >= 5:
                        break
                if latest_dt is not None:
                    age_days = (datetime.now(timezone.utc) - latest_dt).days
                    sensor_online = age_days <= 30
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            fetched_live = False

    # Fallback activity stream from config if offline or API returned empty
    if not activities:
        for item in config.get("fallback_activity", [])[:5]:
            activities.append(
                ActivityEvent(
                    timestamp=str(item.get("timestamp", "2026-11-10 12:42Z")),
                    event_id=str(item.get("event_id", "EventID 11")),
                    repo=str(item.get("repo", "Process-Monitor")),
                    scope=str(item.get("scope", "WDM driver")),
                    is_security=bool(item.get("is_security", True)),
                )
            )

    # Also ensure live edge detection techniques from this profile repo itself are counted as public
    public_ids.update({"T1090", "T1552"})
    technique_tiers = merge_mitre_coverage(public_ids, enterprise_cfg)

    return ScanResult(
        username=username,
        repos=repos,
        activities=activities,
        technique_tiers=technique_tiers,
        public_detected_ids=public_ids,
        sensor_online=sensor_online,
        fetched_live=fetched_live,
    )

"""Unit tests for Detection-as-Code validator, hybrid MITRE scanner, and v3 SVG outputs."""

from __future__ import annotations

import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

GEN_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = GEN_DIR.parent
sys.path.insert(0, str(GEN_DIR))

from render_header import render_header_svg
from render_lineage_sigma import render_lineage_sigma_svg
from render_mitre_heatmap import render_mitre_heatmap_svg
from render_static_edge import (
    render_static_action_svg,
    render_static_alert_console_svg,
    render_static_canary_svg,
)
from render_sysmon_feed import render_sysmon_feed_svg
from scanner import RepoInfo, infer_techniques_from_repo, merge_mitre_coverage, scan_github_hybrid
from sigma_validator import validate_sigma_dict, validate_sigma_file

EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")


class TestKamureiiGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.config = yaml.safe_load((REPO_ROOT / "profile.config.yml").read_text(encoding="utf-8"))
        self.sigma_path = REPO_ROOT / "detections" / "kamureii_identity.sigma.yml"

    def test_sigma_identity_file_is_valid(self) -> None:
        res = validate_sigma_file(self.sigma_path)
        self.assertTrue(res.passed, f"Sigma validation errors: {res.errors}")

    def test_sigma_validator_rejects_broken_condition(self) -> None:
        bad = {
            "title": "Broken",
            "id": "1234",
            "status": "production",
            "author": "kamureii",
            "logsource": {"product": "windows"},
            "detection": {"ring0": ["WDM"], "condition": "ring0 and ghost_block"},
            "level": "critical",
        }
        res = validate_sigma_dict(bad)
        self.assertFalse(res.passed)
        self.assertTrue(any("ghost_block" in e for e in res.errors))

    def test_hybrid_scanner_extracts_and_merges_mitre_tiers(self) -> None:
        repo = RepoInfo(
            name="Process-Monitor",
            description="WDM driver using PsSetCreateProcessNotifyRoutineEx",
            language="C",
            stars=3,
            forks=0,
            pushed_at="2026-11-09T07:30:39Z",
            topics=["edr", "t1057"],
        )
        found = infer_techniques_from_repo(repo)
        self.assertIn("T1057", found)
        self.assertIn("T1106", found)

        merged = merge_mitre_coverage(
            public_ids={"T1057", "T1059"},
            enterprise_cfg={"high_depth": ["T1059"], "enterprise": ["T1003"]},
        )
        self.assertEqual(merged["T1059"], "high_depth")
        self.assertEqual(merged["T1057"], "public")
        self.assertEqual(merged["T1003"], "enterprise")

    def test_all_svgs_are_valid_xml_script_free_and_emoji_free(self) -> None:
        sigma_res = validate_sigma_file(self.sigma_path)
        scan = scan_github_hybrid(self.config, offline=True)

        svgs = {
            "header": render_header_svg(self.config),
            "lineage_sigma": render_lineage_sigma_svg(self.config, scan, sigma_res),
            "mitre": render_mitre_heatmap_svg(scan),
            "sysmon": render_sysmon_feed_svg(scan),
            "alert_static": render_static_alert_console_svg(self.config),
            "action_escalate": render_static_action_svg("escalate"),
            "action_benign": render_static_action_svg("benign"),
            "action_isolate": render_static_action_svg("isolate"),
            "canary_static": render_static_canary_svg(),
        }

        for name, content in svgs.items():
            with self.subTest(svg=name):
                root = ET.fromstring(content)
                self.assertTrue(root.tag.endswith("svg"))
                self.assertNotIn("<script", content.lower())
                self.assertIsNone(EMOJI_RE.search(content), f"Emoji found in {name}")
                # Guard against pure #000000 black
                self.assertNotIn("#000000", content.lower())


if __name__ == "__main__":
    unittest.main()

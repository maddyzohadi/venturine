"""Repository hygiene tests.

Checks security rules (agent permissions, calculator imports), manifest and
changelog consistency, required project files, markdown links, workflow
pinning, and the social preview image. Standard library only.
"""

import ast
import json
import re
import shlex
import struct
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.calculator import ENGINE_VERSION

ROOT = Path(__file__).resolve().parents[1]

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def frontmatter(relative):
    """Return (scalars, lists) parsed from simple YAML frontmatter."""
    text = read(relative)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{relative} has no frontmatter")
    scalars, lists, current = {}, {}, None
    for line in match.group(1).splitlines():
        item = re.match(r"^\s+-\s+(.*)$", line)
        key = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if item and current:
            lists[current].append(item.group(1).strip())
        elif key:
            current = key.group(1)
            if key.group(2):
                scalars[current] = key.group(2).strip()
            else:
                lists[current] = []
    return scalars, lists


def markdown_files():
    skip = {".git"}
    return [
        p for p in ROOT.rglob("*.md")
        if not (set(p.relative_to(ROOT).parts) & skip)
    ]


class TestAgentPermissions(unittest.TestCase):

    def agent_files(self):
        files = sorted((ROOT / "agents").glob("*.md"))
        self.assertTrue(files, "no agent definitions found")
        return files

    def test_no_agent_has_bash(self):
        for path in self.agent_files():
            _, lists = frontmatter(path.relative_to(ROOT).as_posix())
            tools = lists.get("tools", [])
            self.assertTrue(tools, f"{path.name} lists no tools")
            for tool in tools:
                self.assertFalse(
                    tool.lower().startswith("bash"),
                    f"{path.name} must not grant {tool}",
                )

    def test_agents_cannot_write_files(self):
        for path in self.agent_files():
            _, lists = frontmatter(path.relative_to(ROOT).as_posix())
            for tool in lists.get("tools", []):
                self.assertNotIn(
                    tool, {"Write", "Edit", "NotebookEdit"},
                    f"{path.name} must not grant {tool}",
                )

    def test_agent_frontmatter_complete(self):
        for path in self.agent_files():
            scalars, _ = frontmatter(path.relative_to(ROOT).as_posix())
            self.assertEqual(scalars.get("name"), path.stem)
            self.assertTrue(scalars.get("description"))

    def test_web_agents_treat_fetched_content_as_untrusted(self):
        for name in ("research-lead", "evidence-auditor"):
            text = read(f"agents/{name}.md")
            self.assertIn("## Untrusted Content", text, name)
            self.assertIn("data, not instructions", text, name)


class TestSkills(unittest.TestCase):

    def test_skill_frontmatter(self):
        skills = sorted((ROOT / "skills").iterdir())
        self.assertTrue(skills)
        for directory in skills:
            relative = (directory / "SKILL.md").relative_to(ROOT).as_posix()
            scalars, _ = frontmatter(relative)
            self.assertEqual(scalars.get("name"), directory.name)
            self.assertTrue(scalars.get("description"), directory.name)


class TestNoHiddenExecution(unittest.TestCase):

    def test_no_hooks_or_bundled_servers(self):
        self.assertFalse((ROOT / "hooks").exists())
        self.assertFalse((ROOT / ".mcp.json").exists())
        self.assertFalse((ROOT / ".claude-plugin" / "hooks.json").exists())

    def test_calculator_imports_are_limited(self):
        # "re" is used only to validate the numeric input syntax.
        allowed = {
            "decimal", "argparse", "json", "re", "scripts", "calculator",
        }
        for path in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                for module in modules:
                    self.assertIn(
                        module.split(".")[0], allowed,
                        f"{path.name} imports {module}",
                    )

    def test_calculator_does_not_open_files_or_eval(self):
        forbidden = {"open", "exec", "eval", "compile", "__import__"}
        for path in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(
                    node.func, ast.Name
                ):
                    self.assertNotIn(
                        node.func.id, forbidden,
                        f"{path.name} calls {node.func.id}",
                    )


class TestManifestConsistency(unittest.TestCase):

    def setUp(self):
        self.plugin = json.loads(read(".claude-plugin/plugin.json"))

    def test_version_is_semver(self):
        self.assertRegex(self.plugin["version"], SEMVER)

    def test_changelog_has_current_version(self):
        self.assertIn(f"## [{self.plugin['version']}]", read("CHANGELOG.md"))

    def test_license_is_apache(self):
        self.assertEqual(self.plugin["license"], "Apache-2.0")

    def test_author_present(self):
        self.assertTrue(self.plugin["author"]["name"])

    def test_readme_names_engine_version(self):
        self.assertIn(f"v{ENGINE_VERSION}", read("README.md"))

    def test_marketplace_lists_plugin(self):
        market = json.loads(read(".claude-plugin/marketplace.json"))
        names = [p["name"] for p in market["plugins"]]
        self.assertIn(self.plugin["name"], names)


class TestLicenseAndTrademark(unittest.TestCase):

    def test_license_is_full_apache_2(self):
        text = read("LICENSE")
        for needle in (
            "Apache License",
            "Version 2.0, January 2004",
            "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION",
            "6. Trademarks.",
            "END OF TERMS AND CONDITIONS",
            "APPENDIX: How to apply the Apache License",
        ):
            self.assertIn(needle, text)

    def test_notice_has_copyright_holder(self):
        text = read("NOTICE")
        self.assertIn("Copyright 2026 Mahdokht Zohadi", text)
        self.assertIn("Apache License, Version 2.0", text)

    def test_no_stale_mit_references(self):
        for relative in (
            "LICENSE", "NOTICE", "README.md", "CONTRIBUTING.md",
            "TRADEMARK.md", ".claude-plugin/plugin.json",
            "docs/release-notes/v0.2.1.md",
        ):
            self.assertNotRegex(read(relative), r"\bMIT\b", relative)

    def test_trademark_policy_makes_no_registration_claim(self):
        text = read("TRADEMARK.md")
        self.assertIn("does not grant permission to use the Venturine name or logo", text)
        self.assertIn("makes no claim that", text)
        for symbol in ("®", "™"):
            self.assertNotIn(symbol, text)

    def test_readme_states_name_and_logo_limit(self):
        text = read("README.md")
        self.assertIn("does not grant permission to use the Venturine name or logo", text)
        self.assertIn("TRADEMARK.md", text)


class TestRequiredFiles(unittest.TestCase):

    REQUIRED = [
        "LICENSE", "NOTICE", "README.md", "TRADEMARK.md", "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md",
        "docs/security-and-privacy.md", "docs/competitive-landscape.md",
        "docs/examples.md", "docs/roadmap.md", "docs/release-notes/v0.2.1.md",
        "docs/evidence-terminology.md", "docs/releasing.md",
        "docs/handoff-v1.md", "docs/handoff-v1.example.json",
        "schemas/venturine-handoff.v1.schema.json",
        "scripts/validate_handoff.py",
        "skills/venture-intake/SKILL.md", "skills/evidence-audit/SKILL.md",
        "agents/red-team-reviewer.md",
        "docs/commit-metadata.md", "docs/repository-settings.md",
        ".gitignore", ".github/workflows/release-check.yml",
        ".github/PULL_REQUEST_TEMPLATE.md", ".github/CODEOWNERS",
        ".github/dependabot.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/evidence_or_calculation_issue.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        "assets/logo.svg", "assets/social-preview.svg",
        "assets/social-preview.png",
    ]

    def test_required_files_exist_and_are_not_empty(self):
        for relative in self.REQUIRED:
            path = ROOT / relative
            self.assertTrue(path.is_file(), f"missing {relative}")
            self.assertGreater(path.stat().st_size, 0, relative)

    def test_issue_forms_are_well_formed(self):
        for name in ("bug_report", "feature_request",
                     "evidence_or_calculation_issue"):
            text = read(f".github/ISSUE_TEMPLATE/{name}.yml")
            for key in ("name:", "description:", "body:"):
                self.assertIn(key, text, name)
            self.assertNotIn("\t", text, f"{name} contains tabs")

    def test_issue_chooser_blocks_blank_issues(self):
        text = read(".github/ISSUE_TEMPLATE/config.yml")
        self.assertIn("blank_issues_enabled: false", text)


class TestDocumentation(unittest.TestCase):

    LINK = re.compile(r"\]\(([^)\s]+)\)")
    IMG = re.compile(r"<img[^>]+src=\"([^\"]+)\"")

    def test_relative_links_resolve(self):
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            targets = self.LINK.findall(text) + self.IMG.findall(text)
            for target in targets:
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                clean = target.split("#")[0]
                if not clean:
                    continue
                resolved = (path.parent / clean).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"{path.relative_to(ROOT)} links to missing {target}",
                )

    def test_examples_are_labeled_hypothetical(self):
        text = read("docs/examples.md").lower()
        self.assertIn("hypothetical", text)
        self.assertNotIn("testimonial:", text)

    def test_competitive_research_is_dated_and_sourced(self):
        text = read("docs/competitive-landscape.md")
        self.assertRegex(text, r"Research date: \d{4}-\d{2}-\d{2}")
        self.assertIn("## Sources", text)
        self.assertIn("https://github.com/", text)

    def test_security_doc_matches_agent_permissions(self):
        text = read("docs/security-and-privacy.md")
        for agent in ("research-lead", "evidence-auditor", "financial-analyst",
                      "red-team-reviewer"):
            self.assertIn(agent, text)


class TestWorkflows(unittest.TestCase):

    def workflows(self):
        files = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        self.assertTrue(files)
        return files

    def test_actions_are_pinned_to_commit_shas(self):
        for path in self.workflows():
            for line in path.read_text(encoding="utf-8").splitlines():
                match = re.match(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", line)
                if not match:
                    continue
                ref = match.group(1)
                self.assertIn("@", ref, f"{path.name}: {ref}")
                self.assertRegex(
                    ref.split("@", 1)[1], SHA,
                    f"{path.name}: {ref} is not pinned to a commit SHA",
                )

    def test_cli_install_is_version_pinned(self):
        for path in self.workflows():
            for line in path.read_text(encoding="utf-8").splitlines():
                if "npm install" in line and "claude-code" in line:
                    self.assertRegex(
                        line, r"@anthropic-ai/claude-code@\d+\.\d+\.\d+",
                        f"{path.name}: unpinned CLI install",
                    )

    def test_least_privilege_and_timeouts(self):
        for path in self.workflows():
            text = path.read_text(encoding="utf-8")
            self.assertIn("permissions:\n  contents: read", text, path.name)
            self.assertIn("timeout-minutes:", text, path.name)
            self.assertIn("persist-credentials: false", text, path.name)
            self.assertNotIn("pull_request_target", text, path.name)


class TestSocialPreview(unittest.TestCase):

    def test_png_is_valid_size_and_under_github_limit(self):
        data = (ROOT / "assets" / "social-preview.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1280, 640))
        self.assertLess(len(data), 1_000_000)

    def test_svg_sources_are_svg(self):
        for name in ("logo.svg", "social-preview.svg"):
            text = read(f"assets/{name}")
            self.assertIn("<svg", text)
            self.assertNotIn("<script", text)


class TestDocumentedCalculatorCommands(unittest.TestCase):
    """Guards for the audit findings on command shadowing (H1): documented
    commands must use the file-path form, and every one must really run."""

    SKILL_CMD = re.compile(
        r'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/scripts/calculate\.py" ([^`\n]+)'
    )
    REPO_CMD = re.compile(r"^python3 scripts/calculate\.py (.+)$", re.M)

    def user_facing_docs(self):
        files = ["README.md", "docs/examples.md"]
        files += [p.relative_to(ROOT).as_posix()
                  for p in (ROOT / "skills").glob("*/SKILL.md")]
        files += [p.relative_to(ROOT).as_posix()
                  for p in (ROOT / "agents").glob("*.md")]
        return files

    def test_no_documented_command_uses_the_shadowable_form(self):
        for relative in self.user_facing_docs():
            text = read(relative)
            self.assertNotIn("PYTHONPATH=", text, relative)
            self.assertNotIn("python3 -m scripts.calculate", text, relative)

    def run_documented(self, args):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "calculate.py"),
             *shlex.split(args)],
            capture_output=True, text=True, timeout=20, cwd=ROOT,
            check=False,
        )

    def test_every_skill_command_runs_and_all_operations_are_covered(self):
        from scripts.calculate import OPERATIONS

        commands = self.SKILL_CMD.findall(read("skills/unit-economics/SKILL.md"))
        self.assertTrue(commands)
        seen = set()
        for args in commands:
            result = self.run_documented(args)
            self.assertEqual(result.returncode, 0, f"{args}: {result.stderr}")
            seen.add(json.loads(result.stdout)["operation"])
        self.assertEqual(seen, set(OPERATIONS))

    def test_every_readme_and_example_command_runs(self):
        for relative in ("README.md", "docs/examples.md"):
            commands = self.REPO_CMD.findall(read(relative))
            self.assertTrue(commands, relative)
            for args in commands:
                result = self.run_documented(args)
                self.assertEqual(
                    result.returncode, 0, f"{relative}: {args}: {result.stderr}"
                )

    def test_documented_json_versions_match_the_engine(self):
        for match in re.findall(r'"version": "([^"]+)"', read("docs/examples.md")):
            self.assertEqual(match, ENGINE_VERSION)


if __name__ == "__main__":
    unittest.main()

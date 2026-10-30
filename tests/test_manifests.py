import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins/fortls-lsp"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path} has no front matter"
    return dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)


class Manifests(unittest.TestCase):
    def setUp(self):
        self.plugin = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
        self.market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())

    def test_versions_agree(self):
        entry = self.market["plugins"][0]
        self.assertEqual(entry["name"], self.plugin["name"])
        self.assertEqual(entry["version"], self.plugin["version"])
        top = re.search(r"^## (\S+)", (ROOT / "CHANGELOG.md").read_text(), re.M).group(1)
        self.assertEqual(top, self.plugin["version"])

    def test_name_pattern(self):
        self.assertRegex(self.plugin["name"], r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")

    def test_skills_load_everywhere(self):
        skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            fm = frontmatter(skill)
            self.assertEqual(fm["name"], skill.parent.name)
            self.assertLessEqual(len(fm["description"]), 1024)
            self.assertLess(len(skill.read_text().splitlines()), 500)
            for ref in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/(\S+?)[`\s]", skill.read_text()):
                self.assertTrue((skill.parent / ref).is_file(), ref)
        self.assertFalse((PLUGIN / "bin").exists(), "a top-level bin/ blocks chat and Cowork")

    def test_directory_file_rules(self):
        files = [p for p in PLUGIN.rglob("*") if p.is_file()]
        self.assertLessEqual(len(files), 512)
        for p in files:
            self.assertNotIn(p.name, {".DS_Store", "Thumbs.db", "desktop.ini"})
            self.assertFalse(p.is_symlink(), p)
            if p.suffix != ".png":
                self.assertLess(p.stat().st_size, 256 * 1024, p)
                text = p.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"[\w.+-]+@[\w-]+\.[\w.]+", f"email address in {p}")
                self.assertNotRegex(text, r"/(home|Users)/\w+", f"home path in {p}")

    def test_readme_long_enough(self):
        text = re.sub(r"```.*?```", "", (PLUGIN / "README.md").read_text(), flags=re.S)
        self.assertGreaterEqual(len(text.split()), 40)
        self.assertIn("## Privacy", text)


if __name__ == "__main__":
    unittest.main()

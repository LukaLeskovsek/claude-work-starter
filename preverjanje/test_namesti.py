"""Personal installation in disposable homes only."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("namesti", Path(__file__).resolve().parents[1] / "setup/namesti.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.work = self.root / "Moje delo"
        self.work.mkdir()

    def test_requires_approval(self):
        with self.assertRaises(ValueError):
            n.install(self.home, self.work)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_install_repeat_preserves_global_instructions(self):
        global_file = self.home / ".claude/CLAUDE.md"
        global_file.parent.mkdir()
        global_file.write_text("My existing AIOS", encoding="utf-8")
        result = n.install(self.home, self.work, approved=True)
        target = Path(result["installed"])
        times = {f: (target / f).stat().st_mtime_ns for f in n.FILES}
        n.install(self.home, self.work, approved=True)
        self.assertEqual(times, {f: (target / f).stat().st_mtime_ns for f in n.FILES})
        self.assertEqual(global_file.read_text(encoding="utf-8"), "My existing AIOS")

    def test_customized_personal_skill_is_not_overwritten(self):
        target = Path(n.install(self.home, self.work, approved=True)["installed"])
        (target / "SKILL.md").write_text("my custom instructions")
        with self.assertRaises(ValueError):
            n.install(self.home, self.work, approved=True)
        self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "my custom instructions")

    def test_customized_project_preflight_prevents_personal_install(self):
        project = self.work / ".claude/skills/dokumenti"
        project.mkdir(parents=True)
        (project / "SKILL.md").write_text("my special restrictions")
        with self.assertRaises(ValueError):
            n.install(self.home, self.work, approved=True, migrate=True)
        self.assertFalse((self.home / ".claude/skills/dokumenti").exists())
        self.assertTrue(project.exists())

    def test_known_project_moved_to_private_recoverable_backup(self):
        project = self.work / ".claude/skills/dokumenti"
        project.mkdir(parents=True)
        old = b"test old release"
        (project / "SKILL.md").write_bytes(old)
        actual_blob = n.blob
        def read(path):
            if Path(path).name == "predhodne-izdaje.json":
                return json.dumps({"fixture": {"dokumenti/SKILL.md": n.digest(old)}}).encode()
            return actual_blob(path)
        with patch.object(n, "blob", side_effect=read):
            result = n.install(self.home, self.work, approved=True, migrate=True)
        self.assertFalse(project.exists())
        self.assertEqual((Path(result["backup"]) / "projektni-dokumenti/SKILL.md").read_bytes(), old)


if __name__ == "__main__":
    unittest.main(verbosity=2)

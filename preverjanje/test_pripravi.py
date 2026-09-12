"""Isolated package bootstrap tests; never use personal folders."""
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
import warnings
import zipfile

spec = importlib.util.spec_from_file_location("pripravi", Path(__file__).resolve().parents[1] / "setup/pripravi.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "Moje delo"
        self.root.mkdir()
        source = Path(__file__).resolve().parents[1]
        self.files = {n: (source / n).read_bytes() for n in p.FILES}

    def package(self, names=None, symlink=None):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for n in (names if names is not None else self.files):
                if n == symlink:
                    info = zipfile.ZipInfo(n)
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    z.writestr(info, self.files[n])
                else:
                    z.writestr(n, self.files.get(n, b"unexpected"))
        archive = buf.getvalue()
        return archive, {"version": p.VERSION, "archive_url": p.ARCHIVE_URL,
                         "sha256": p.digest(archive),
                         "files": {n: p.digest(d) for n, d in self.files.items()}}

    def test_complete_flat_package_and_local_continuation(self):
        result = p.unpack(self.root, *self.package())
        self.assertEqual(result["created"], len(p.FILES))
        self.assertFalse((self.root / "claude-work-starter").exists())
        self.assertEqual({f.relative_to(self.root).as_posix() for f in self.root.rglob("*") if f.is_file()}, set(p.FILES))
        self.assertIn("## 1. Najprej obseg", Path(result["next"]).read_text(encoding="utf-8"))

    def test_routine_setup_is_agent_driven_and_uses_supported_desktop_path(self):
        source = Path(__file__).resolve().parents[1]
        guide = (source / "NASTAVI-CLAUDE.md").read_text(encoding="utf-8")
        routine = (source / "predloge/DNEVNA-RUTINA.md").read_text(encoding="utf-8")
        self.assertIn("sam ustvari ali posodobi", guide)
        self.assertIn("starejši od 1.1.5368", guide)
        self.assertIn("najprej preveri seznam obstoječih lokalnih rutin", routine)
        self.assertIn("vsak dan ob 9.00 po lokalnem času", routine)
        self.assertIn("neposredno v `~/.claude/scheduled-tasks/`", routine)

    def test_rerun_is_noop(self):
        archive, manifest = self.package()
        p.unpack(self.root, archive, manifest)
        times = {n: (self.root / n).stat().st_mtime_ns for n in p.FILES}
        self.assertEqual(p.unpack(self.root, archive, manifest)["created"], 0)
        self.assertEqual(times, {n: (self.root / n).stat().st_mtime_ns for n in p.FILES})

    def test_existing_work_and_personalization_preserved(self):
        for n in ("CLAUDE.md", "MOJ-DELOVNI-PROFIL.md", "racun.docx"):
            (self.root / n).write_bytes(b"keep")
        p.unpack(self.root, *self.package())
        for n in ("CLAUDE.md", "MOJ-DELOVNI-PROFIL.md", "racun.docx"):
            self.assertEqual((self.root / n).read_bytes(), b"keep")

    def test_conflict_writes_nothing(self):
        (self.root / "ZACNI-TUKAJ.txt").write_bytes(b"my file")
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package())
        self.assertEqual(list(self.root.iterdir()), [self.root / "ZACNI-TUKAJ.txt"])
        self.assertEqual((self.root / "ZACNI-TUKAJ.txt").read_bytes(), b"my file")

    def test_case_collision(self):
        (self.root / "readme.md").write_bytes(b"keep")
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package())
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_file_blocks_directory(self):
        (self.root / "setup").write_bytes(b"keep")
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package())
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_destination_symlink(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.root / "dokumenti").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package())
        self.assertEqual(list(outside.iterdir()), [])

    def test_reject_unexpected_paths_nesting_and_duplicates(self):
        for bad in ("../escape", "/escape", "C:\\escape", "dokumenti\\escape", "claude-work-starter/README.md", "README.md"):
            with self.subTest(bad=bad), warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with self.assertRaises(ValueError):
                    p.unpack(self.root, *self.package(list(self.files) + [bad]))
                self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_archive_symlink(self):
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package(symlink="README.md"))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_missing_file(self):
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package(list(self.files)[1:]))

    def test_reject_bad_archive_and_file_hashes(self):
        for location in ("archive", "file"):
            archive, manifest = self.package()
            if location == "archive":
                manifest["sha256"] = "0" * 64
            else:
                manifest["files"]["README.md"] = "0" * 64
            with self.assertRaises(ValueError):
                p.unpack(self.root, archive, manifest)
            self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_wrong_version_url_or_manifest(self):
        for key, value in (("version", "old"), ("archive_url", "https://example.com/other.zip"), ("files", {})):
            archive, manifest = self.package()
            manifest[key] = value
            with self.assertRaises(ValueError):
                p.unpack(self.root, archive, manifest)

    def test_approved_known_upgrade_keeps_recoverable_backup(self):
        old = b"known old starter README"
        (self.root / "README.md").write_bytes(old)
        self.files["setup/predhodne-izdaje.json"] = json.dumps({"fixture": {"README.md": p.digest(old)}}).encode()
        result = p.unpack(self.root, *self.package(), upgrade=True)
        self.assertEqual(result["updated"], 1)
        self.assertEqual((Path(result["backup"]) / "README.md").read_bytes(), old)
        self.assertEqual((self.root / "README.md").read_bytes(), self.files["README.md"])

    def test_upgrade_never_overwrites_customized_files(self):
        old = b"my customized README"
        (self.root / "README.md").write_bytes(old)
        with self.assertRaises(ValueError):
            p.unpack(self.root, *self.package(), upgrade=True)
        self.assertEqual(list(self.root.iterdir()), [self.root / "README.md"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Isolated fixtures only; never uses the user's work folders."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "dokumenti/scripts/dokumenti.py"
spec = importlib.util.spec_from_file_location("dokumenti", SCRIPT)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class DocumentsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="iri-starter-test-")
        self.root = Path(self.temp.name).resolve()
        (self.root / "Sestanki").mkdir()
        (self.root / "Drugi").mkdir()
        (self.root / "Zasebno").mkdir()
        (self.root / ".skrito").mkdir()
        (self.root / "node_modules").mkdir()
        self.doc = self.root / "Sestanki/Primer.DOCX"
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
               '<w:p><w:r><w:t>Uvod v sestanek</w:t></w:r></w:p>'
               '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Naloga A</w:t></w:r></w:p></w:tc>'
               '<w:tc><w:p><w:r><w:t>Rok ni določen</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
               '<w:p><w:r><w:t>Naslednji korak</w:t></w:r></w:p></w:body></w:document>')
        with zipfile.ZipFile(self.doc, "w") as archive:
            archive.writestr("word/document.xml", xml)
        (self.root / "Drugi/Primer.DOCX").write_bytes(self.doc.read_bytes())
        for rel in ("Zasebno/osebno.pdf", ".skrito/skrito.pdf", "node_modules/test.pdf"):
            (self.root / rel).write_bytes(b"not a real pdf")
        (self.root / "zapis.txt").write_text("Varen test", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_read_only_count_exclusions_and_case(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        data = d.inventory(self.root, ["Zasebno"])
        self.assertEqual(d.summary(data)["by_type"], {".docx": 2, ".txt": 1})
        self.assertEqual(len(data["skipped"]), 3)
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))

    def test_docx_order_provenance_and_no_source_changes(self):
        before = self.doc.read_bytes()
        output = d.read_source(self.root, "Sestanki/Primer.DOCX", [])
        self.assertIn('"Sestanki/Primer.DOCX"', output)
        self.assertIn(hashlib.sha256(before).hexdigest(), output)
        self.assertLess(output.index("Uvod v sestanek"), output.index("Naloga A"))
        self.assertLess(output.index("Naloga A"), output.index("Naslednji korak"))
        self.assertIn("Rok ni določen", output)
        self.assertEqual(before, self.doc.read_bytes())
        self.assertFalse((self.root / d.OUTPUT).exists())

    def test_duplicate_basenames_preserved_and_catalogue_refresh(self):
        d.save_catalogue(self.root, d.inventory(self.root, ["Zasebno"]))
        data = json.loads((self.root / d.OUTPUT / "inventar.json").read_text(encoding="utf-8"))
        self.assertEqual(len([f for f in data["files"] if f["type"] == ".docx"]), 2)
        self.assertEqual(d.saved_exclusions(self.root), ["Zasebno"])
        d.save_catalogue(self.root, d.inventory(self.root, d.saved_exclusions(self.root)))
        self.assertEqual(len(json.loads((self.root / d.OUTPUT / "inventar.json").read_text(encoding="utf-8"))["files"]), 3)

    def test_cli_keeps_exclusions_even_if_flag_is_omitted(self):
        d.save_catalogue(self.root, d.inventory(self.root, ["Zasebno"]))
        out = io.StringIO()
        with mock.patch("sys.argv", ["dokumenti", "--root", str(self.root), "pregled"]), contextlib.redirect_stdout(out):
            result = d.main()
        self.assertEqual(result, 0)
        self.assertNotIn(".pdf", json.loads(out.getvalue())["by_type"])

    def test_exclusions_ignore_case(self):
        self.assertTrue(d.blocked("zasebno/osebno.pdf", ["Zasebno"]))
        self.assertTrue(d.blocked("ZASEBNO/osebno.pdf", ["Zasebno"]))
        with self.assertRaises(ValueError):
            d.safe_source(self.root, "zasebno/osebno.pdf", ["Zasebno"])

    def test_shared_catalogue_works_at_different_local_path(self):
        d.save_catalogue(self.root, d.inventory(self.root, ["Zasebno"]))
        with tempfile.TemporaryDirectory(prefix="iri-relocated-test-") as moved:
            new_root = Path(moved).resolve() / "Delovna mapa"
            shutil.copytree(self.root, new_root)
            exclusions = d.saved_exclusions(new_root)
            self.assertEqual(exclusions, ["Zasebno"])
            d.save_catalogue(new_root, d.inventory(new_root, exclusions))
            data = json.loads((new_root / d.OUTPUT / "inventar.json").read_text(encoding="utf-8"))
            self.assertEqual(data["root"], str(new_root))
            self.assertNotIn(".pdf", d.summary(data)["by_type"])

    def test_no_unowned_overwrite(self):
        folder = self.root / d.OUTPUT
        folder.mkdir()
        (folder / "KAZALO.md").write_text("Uporabnikov zapis")
        with self.assertRaises(ValueError):
            d.save_catalogue(self.root, d.inventory(self.root, []))
        self.assertEqual((folder / "KAZALO.md").read_text(encoding="utf-8"), "Uporabnikov zapis")

    def test_traversal_and_excluded_read_refused(self):
        for path in ("../other.docx", str(self.doc), "Zasebno/osebno.pdf", ".skrito/skrito.pdf"):
            with self.assertRaises(ValueError):
                d.safe_source(self.root, path, ["Zasebno"])

    def test_symlink_skipped_and_unreadable(self):
        link = self.root / "povezava.docx"
        link.symlink_to(self.doc)
        data = d.inventory(self.root, ["Zasebno"])
        self.assertIn("povezava.docx", [p["path"] for p in data["skipped"]])
        with self.assertRaises(ValueError):
            d.read_source(self.root, "povezava.docx", [])

    def test_directory_error_is_visible(self):
        original = d.os.scandir
        def denied(path):
            if Path(path).name == "Sestanki":
                raise PermissionError("Test: ni dostopa")
            return original(path)
        with mock.patch.object(d.os, "scandir", side_effect=denied):
            data = d.inventory(self.root, [])
        self.assertEqual(data["errors"][0]["path"], "Sestanki")

    def test_corrupt_docx_no_stale_content(self):
        self.assertIn("Uvod v sestanek", d.read_source(self.root, "Sestanki/Primer.DOCX", []))
        self.doc.write_bytes(b"corrupt")
        with self.assertRaises(zipfile.BadZipFile):
            d.read_source(self.root, "Sestanki/Primer.DOCX", [])

    def test_text_pdf_page_selection_and_blank_warning(self):
        from reportlab.pdfgen import canvas
        path = self.root / "dve-strani.pdf"
        pdf = canvas.Canvas(str(path))
        pdf.drawString(30, 800, "Project Alpha 123")
        pdf.showPage()
        pdf.showPage()
        pdf.save()
        output = d.read_source(self.root, "dve-strani.pdf", [], "1")
        self.assertIn("Project Alpha 123", output)
        self.assertNotIn("## Stran 2", output)
        output = d.read_source(self.root, "dve-strani.pdf", [], "2")
        self.assertIn("Stran 2: brez izvlečenega besedila", output)
        with self.assertRaises(ValueError):
            d.read_source(self.root, "dve-strani.pdf", [], "3")

    def test_empty_converter_output_does_not_invent_blank_page(self):
        import subprocess
        with mock.patch.object(d.shutil, "which", return_value="pdftotext"), mock.patch.object(
                d.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"", b"")):
            with self.assertRaises(ValueError):
                d.read_pdf(self.root / "unused.pdf", "3")

    def test_image_only_pdf_does_not_claim_empty_document(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from PIL import Image
        path = self.root / "brez-besedila.pdf"
        pdf = canvas.Canvas(str(path))
        pdf.drawImage(ImageReader(Image.new("RGB", (40, 20), "navy")), 30, 500, 150, 100)
        pdf.save()
        output = d.read_source(self.root, "brez-besedila.pdf", [])
        self.assertIn("potreben vizualni pregled", output)
        self.assertIn("vsebina ni potrjena", output)

    def test_pypdf_fallback(self):
        from reportlab.pdfgen import canvas
        path = self.root / "fallback.pdf"
        pdf = canvas.Canvas(str(path))
        pdf.drawString(30, 800, "Fallback 42")
        pdf.save()
        with mock.patch.object(d.shutil, "which", return_value=None):
            output = d.read_source(self.root, "fallback.pdf", [])
        self.assertIn("Bralnik: pypdf", output)
        self.assertIn("Fallback 42", output)

    def test_pdf_converter_receives_requested_range(self):
        import subprocess
        with mock.patch.object(d.shutil, "which", return_value="pdftotext"), mock.patch.object(
            d.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"Page two\f", b"")
        ) as run:
            content, _, _ = d.read_pdf(self.root / "example.pdf", "2")
        self.assertIn("## Stran 2", content)
        argv = run.call_args.args[0]
        first = argv.index("-f")
        self.assertEqual(argv[first:first + 4], ["-f", "2", "-l", "2"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

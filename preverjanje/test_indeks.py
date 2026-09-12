"""Synthetic data only. Model summaries below are fixtures, not live AI validation."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dokumenti/scripts"))
import indeks as m
import dokumenti as d


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "Skupni šumniki"
        self.root.mkdir()
        self.i = m.Index(self.base / "osebno")
        self.i.register("delo", self.root, cloud_approved=True, private_verified=True,
                        shared=True, shared_approved=True)

    def doc(self, name="sestanek.txt", text="Dogovor o delavnici: priprava ponudbe do petka. Cena 120 EUR."):
        path = self.root / name
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(text, encoding="utf-8")
        return path

    def complete(self, index=None):
        index = index or self.i
        batch = index.batch()
        answers = {"batch": batch["batch"], "summaries": [{"collection": x["collection"], "path": x["path"],
            "chunk": x["chunk"], "summary": "Testni povzetek: priprava ponudbe za delavnico, 120 EUR; preveri izvirnik."} for x in batch["items"]]}
        target = index.base / "odgovori.json"
        m.write(target, answers)
        return index.accept(target)

    def test_end_to_end_search_read_and_unchanged_reuse(self):
        path = self.doc()
        original = path.read_bytes()
        self.assertEqual(self.i.prepare(["delo"])["items"], 1)
        self.assertEqual(self.complete()["ready"], 1)
        self.assertEqual(self.i.prepare(["delo"])["items"], 0)
        matches = self.i.search(["delo"], "delavnico")['matches']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["source"], str(path))
        self.assertIn("120 EUR", self.i.read("delo", "sestanek.txt")["text"])
        self.assertEqual(path.read_bytes(), original)

    def test_second_computer_reuses_synced_packages_on_different_path(self):
        self.doc()
        self.i.prepare(["delo"])
        self.complete()
        other = self.base / "Druga lokalna pot"
        shutil.copytree(self.root, other)
        peer = m.Index(self.base / "drugi uporabnik")
        peer.register("delo", other, shared=True, cloud_approved=True, private_verified=True, shared_approved=True)
        with patch.object(d, "read_source", side_effect=AssertionError("Should reuse")):
            result = peer.prepare(["delo"])
        self.assertEqual(result["items"], 0)
        self.assertTrue(peer.search(["delo"], "ponudbe")["matches"])
        for file in (other / ".claude-index").rglob("*"):
            if file.is_file():
                self.assertNotIn(str(self.base), file.read_text(encoding="utf-8"))

    def test_same_time_peers_and_partial_package(self):
        self.doc()
        peer = m.Index(self.base / "peer")
        peer.register("delo", self.root, shared=True, cloud_approved=True, private_verified=True, shared_approved=True)
        self.i.prepare(["delo"])
        peer.prepare(["delo"])
        self.complete()
        self.complete(peer)
        manifests = list((self.root / ".claude-index/paketi").rglob("manifest.json"))
        self.assertEqual(len(manifests), 1)
        manifests[0].unlink()
        self.assertEqual(self.i.search(["delo"], "ponudbe")["matches"], [])

    def test_source_change_delete_exclusion_and_unavailable_root(self):
        path = self.doc()
        self.i.prepare(["delo"])
        self.complete()
        path.write_text("Spremenjena vsebina", encoding="utf-8")
        self.assertEqual(self.i.search(["delo"], "ponudbe")["matches"], [])
        path.unlink()
        self.assertEqual(self.i.rebuild()["ready"], 0)
        self.root.rename(self.base / "offline")
        result = self.i.rebuild()
        self.assertTrue(result["errors"])
        self.assertEqual(result["ready"], 0)

    def test_changed_source_rejects_pending_batch(self):
        path = self.doc()
        self.i.prepare(["delo"])
        path.write_text("Nova vsebina", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.i.batch()

    def test_daily_budget_cannot_be_bypassed_by_repeated_refresh(self):
        for i in range(12):
            self.doc(f"{i:02}.txt")
        self.assertEqual(self.i.prepare(["delo"])["items"], 10)
        self.assertEqual(self.i.prepare(["delo"])["items"], 10)  # Same outstanding batch.
        self.complete()
        self.assertEqual(self.i.prepare(["delo"])["items"], 0)
        self.assertEqual(m.load(self.i.base / "stanje.json")["pending"], 2)

    def test_large_document_resumes_and_is_not_searchable_until_complete(self):
        self.doc(text="Besedilo in vsebina. " * 15000)
        result = self.i.prepare(["delo"])
        self.assertEqual(result["items"], 20)
        self.assertEqual(self.complete()["ready"], 0)
        budget = m.load(self.i.base / "poraba.json")
        budget["day"] = "2020-01-01"
        m.write(self.i.base / "poraba.json", budget)
        self.assertGreater(self.i.prepare(["delo"])["items"], 0)
        self.assertEqual(self.complete()["ready"], 1)

    def test_exclusions_and_old_date_require_explicit_inclusion(self):
        self.doc("skrivno/a.txt")
        old = self.doc("staro.txt")
        os.utime(old, (1600000000, 1600000000))
        self.i.register("delo", self.root, exclusions=["skrivno"], cloud_approved=True,
                        private_verified=True, shared=True, shared_approved=True)
        self.assertEqual(self.i.prepare(["delo"])["items"], 0)
        with self.assertRaises(ValueError):
            self.i.read("delo", "staro.txt")
        with self.assertRaises(ValueError):
            self.i.source("delo", "skrivno/a.txt")
        self.i.config["collections"]["delo"]["include"].append("staro.txt")
        m.write(self.i.config_path, self.i.config)
        self.assertEqual(self.i.prepare(["delo"])["items"], 1)

    def test_scope_no_unapproved_or_overlapping_roots(self):
        with self.assertRaises(ValueError):
            self.i.scope(root=self.base)
        self.assertEqual(self.i.scope(root=self.root / "podmapa"), ["delo"])
        with self.assertRaises(ValueError):
            self.i.register("druga", self.root, cloud_approved=True, private_verified=True)
        with self.assertRaises(ValueError):
            self.i.register("nova", self.root, private_verified=True)

    def test_private_cache_when_shared_not_approved(self):
        root = self.base / "Zasebno"
        root.mkdir()
        i = m.Index(self.base / "private cache")
        i.register("zasebno", root, cloud_approved=True, private_verified=True)
        self.assertFalse((root / ".claude-index").exists())
        self.assertTrue((i.base / "lokalno/zasebno/zbirka.json").exists())

    def test_symlink_and_traversal_rejected(self):
        for rel in ("../outside", "/tmp/outside", "C:\\outside", "a\\b"):
            with self.assertRaises(ValueError):
                self.i.source("delo", rel)
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.i.source("delo", "link/a.txt")
        with self.assertRaises(ValueError):
            m.Index(self.root / "link/state")

    def test_corrupt_package_never_returned(self):
        self.doc()
        self.i.prepare(["delo"])
        self.complete()
        summary = next((self.root / ".claude-index").rglob("povzetek.md"))
        summary.write_text("tampered")
        self.assertFalse(self.i.search(["delo"], "ponudbe")["matches"])

    def test_invalid_model_response_does_not_publish(self):
        self.doc()
        self.i.prepare(["delo"])
        batch = self.i.batch()
        answer = self.i.base / "odgovori.json"
        m.write(answer, {"batch": batch["batch"], "summaries": []})
        with self.assertRaises(ValueError):
            self.i.accept(answer)
        self.assertFalse(list((self.root / ".claude-index").rglob("manifest.json")))

    def test_xlsx_cell_provenance_formula_and_source_preserved(self):
        from openpyxl import Workbook
        book = Workbook()
        sheet = book.active
        sheet.title = "Podatki"
        sheet.append(["Storitev", "Cena"])
        sheet.append(["Delavnica", 120])
        sheet["B3"] = "=SUM(B2:B2)"
        path = self.root / "cene.xlsx"
        book.save(path)
        original = path.read_bytes()
        result = d.read_source(self.root, "cene.xlsx", [])
        self.assertIn("Podatki!B2", result)
        self.assertIn('"formula": "=SUM(B2:B2)"', result)
        self.assertIn('"cached_value": null', result)
        self.assertEqual(original, path.read_bytes())

    def test_fts_input_is_not_sql_and_does_not_expand_scope(self):
        self.doc()
        self.i.prepare(["delo"])
        self.complete()
        self.i.search(["delo"], '\" OR 1=1; DROP TABLE docs; --')
        self.assertTrue(self.i.search(["delo"], "ponudbe")["matches"])

    def test_local_lock_does_not_allow_overlapping_mutations(self):
        with self.i.lock():
            with self.assertRaises(ValueError):
                with self.i.lock():
                    self.fail("A second writer acquired the lock")
        self.assertFalse((self.i.base / "izvajanje.lock").exists())

    def test_late_legacy_exclusion_still_applies(self):
        self.doc()
        self.i.prepare(["delo"])
        self.complete()
        d.save_catalogue(self.root, d.inventory(self.root, ["sestanek.txt"]))
        self.assertFalse(self.i.search(["delo"], "ponudbe")["matches"])
        with self.assertRaises(ValueError):
            self.i.read("delo", "sestanek.txt")


if __name__ == "__main__":
    unittest.main(verbosity=2)

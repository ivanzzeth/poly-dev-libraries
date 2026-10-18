"""Negative fixtures prove the catalog gate rejects inconsistent metadata."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(catalog, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.entry = dict(name="example", path="go/infrastructure/example", language="go", domain="infrastructure", kind="library", repository="https://github.com/example/example.git", module="github.com/example/example", license_file=None)
        self.write_manifest([self.entry])
        (self.root / ".gitmodules").write_text('[submodule "example"]\n path = go/infrastructure/example\n url = https://github.com/example/example.git\n')
        subprocess.run(["git", "update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",go/infrastructure/example"], cwd=self.root, check=True)

    def write_manifest(self, entries):
        (self.root / "libraries.json").write_text(json.dumps(dict(schema_version=1, libraries=entries)))

    def test_consistent_catalog_passes(self):
        self.assertEqual(catalog.validate(), [self.entry])

    def test_duplicate_catalog_entry_is_rejected(self):
        self.write_manifest([self.entry, self.entry])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            catalog.validate()

    def test_missing_gitlink_is_rejected(self):
        subprocess.run(["git", "update-index", "--force-remove", self.entry["path"]], cwd=self.root, check=True)
        with self.assertRaisesRegex(ValueError, "missing gitlink"):
            catalog.validate()

    def test_repository_mismatch_is_rejected(self):
        entry = copy.deepcopy(self.entry)
        entry["repository"] = "https://github.com/example/different.git"
        self.write_manifest([entry])
        with self.assertRaisesRegex(ValueError, "submodule mismatch"):
            catalog.validate()

    def test_path_traversal_is_rejected(self):
        entry = copy.deepcopy(self.entry)
        entry["path"] = "../go/example"
        self.write_manifest([entry])
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            catalog.validate()

    def test_implicit_branch_tracking_is_rejected(self):
        with (self.root / ".gitmodules").open("a") as stream:
            stream.write(" branch = main\n")
        with self.assertRaisesRegex(ValueError, "branch tracking"):
            catalog.validate()

    def test_uninitialized_checkout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "uninitialized"):
            catalog.validate(checkouts=True)


if __name__ == "__main__":
    unittest.main()

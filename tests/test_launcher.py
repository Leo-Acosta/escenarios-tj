import importlib.util
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from escenarios import launcher, server

spec = importlib.util.spec_from_file_location('release_manifest', Path(__file__).parents[1] / 'packaging/release_manifest.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class LauncherTests(unittest.TestCase):
    def test_data_directory_is_separate_from_application(self):
        with patch.dict(os.environ, {'LOCALAPPDATA': 'synthetic-user-local'}):
            self.assertEqual(launcher.default_data_dir(), Path('synthetic-user-local/EscenariosTJ'))

    def test_lock_rejects_second_instance_and_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            with launcher.instance_lock(directory):
                with self.assertRaises(RuntimeError):
                    with launcher.instance_lock(directory):
                        pass
            with launcher.instance_lock(directory):
                pass

    def test_occupied_port_does_not_create_or_migrate_database(self):
        with tempfile.TemporaryDirectory() as directory, socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            target = Path(directory) / 'untouched.sqlite3'
            with self.assertRaises(OSError):
                server.serve(target, listener.getsockname()[1])
            self.assertFalse(target.exists())

    def test_manifest_hashes_assets_and_rejects_user_databases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'EscenariosTJ.exe').write_bytes(b'synthetic-executable')
            assets = root / '_internal/frontend/dist'
            assets.mkdir(parents=True)
            (assets / 'index.html').write_text('synthetic interface')
            self.assertEqual(len(release.manifest(root)['files']), 2)
            (root / 'private.sqlite3').write_bytes(b'private')
            with self.assertRaises(ValueError):
                release.manifest(root)

    def test_scientific_package_data_allowed_but_private_databases_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'EscenariosTJ.exe').write_bytes(b'synthetic')
            assets=root/'_internal/frontend/dist';assets.mkdir(parents=True)
            (assets/'index.html').write_text('synthetic')
            package=root/'.tools/R-library/example/data';package.mkdir(parents=True)
            (package/'public.rda').write_bytes(b'package data')
            self.assertEqual(len(release.manifest(root)['files']),3)
            index=root/'.tools/R/doc';index.mkdir(parents=True)
            (index/'KEYWORDS.db').write_bytes(b'public R keyword index')
            self.assertEqual(len(release.manifest(root)['files']),4)
            (package/'private.db').write_bytes(b'private')
            with self.assertRaises(ValueError):release.manifest(root)


if __name__ == '__main__':
    unittest.main()

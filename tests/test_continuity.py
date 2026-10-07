from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from escenarios import continuity


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'original.sqlite3'
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('CREATE TABLE workflows (id TEXT PRIMARY KEY,updated_at TEXT,revision INTEGER,payload TEXT)')
            db.execute('INSERT INTO workflows VALUES (?,?,?,?)', ('synthetic', '2026-10-07', 1, json.dumps({'synthetic': True})))

    def test_migration_is_idempotent_and_preserves_rows(self):
        continuity.migrate(self.db)
        backups = list((self.root / 'migration-backups').glob('*.sqlite3'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(continuity.inspect(backups[0])['schema_version'], 0)
        with closing(sqlite3.connect(backups[0])) as saved:
            self.assertEqual(saved.execute('SELECT revision,payload FROM workflows').fetchone(),
                             (1, json.dumps({'synthetic': True})))
        before = self.db.read_bytes()
        continuity.migrate(self.db)
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(continuity.inspect(self.db)['schema_version'], 1)

    def test_frozen_analysis_reproduces_after_recovery(self):
        from escenarios import workflow
        try:
            from test_laboratories import prepare_case
        except ImportError:
            from tests.test_laboratories import prepare_case
        source = self.root / 'scenario.sqlite3'
        case = prepare_case(source)
        original = workflow.get_version(source, case['id'], 1)
        content, _ = continuity.snapshot(source)
        recovered, _ = continuity.recover(content, self.root / 'scenario-recovery')
        self.assertEqual(workflow.get_version(recovered, case['id'], 1), original)
        self.assertEqual(workflow.get_workflow(recovered, case['id']), workflow.get_workflow(source, case['id']))

    def test_backup_and_recovery_preserve_original_and_independent_records(self):
        before = self.db.read_bytes()
        content, metadata = continuity.snapshot(self.db)
        restored, info = continuity.recover(content, self.root / 'recovered')
        self.assertEqual(before, self.db.read_bytes())
        self.assertFalse(info['active_database_changed'])
        self.assertEqual(info['tables'], metadata['tables'])
        self.assertEqual(continuity.inspect(restored)['schema_version'], 1)
        with closing(sqlite3.connect(restored)) as db, db:
            self.assertEqual(json.loads(db.execute('SELECT payload FROM workflows').fetchone()[0]), {'synthetic': True})
        again, _ = continuity.recover(content, self.root / 'recovered')
        self.assertNotEqual(restored, again)

    def test_rejects_future_corrupt_and_unexpected_schema(self):
        for statement in ['PRAGMA user_version=99', 'CREATE TABLE extra (x TEXT)',
                          'CREATE TRIGGER unexpected AFTER INSERT ON workflows BEGIN DELETE FROM workflows; END',
                          "UPDATE workflows SET payload='broken'"]:
            content, _ = continuity.snapshot(self.db)
            bad = self.root / 'bad.sqlite3'
            bad.write_bytes(content)
            with closing(sqlite3.connect(bad)) as db, db:
                db.execute(statement)
            with self.assertRaises(ValueError):
                continuity.recover(bad.read_bytes(), self.root / 'rejected')
        with self.assertRaises(ValueError):
            continuity.recover(b'not a database', self.root / 'rejected')
        self.assertFalse(list((self.root / 'rejected').glob('recuperada-*')))

    def test_online_backup_includes_committed_wal(self):
        with closing(sqlite3.connect(self.db)) as live, live:
            live.execute('PRAGMA journal_mode=WAL')
            live.execute('UPDATE workflows SET revision=2')
            live.commit()
            content, _ = continuity.snapshot(self.db)
            restored, _ = continuity.recover(content, self.root / 'wal')
            with closing(sqlite3.connect(restored)) as db, db:
                self.assertEqual(db.execute('SELECT revision FROM workflows').fetchone()[0], 2)

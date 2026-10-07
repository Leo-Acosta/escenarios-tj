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
                          "UPDATE workflows SET payload='broken'", "UPDATE workflows SET payload='{\"x\":NaN}'"]:
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

    def test_all_frozen_laboratories_export_and_replay_after_restore_without_inference(self):
        from unittest.mock import patch
        from escenarios import executive, executive_pdf, graph, variables
        from test_executive import prepared
        source = self.root / 'complete.sqlite3'
        case, refs = prepared(source)  # Synthetic observations and mocked agent responses only.
        dictionary = variables.save(source, {'workflow_id': case['id'], 'version': 1, 'reviewed': True,
            'variables': [{'name': 'Contexto sintético', 'type': 'number', 'value': 12, 'unit': 'puntos',
                'target': 'context', 'source': 'Fixture sintético', 'uncertainty': 'No evidencia real',
                'interval': None, 'evidence': 'synthetic'}]})
        refs.append({'kind': 'variables', 'id': dictionary['id']})
        graph.save_version(source, {'workflow_id': case['id'], 'title': 'Red sintética',
            'assumptions': 'Vínculos hipotéticos', 'reviewed': True,
            'graph': {'nodes': [{'id': 0, 'name': 'Actor', 'type': 1}], 'edges': []}})
        report = executive.create(source, {'workflow_id': case['id'], 'version': 1, 'reviewed': True,
            'title': 'Informe de recuperación sintético', 'executive_note': 'Prueba funcional',
            'pending': 'Evidencia real pendiente', 'evidence_mode': 'synthetic',
            'sections': list(executive.LABELS), 'references': refs})
        content, metadata = continuity.snapshot(source)
        original_bytes = source.read_bytes()
        recovered, info = continuity.recover(content, self.root / 'complete-recovery')
        self.assertEqual(source.read_bytes(), original_bytes)
        self.assertEqual(metadata['tables'], info['tables'])
        with closing(sqlite3.connect(source)) as a, closing(sqlite3.connect(recovered)) as b:
            for name in metadata['tables']:
                self.assertEqual(sorted(a.execute('SELECT * FROM "'+name+'"').fetchall(), key=repr),
                                 sorted(b.execute('SELECT * FROM "'+name+'"').fetchall(), key=repr))
        with patch('escenarios.local_ai.request', side_effect=AssertionError('No new inference')):
            self.assertTrue(executive.replay(recovered, report['id'])['reproduced'])
            self.assertEqual(executive.read(recovered, report['id']), report)
            self.assertEqual(variables.read(recovered, dictionary['id']), dictionary)
            variables.verify(variables.read(recovered, dictionary['id']))
            self.assertEqual(executive_pdf.build_pdf(report),
                             executive_pdf.build_pdf(executive.read(recovered, report['id'])))

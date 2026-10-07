"""Consistent SQLite snapshots and non-destructive, versioned recovery."""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from uuid import uuid4

SCHEMA_VERSION = 1
MAX_BYTES = 20 * 1024 * 1024
COLUMNS = {
    'workflows': {'id', 'updated_at', 'revision', 'payload'},
    'workflow_versions': {'workflow_id', 'version', 'created_at', 'payload'},
    'snapshots': {'id', 'created_at', 'payload'}, 'cases': {'id', 'created_at', 'payload'},
    'graph': {'id', 'payload'}, 'graph_versions': {'id', 'payload'},
    'ai_config': {'id', 'payload'}, 'ai_jobs': {'id', 'workflow_id', 'payload'},
    'executive_reports': {'id', 'workflow_id', 'payload'},
    'variable_versions': {'id', 'workflow_id', 'payload'},
    'research_records': {'id', 'kind', 'payload'},
    'research_units': {'protocol', 'unit', 'partition'},
    **{name: {'id', 'payload'} for name in ('agent_runs', 'agent_comparisons',
       'decision_audits', 'decision_comparisons', 'decision_advice', 'decision_benchmarks',
       'payoff_sweeps', 'prediction_events', 'prediction_evaluations', 'sequential_versions')},
}


def inspect(path, require_data=False):
    path = Path(path)
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError('La base debe existir y no superar 20 MiB.')
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
            db.execute('PRAGMA trusted_schema=OFF')
            if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise ValueError('La base no supera la comprobación de integridad SQLite.')
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                raise ValueError('Versión de esquema no compatible.')
            tables = {}
            for kind, name in db.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"):
                if kind != 'table' or name not in COLUMNS:
                    raise ValueError('La copia contiene objetos de esquema no admitidos.')
                columns = {r[1] for r in db.execute(f'PRAGMA table_info("{name}")')}
                if columns != COLUMNS[name]:
                    raise ValueError('Estructura de tabla incompatible: ' + name)
                tables[name] = db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                if 'payload' in columns:
                    for (payload,) in db.execute(f'SELECT payload FROM "{name}"'):
                        if not isinstance(json.loads(payload), dict):
                            raise ValueError('Registro JSON incompatible.')
            if require_data and not tables:
                raise ValueError('La copia no contiene tablas de Escenarios TJ.')
            return {'schema_version': version, 'supported_version': SCHEMA_VERSION,
                    'tables': tables, 'integrity': 'ok',
                    'limits': ['La integridad estructural no acredita veracidad de evidencias ni coherencia semántica.']}
    except (sqlite3.Error, json.JSONDecodeError, TypeError) as error:
        raise ValueError('Archivo SQLite o contenido JSON inválido.') from error


def migrate(path, preserve_legacy=True):
    """Register the verified legacy schema; no analytical records are rewritten."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        info = inspect(path)
        if info['schema_version'] == SCHEMA_VERSION:
            return info
        if preserve_legacy:
            content, metadata = snapshot(path)
            directory = path.parent / 'migration-backups'
            directory.mkdir(parents=True, exist_ok=True)
            backup = directory / ('schema-0-' + str(uuid4()) + '.sqlite3')
            with backup.open('xb') as dest:
                dest.write(content)
            backup.with_suffix('.json').write_text(json.dumps(metadata), encoding='utf-8')
    with closing(sqlite3.connect(path)) as db, db:
        db.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
    return inspect(path)


def snapshot(path):
    inspect(path)
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / 'snapshot.sqlite3'
        with closing(sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)) as source:
            with closing(sqlite3.connect(target)) as dest:
                source.backup(dest)
        info = inspect(target)
        content = target.read_bytes()
        return content, {**info, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def recover(content, directory):
    if not isinstance(content, bytes) or not 0 < len(content) <= MAX_BYTES:
        raise ValueError('La copia no puede superar 20 MiB.')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # Validate and migrate privately before exposing a recovered database.
    with tempfile.TemporaryDirectory(dir=directory) as temporary:
        stage = Path(temporary) / 'candidate.sqlite3'
        stage.write_bytes(content)
        inspect(stage, require_data=True)
        migrate(stage, preserve_legacy=False)
        clean, info = snapshot(stage)
        target = directory / ('recuperada-' + str(uuid4()) + '.sqlite3')
        with target.open('xb') as output:
            output.write(clean)
        return target, {**info, 'file': target.name,
                        'active_database_changed': False,
                        'message': 'Copia recuperada por separado. La base activa permanece sin cambios.'}


def main():
    parser = argparse.ArgumentParser(description='Respaldo y recuperación segura de Escenarios TJ')
    parser.add_argument('action', choices=['inspect', 'backup', 'recover'])
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'inspect':
            result = inspect(args.source, require_data=True)
        elif args.action == 'backup':
            if not args.destination:
                raise ValueError('Indicá --destination para un archivo nuevo.')
            content, result = snapshot(args.source)
            with args.destination.open('xb') as dest:
                dest.write(content)
        else:
            if not args.destination:
                raise ValueError('Indicá --destination como directorio de recuperación.')
            _, result = recover(args.source.read_bytes(), args.destination)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()

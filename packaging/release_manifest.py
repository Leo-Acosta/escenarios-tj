"""Hash and validate the generated bundle; never collect workspace data."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path


def manifest(root):
    root = Path(root)
    files = {}
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == 'release-manifest.json':
            continue
        if path.is_symlink() or path.suffix.lower() in {'.sqlite', '.sqlite3', '.db'} or any(
                part.lower() in {'data', 'output', 'reference', '.git', '.env'} for part in path.relative_to(root).parts):
            raise ValueError('El paquete contiene un archivo no distribuible: ' + relative)
        files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not (root / 'EscenariosTJ.exe').is_file() or not (root / '_internal/frontend/dist/index.html').is_file():
        raise ValueError('Faltan ejecutable o interfaz compilada.')
    return {'product': 'Escenarios TJ', 'version': '0.1.0', 'platform': 'windows', 'files': files}


def build(root):
    root = Path(root).resolve()
    value = manifest(root)
    (root / 'release-manifest.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    archive = root.parent / 'EscenariosTJ-0.1.0-windows.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                bundle.write(path, 'EscenariosTJ/' + path.relative_to(root).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    print(archive)
    return value


if __name__ == '__main__':
    build(sys.argv[1])

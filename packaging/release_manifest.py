"""Hash and validate the generated bundle; never collect workspace data."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

def file_digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def manifest(root):
    root = Path(root)
    files = {}
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == 'release-manifest.json':
            continue
        parts = path.relative_to(root).parts
        scientific = len(parts)>2 and parts[0]=='.tools' and parts[1] in {'R','R-library','keras-python'}
        public_r_index = relative in {'.tools/R/doc/KEYWORDS.db','.tools/R/share/licenses/license.db'}
        if path.is_symlink() or (path.suffix.lower() in {'.sqlite', '.sqlite3', '.db'} and not public_r_index) or any(
                part.lower() in {'.git', '.env'} or (not scientific and part.lower() in {'data','output','reference'}) for part in parts):
            raise ValueError('El paquete contiene un archivo no distribuible: ' + relative)
        files[relative] = file_digest(path)
    if not (root / 'EscenariosTJ.exe').is_file() or not (root / '_internal/frontend/dist/index.html').is_file():
        raise ValueError('Faltan ejecutable o interfaz compilada.')
    return {'product': 'Escenarios TJ', 'version': '0.1.0', 'platform': 'windows', 'files': files}


def build(root, archive_enabled=True):
    root = Path(root).resolve()
    value = manifest(root)
    (root / 'release-manifest.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    if not archive_enabled:
        print('Manifiesto verificado: '+str(len(value['files']))+' archivos.')
        return value
    archive = root.parent / 'EscenariosTJ-0.1.0-windows.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                bundle.write(path, 'EscenariosTJ/' + path.relative_to(root).as_posix())
    digest = file_digest(archive)
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    print(archive)
    return value


if __name__ == '__main__':
    build(sys.argv[1], '--manifest-only' not in sys.argv)

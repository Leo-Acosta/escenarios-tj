"""Bundle installed, licensed scientific runtimes only; never workspace case data."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def bundle(destination):
    if sys.version_info[:2] != (3,12):
        raise ValueError('La distribución científica actual requiere Python 3.12 para coincidir con sus bibliotecas CPU.')
    destination = Path(destination).resolve()
    if destination != ROOT / 'release/EscenariosTJ':
        raise ValueError('Use la carpeta de distribución declarada.')
    tools = destination / '.tools'
    tools.mkdir(exist_ok=True)
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    for name in ('R', 'R-library'):
        source = ROOT / '.tools' / name
        if not source.is_dir(): raise ValueError('Falta ' + name)
        shutil.copytree(source, tools / name, ignore=ignore, dirs_exist_ok=True)
    # A venv cannot be relocated: include a standalone interpreter and its stdlib.
    base = Path(sys.base_prefix)
    python = tools / 'keras-python'
    python.mkdir(exist_ok=True)
    for source in base.iterdir():
        if source.is_file() and (source.suffix in ('.exe', '.dll') or source.name == 'LICENSE.txt'):
            shutil.copy2(source, python / source.name)
    shutil.copytree(base / 'DLLs', python / 'DLLs', ignore=ignore, dirs_exist_ok=True)
    shutil.copytree(base / 'Lib', python / 'Lib',
        ignore=shutil.ignore_patterns('site-packages', '__pycache__', '*.pyc', 'test', 'tests'), dirs_exist_ok=True)
    # C++ extension development headers are unnecessary for CPU inference and
    # include paths longer than Windows installers can safely rename.
    headers=python / 'Lib/site-packages/torch/include'
    if headers.is_dir():
        if not headers.resolve().is_relative_to(destination):raise ValueError('Destino fuera del paquete.')
        shutil.rmtree(headers)
    def runtime_ignore(folder,names):
        omitted=list(ignore(folder,names))
        if Path(folder).name=='torch' and 'include' in names:omitted.append('include')
        return omitted
    shutil.copytree(ROOT / '.tools/keras-python/Lib/site-packages', python / 'Lib/site-packages',
        ignore=runtime_ignore, dirs_exist_ok=True)
    # Disable user-site packages and external PYTHONPATH, while loading own stdlib.
    (python / 'python312._pth').write_text('Lib\nDLLs\nLib/site-packages\n.\nimport site\n', encoding='ascii')
    record = {'runtime': 'R + paquetes CRAN + Python/Keras/PyTorch CPU',
        'private_data_included': False, 'offline_after_install': True,
        'licenses': 'Licencias originales conservadas en R/doc y metadatos de cada paquete.',
        'limits': 'Sin firma digital; Windows x64. Sin cabeceras C++ para compilar extensiones PyTorch. Ollama/modelos LLM no incluidos.'}
    (destination / 'ENTORNO-CIENTIFICO.json').write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))

if __name__ == '__main__': bundle(sys.argv[1])

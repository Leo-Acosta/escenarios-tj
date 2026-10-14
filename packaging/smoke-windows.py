"""Exercise the built executable in a synthetic folder with no Python on PATH."""
import json
import base64
import io
import zipfile
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from escenarios import executive, dossier
from tests.test_executive import prepared


def run(executable, directory):
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / 'escenarios.sqlite3'
    case, refs = prepared(database)
    report = executive.create(database, {'workflow_id': case['id'], 'version': 1,
        'title': 'Distribución · prueba sintética', 'sections': ['matrix', 'tree', 'agents'],
        'sources': refs[:2], 'evidence_mode': 'synthetic', 'reviewed': True})
    from reportlab.pdfgen import canvas
    stream=io.BytesIO(); page=canvas.Canvas(stream); page.drawString(50,700,'Prueba documental sintetica'); page.save()
    original=stream.getvalue()+b' '*(3*1024*1024)
    document=dossier.save(database,{'workflow_id':case['id'],'kind':'document','name':'sintetico.pdf',
        'content':base64.b64encode(original).decode(),'note':'Datos sinteticos, no caso real'})
    frozen=dossier.save(database,{'workflow_id':case['id'],'kind':'snapshot','title':'Prueba documental sintetica','reviewed':True})
    environment = {**os.environ, 'PATH': ''}
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    command = [str(executable), '--no-browser', '--port', str(port), '--data-dir', str(directory)]

    def cycle():
        with (directory / 'server.log').open('ab') as log:
            process = subprocess.Popen(command, cwd=directory, env=environment, stdout=log, stderr=log)
            try:
                base = f'http://127.0.0.1:{port}'
                deadline = time.monotonic() + 30
                while True:
                    if process.poll() is not None:
                        raise RuntimeError('El ejecutable terminó antes de iniciar. Consultar server.log.')
                    try:
                        with urlopen(base + '/api/continuity/status', timeout=1) as response:
                            assert response.status == 200
                        break
                    except (URLError, TimeoutError):
                        if time.monotonic() > deadline:
                            raise RuntimeError('El ejecutable no inició en 30 segundos.')
                        time.sleep(.1)
                for endpoint in ['/app/', '/', '/api/workflows', '/api/executive/replay?id=' + report['id']]:
                    with urlopen(base + endpoint, timeout=5) as response:
                        assert response.status == 200
                with urlopen(base+'/api/dossier/export?id='+frozen['id'],timeout=10) as response:
                    assert json.load(response)==frozen
                with urlopen(base+'/api/dossier/file?id='+document['id'],timeout=10) as response:
                    assert response.read()==original
                with urlopen(base+'/api/dossier/zip?id='+frozen['id'],timeout=15) as response:
                    with zipfile.ZipFile(io.BytesIO(response.read())) as archive:
                        assert json.loads(archive.read('registro.json'))==frozen
                with urlopen(base + '/api/executive/pdf?id=' + report['id'], timeout=10) as response:
                    pdf = response.read()
                    assert pdf.startswith(b'%PDF')
                duplicate = subprocess.run(command, env=environment, cwd=directory, capture_output=True, timeout=10)
                assert duplicate.returncode == 1 and b'instancia' in duplicate.stderr
                return pdf
            finally:
                process.terminate()
                process.wait(timeout=10)

    first = cycle()
    second = cycle()
    assert first == second, 'La reproducción cambió después de reiniciar.'
    result = {'synthetic': True, 'python_on_path': False, 'cycles': 2,
              'duplicate_rejected': True, 'frozen_pdf_identical': True, 'pdf_bytes': len(first),
              'documentary_export_identical':True,'large_original_identical':True,'documentary_zip_verified':True}
    (directory / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())

"""Install/reinstall/uninstall a QA build in a fresh, explicit test directory."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import socket
import time
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path


def verify_files(app):
    manifest = json.loads((app / 'release-manifest.json').read_text(encoding='utf-8'))
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((app / name).read_bytes()).hexdigest() == digest, name
    return len(manifest['files'])


def run(setup, root):
    if '-QA-Setup.exe' not in setup.name:
        raise ValueError('La prueba requiere un instalador QA con AppId separado.')
    root.mkdir(parents=True, exist_ok=False)
    app = root / 'programa'
    args = [str(setup), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOICONS',
            '/NOCLOSEAPPLICATIONS', '/DIR=' + str(app), '/LOG=' + str(root / 'install.log')]
    subprocess.run(args, check=True, timeout=120)
    count = verify_files(app)
    spec = importlib.util.spec_from_file_location('smoke_windows', Path(__file__).with_name('smoke-windows.py'))
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    smoke.run(app / 'EscenariosTJ.exe', root / 'datos-sinteticos')
    database = root / 'datos-sinteticos/escenarios.sqlite3'
    original = hashlib.sha256(database.read_bytes()).hexdigest()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    with (root / 'running-update.log').open('ab') as log:
        process = subprocess.Popen([str(app / 'EscenariosTJ.exe'), '--no-browser', '--port', str(port),
            '--data-dir', str(database.parent)], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while True:
                try:
                    with urlopen(f'http://127.0.0.1:{port}/api/continuity/status', timeout=1):
                        break
                except (URLError, TimeoutError):
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('No inició la prueba de actualización en uso.')
                    time.sleep(.1)
            blocked = subprocess.run(args, timeout=60)
            assert blocked.returncode != 0, 'No se rechazó actualizar la aplicación abierta.'
            assert process.poll() is None, 'El instalador cerró la aplicación.'
            assert verify_files(app) == count
        finally:
            process.terminate()
            process.wait(timeout=10)
    subprocess.run(args, check=True, timeout=120)
    assert verify_files(app) == count
    assert hashlib.sha256(database.read_bytes()).hexdigest() == original
    uninstaller = app / 'unins000.exe'
    assert uninstaller.resolve().parent == app.resolve() and app.resolve().is_relative_to(root.resolve())
    subprocess.run([str(uninstaller), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'], check=True, timeout=120)
    assert not (app / 'EscenariosTJ.exe').exists()
    assert hashlib.sha256(database.read_bytes()).hexdigest() == original
    result = {'synthetic': True, 'installed_files_verified': count, 'installed_exe_tested': True,
              'running_update_rejected': True, 'reinstallation_kept_data': True, 'uninstall_kept_data': True}
    (root / 'installer-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())

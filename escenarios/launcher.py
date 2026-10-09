"""Windows distribution entry point; application files never contain user data."""
import argparse
import os
from contextlib import contextmanager
from pathlib import Path
from . import server

VERSION = '0.1.0'


def default_data_dir():
    base = os.environ.get('LOCALAPPDATA')
    return (Path(base) if base else Path.home() / '.local' / 'share') / 'EscenariosTJ'


@contextmanager
def instance_lock(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / '.instance.lock').open('a+b') as handle:
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('Ya hay una instancia usando esta carpeta de datos.') from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Escenarios TJ · aplicación local')
    parser.add_argument('--version', action='version', version='Escenarios TJ ' + VERSION)
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--data-dir', type=Path, default=default_data_dir())
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('El puerto debe estar entre 1 y 65535.')
    try:
        with instance_lock(args.data_dir):
            server.serve(args.data_dir.resolve() / 'escenarios.sqlite3', args.port,
                         open_browser=not args.no_browser)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, 'No se pudo iniciar Escenarios TJ: ' + str(error) + '\n')


if __name__ == '__main__':
    main()

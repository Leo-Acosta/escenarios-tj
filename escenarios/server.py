"""Servidor local. La UI nunca calcula pagos: consulta el núcleo Python."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .core import Parameters, analyze
from .storage import save_snapshot, list_snapshots
from .graph import save_graph, load_graph
from .intake import prepare
from .case_model import analyze_case,save_case,list_cases

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'escenarios.sqlite3'


class Handler(BaseHTTPRequestHandler):
    def send(self, status, content, mime='application/json; charset=utf-8'):
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False, allow_nan=False)
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def allowed(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {'error': 'Host no autorizado.'})
        url = urlsplit(self.path)
        if url.path == '/api/cases':
            return self.send(200, list_cases(DB))
        if url.path == '/api/graph':
            return self.send(200, {'graph': load_graph(DB)})
        if url.path in ('/api/analysis', '/api/report.pdf'):
            try:
                args = parse_qs(url.query)
                p = Parameters(float(args.get('q', ['0.6'])[0]), float(args.get('cost', ['3'])[0]))
                result = analyze(p)
                if url.path == '/api/report.pdf':
                    try:
                        from .report import build_pdf
                    except ImportError:
                        return self.send(503, {'error': 'Instalá reportlab para exportar PDF, o usá la impresión del navegador.'})
                    return self.send(200, build_pdf(result), 'application/pdf')
                return self.send(200, result)
            except (ValueError, TypeError):
                return self.send(400, {'error': 'Parámetros inválidos.'})
        if url.path == '/api/history':
            return self.send(200, list_snapshots(DB))
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.css': ('app.css', 'text/css; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/graphs.js': ('graphs.js', 'text/javascript; charset=utf-8'),
                 '/network.js': ('network.js', 'text/javascript; charset=utf-8'),
                 '/intake.js': ('intake.js', 'text/javascript; charset=utf-8'),
                 '/case.js': ('case.js', 'text/javascript; charset=utf-8'),
                 '/case-visuals.js': ('case-visuals.js', 'text/javascript; charset=utf-8'),
                 '/sensitivity.js': ('sensitivity.js', 'text/javascript; charset=utf-8')}
        if url.path in files:
            name, mime = files[url.path]
            return self.send(200, (ROOT / 'web' / name).read_bytes(), mime)
        return self.send(404, {'error': 'Recurso inexistente.'})

    def do_POST(self):
        if not self.allowed() or self.headers.get('Origin') not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            return self.send(403, {'error': 'Origen no autorizado.'})
        if self.path not in ('/api/snapshots','/api/graph','/api/intake','/api/cases'):
            return self.send(404, {'error': 'Recurso inexistente.'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= (100000 if self.path in ('/api/graph','/api/intake','/api/cases') else 2048):
                raise ValueError()
            payload = json.loads(self.rfile.read(length))
            if self.path == '/api/cases':
                case=analyze_case(payload)
                if payload.get('save') is True:case['id']=save_case(DB,case)
                return self.send(200,case)
            if self.path == '/api/intake':
                try:
                    return self.send(200, prepare(payload['prompt']))
                except ValueError:
                    return self.send(400, {'error':'Revisá la descripción o la respuesta del modelo.'})
                except Exception:
                    return self.send(502, {'error':'No se pudo obtener el borrador. Revisá la conexión y configuración del modelo.'})
            if self.path == '/api/graph':
                return self.send(200, {'graph':save_graph(DB,payload)})
            result = analyze(Parameters(float(payload['cooperation']), float(payload['cost'])))
            return self.send(201, {'id': save_snapshot(DB, result)})
        except (ValueError, KeyError, TypeError):
            return self.send(400, {'error': 'Datos inválidos.'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Escenarios TJ: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

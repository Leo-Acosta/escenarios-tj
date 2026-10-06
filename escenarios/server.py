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
from .workflow import operate,get_workflow,list_workflows,get_version,Conflict,NotFound
from . import local_ai,ai_jobs,sequential,simulation,agents,comparisons

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
        if url.path == '/api/sequential/report.pdf':
            try:
                identity=parse_qs(url.query)['id'][0]
                record=sequential.get_version(DB,identity)
            except (KeyError,IndexError):return self.send(404,{'error':'Versión guardada no encontrada.'})
            try:
                from .sequential_report import build_pdf
            except ImportError:return self.send(503,{'error':'ReportLab no está disponible. Usá la impresión del navegador.'})
            return self.send(200,build_pdf(record),'application/pdf')
        if url.path in ('/api/agents/report.pdf','/api/agents/rounds.csv'):
            try:record=agents.get_run(DB,parse_qs(url.query)['id'][0])
            except (KeyError,IndexError):return self.send(404,{'error':'Corrida guardada no encontrada.'})
            if url.path.endswith('.csv'):return self.send(200,agents.build_csv(record),'text/csv; charset=utf-8')
            try:
                from .agent_report import build_pdf
            except ImportError:return self.send(503,{'error':'ReportLab no está disponible para exportar PDF.'})
            return self.send(200,build_pdf(record),'application/pdf')
        if url.path == '/api/agent-comparisons':
            return self.send(200,comparisons.history(DB))
        if url.path == '/api/agents':
            return self.send(200,agents.history(DB))
        if url.path == '/api/sequential':
            return self.send(200,sequential.history(DB))
        if url.path == '/api/ai/status':
            return self.send(200,local_ai.status(DB))
        if url.path == '/api/ai/jobs':
            try:
                args=parse_qs(url.query)
                if 'job' in args:return self.send(200,ai_jobs.get_job(DB,args['job'][0]))
                if 'workflow' in args:return self.send(200,ai_jobs.list_jobs(DB,args['workflow'][0]))
                raise ValueError()
            except NotFound as error:
                return self.send(404,{'error':str(error)})
            except (ValueError,TypeError):
                return self.send(400,{'error':'Referencia de propuesta inválida.'})
        if url.path == '/api/workflows':
            try:
                args=parse_qs(url.query)
                if 'id' not in args:return self.send(200,list_workflows(DB))
                if 'version' in args:return self.send(200,get_version(DB,args['id'][0],args['version'][0]))
                return self.send(200,get_workflow(DB,args['id'][0]))
            except NotFound as error:
                return self.send(404,{'error':str(error)})
            except (ValueError,TypeError):
                return self.send(400,{'error':'Referencia de expediente inválida.'})
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
        files['/workflow.js']=('workflow.js','text/javascript; charset=utf-8')
        files['/sequential-ai.js']=('sequential-ai.js','text/javascript; charset=utf-8')
        files['/comparisons.js']=('comparisons.js','text/javascript; charset=utf-8')
        files['/agents.js']=('agents.js','text/javascript; charset=utf-8')
        files['/sequential.js']=('sequential.js','text/javascript; charset=utf-8')
        files['/ai.js']=('ai.js','text/javascript; charset=utf-8')
        if url.path in files:
            name, mime = files[url.path]
            return self.send(200, (ROOT / 'web' / name).read_bytes(), mime)
        return self.send(404, {'error': 'Recurso inexistente.'})

    def do_POST(self):
        if not self.allowed() or self.headers.get('Origin') not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            return self.send(403, {'error': 'Origen no autorizado.'})
        if self.path not in ('/api/snapshots','/api/graph','/api/intake','/api/cases','/api/workflows','/api/ai/config','/api/ai/jobs','/api/sequential','/api/sequential/ai-jobs','/api/sequential/ai-apply','/api/agents','/api/agent-comparisons','/api/agent-comparisons/replay'):
            return self.send(404, {'error': 'Recurso inexistente.'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= (100000 if self.path in ('/api/graph','/api/intake','/api/cases','/api/workflows','/api/ai/config','/api/ai/jobs','/api/sequential','/api/sequential/ai-jobs','/api/sequential/ai-apply','/api/agents','/api/agent-comparisons','/api/agent-comparisons/replay') else 2048):
                raise ValueError()
            payload = json.loads(self.rfile.read(length))
            if self.path == '/api/agent-comparisons/replay':
                try:return self.send(200,comparisons.replay(DB,payload))
                except KeyError:return self.send(404,{'error':'Comparación no encontrada.'})
            if self.path == '/api/agent-comparisons':
                if payload.get('save') is True and payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión para guardar.')
                result=comparisons.compare(payload)
                if payload.get('save') is True:result=comparisons.save(DB,result)
                return self.send(200,result)
            if self.path == '/api/agents':
                result=agents.run(payload)
                if payload.get('save') is True:
                    if payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión para guardar.')
                    result=agents.save(DB,result)
                return self.send(200,result)
            if self.path in ('/api/sequential/ai-jobs','/api/sequential/ai-apply'):
                try:
                    if self.path.endswith('ai-jobs'):return self.send(202,ai_jobs.start_tree(DB,payload))
                    return self.send(200,ai_jobs.apply_tree(DB,payload))
                except Conflict as error:return self.send(409,{'error':str(error)})
                except NotFound as error:return self.send(404,{'error':str(error)})
            if self.path == '/api/sequential':
                result=sequential.analyze(payload)
                if payload.get('ai_job_id'):result['ai_proposal']=ai_jobs.tree_provenance(DB,payload['ai_job_id'])
                if payload.get('simulation') is not None:result['simulation']=simulation.simulate(result['model'],payload['simulation'])
                if payload.get('save') is True:
                    if payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión antes de guardar.')
                    result=sequential.save(DB,result)
                return self.send(200,result)
            if self.path in ('/api/ai/config','/api/ai/jobs'):
                try:
                    if self.path=='/api/ai/config':return self.send(200,local_ai.save_config(DB,payload))
                    return self.send(202,ai_jobs.start(DB,payload))
                except Conflict as error:
                    return self.send(409,{'error':str(error)})
                except NotFound as error:
                    return self.send(404,{'error':str(error)})
                except (ValueError,TypeError,KeyError) as error:
                    return self.send(400,{'error':str(error) if isinstance(error,ValueError) else 'Solicitud de IA inválida.'})
            if self.path == '/api/workflows':
                try:
                    return self.send(200,operate(DB,payload))
                except Conflict as error:
                    return self.send(409,{'error':str(error)})
                except NotFound as error:
                    return self.send(404,{'error':str(error)})
                except (ValueError,KeyError,TypeError) as error:
                    return self.send(400,{'error':str(error) if isinstance(error,ValueError) else 'Datos de expediente inválidos.'})
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
    ai_jobs.recover_interrupted(DB)
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

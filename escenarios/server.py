"""Servidor local. La UI nunca calcula pagos: consulta el núcleo Python."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .core import Parameters, analyze
from .storage import save_snapshot, list_snapshots
from .graph import save_graph, load_graph, save_version as save_graph_version, version_history as graph_history
from .intake import prepare
from .case_model import analyze_case,save_case,list_cases
from .workflow import operate,get_workflow,list_workflows,get_version,Conflict,NotFound
from . import local_ai,ai_jobs,sequential,simulation,agents,comparisons,payoff_sweep,library,version_diff
from . import laboratories,research,decision_agents,executive

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
        if url.path.startswith('/api/executive'):
            try:
                args=parse_qs(url.query);identity=args.get('id',[''])[0]
                if url.path=='/api/executive/catalog':return self.send(200,executive.catalog(DB,args.get('workflow_id',[''])[0],int(args.get('version',['0'])[0])))
                if url.path=='/api/executive/history':return self.send(200,executive.history(DB,args.get('workflow_id',[''])[0]))
                if url.path=='/api/executive/replay':return self.send(200,executive.replay(DB,identity))
                record=executive.read(DB,identity)
                if url.path=='/api/executive/export':return self.send(200,record)
                if url.path=='/api/executive/html':
                    from .executive_view import html
                    return self.send(200,html(record),'text/html; charset=utf-8')
                if url.path=='/api/executive/pdf':
                    try:from .executive_pdf import build_pdf
                    except ImportError:return self.send(503,{'error':'ReportLab no disponible. Usá la vista HTML A4 para imprimir.'})
                    return self.send(200,build_pdf(record),'application/pdf')
                if url.path=='/api/executive':return self.send(200,record)
                return self.send(404,{'error':'Ruta de informe desconocida.'})
            except NotFound as error:return self.send(404,{'error':str(error)})
            except (ValueError,KeyError,TypeError) as error:return self.send(400,{'error':str(error)})
        if url.path == '/api/laboratories':
            args=parse_qs(url.query)
            try:return self.send(200,laboratories.history(DB,args.get('kind',[''])[0],args.get('workflow_id',[''])[0]))
            except NotFound as error:return self.send(404,{'error':str(error)})
            except ValueError as error:return self.send(400,{'error':str(error)})
        if url.path == '/app':
            self.send_response(302)
            self.send_header('Location', '/app/')
            self.end_headers()
            return
        if url.path.startswith('/app/'):
            # Resolve and check containment before serving any compiled asset.
            dist = (ROOT / 'frontend' / 'dist').resolve()
            relative = url.path[len('/app/'):] or 'index.html'
            target = (dist / relative).resolve()
            if not target.is_relative_to(dist) or not target.is_file():
                return self.send(404, {'error': 'Interfaz o recurso no disponible. Ejecutá npm ci y npm run build en frontend.'})
            mime = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
            if target.suffix == '.js': mime = 'text/javascript'
            return self.send(200, target.read_bytes(), mime)
        if url.path in ('/api/library','/api/library/item'):
            args=parse_qs(url.query)
            try:
                if url.path.endswith('/item'):return self.send(200,library.get_record(DB,args['type'][0],args['id'][0]))
                return self.send(200,library.search(DB,args.get('q',[''])[0],args.get('type',[''])[0],int(args.get('offset',['0'])[0])))
            except (KeyError,IndexError):return self.send(404,{'error':'Versión no encontrada.'})
            except ValueError:return self.send(400,{'error':'Consulta de biblioteca inválida.'})
        if url.path == '/api/payoff-sweep':
            return self.send(200,payoff_sweep.history(DB))
        if url.path in ('/api/payoff-sweep/scenarios.csv','/api/payoff-sweep/report.pdf'):
            try:record=payoff_sweep.get_record(DB,parse_qs(url.query)['id'][0])
            except (KeyError,IndexError):return self.send(404,{'error':'Exploración guardada no encontrada.'})
            if url.path.endswith('.csv'):return self.send(200,payoff_sweep.build_csv(record),'text/csv; charset=utf-8')
            try:
                from .sweep_report import build_pdf
            except ImportError:return self.send(503,{'error':'ReportLab no está disponible para exportar PDF.'})
            return self.send(200,build_pdf(record),'application/pdf')
        if url.path == '/api/agent-comparisons/report.pdf':
            try:record=comparisons.get_record(DB,parse_qs(url.query)['id'][0])
            except (KeyError,IndexError):return self.send(404,{'error':'Comparación guardada no encontrada.'})
            try:
                from .comparison_report import build_pdf
            except ImportError:return self.send(503,{'error':'ReportLab no está disponible para exportar PDF.'})
            return self.send(200,build_pdf(record),'application/pdf')
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
            identity=parse_qs(url.query).get('workflow_id',[''])[0]
            if identity:
                try:get_workflow(DB,identity)
                except NotFound as error:return self.send(404,{'error':str(error)})
                except ValueError as error:return self.send(400,{'error':str(error)})
            return self.send(200,sequential.history(DB,identity))
        if url.path == '/api/predictions/replay':
            from . import prediction_eval
            try:return self.send(200,prediction_eval.replay(DB,parse_qs(url.query).get('id',[''])[0]))
            except ValueError as error:return self.send(400,{'error':str(error)})
        if url.path == '/api/predictions':
            from . import prediction_eval
            return self.send(200,{'events':prediction_eval.history(DB),'evaluations':prediction_eval.evaluations(DB)})
        if url.path in ('/api/ai/decision-replay','/api/ai/decision-export'):
            identity=parse_qs(url.query).get('id',[''])[0]
            try:return self.send(200,(decision_agents.replay(DB,identity) if url.path.endswith('replay') else decision_agents.get_record(DB,identity)))
            except (ValueError,KeyError,TypeError) as error:return self.send(400,{'error':str(error)})
        if url.path == '/api/ai/status':
            return self.send(200,local_ai.status(DB))
        if url.path in ('/api/research','/api/research/export','/api/research/replay','/api/research/report','/api/ai/benchmark-export','/api/ai/benchmark-replay'):
            try:
                identity=parse_qs(url.query).get('id',[None])[0]
                if url.path=='/api/research':return self.send(200,research.dashboard(DB,identity))
                if url.path=='/api/research/export':return self.send(200,research.export(DB,identity))
                if url.path=='/api/research/replay':return self.send(200,research.replay(DB,identity))
                if url.path=='/api/research/report':return self.send(200,research.report(DB,identity),'text/html; charset=utf-8')
                return self.send(200,decision_agents.benchmark_record(DB,identity,url.path.endswith('replay')))
            except (ValueError,KeyError,TypeError) as error:return self.send(400,{'error':str(error)})
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
        if url.path == '/api/workflows/report.pdf':
            try:
                args=parse_qs(url.query)
                record=get_version(DB,args.get('id',[''])[0],args.get('version',[''])[0])
            except NotFound as error:return self.send(404,{'error':str(error)})
            except (ValueError,TypeError):return self.send(400,{'error':'Referencia de versión inválida.'})
            try:
                from .workflow_report import build_pdf
            except ImportError:return self.send(503,{'error':'ReportLab no está disponible para exportar PDF.'})
            return self.send(200,build_pdf(record),'application/pdf')
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
        if url.path == '/api/graph/versions':
            try:return self.send(200,graph_history(DB,parse_qs(url.query).get('workflow_id',[''])[0]))
            except NotFound as error:return self.send(404,{'error':str(error)})
            except ValueError as error:return self.send(400,{'error':str(error)})
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
        files['/payoff-sweep.js']=('payoff-sweep.js','text/javascript; charset=utf-8')
        files['/library.js']=('library.js','text/javascript; charset=utf-8')
        files['/version-diff.js']=('version-diff.js','text/javascript; charset=utf-8')
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
        if self.path not in ('/api/executive','/api/graph/versions','/api/laboratories','/api/snapshots','/api/graph','/api/intake','/api/cases','/api/workflows','/api/ai/reviews','/api/research','/api/ai/benchmark-jobs','/api/ai/research-advisor','/api/ai/decision-jobs','/api/ai/decision-optimizer','/api/predictions/forecast','/api/predictions/observe','/api/predictions/evaluate','/api/ai/config','/api/ai/jobs','/api/sequential','/api/sequential/ai-jobs','/api/sequential/ai-apply','/api/agents','/api/library/compare','/api/payoff-sweep','/api/agent-comparisons','/api/agent-comparisons/replay'):
            return self.send(404, {'error': 'Recurso inexistente.'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= (100000 if self.path in ('/api/executive','/api/graph/versions','/api/laboratories','/api/graph','/api/intake','/api/cases','/api/workflows','/api/ai/reviews','/api/research','/api/ai/benchmark-jobs','/api/ai/research-advisor','/api/ai/decision-jobs','/api/ai/decision-optimizer','/api/predictions/forecast','/api/predictions/observe','/api/predictions/evaluate','/api/ai/config','/api/ai/jobs','/api/sequential','/api/sequential/ai-jobs','/api/sequential/ai-apply','/api/agents','/api/library/compare','/api/payoff-sweep','/api/agent-comparisons','/api/agent-comparisons/replay') else 2048):
                raise ValueError()
            payload = json.loads(self.rfile.read(length))
            if self.path=='/api/executive':
                try:return self.send(201,executive.create(DB,payload))
                except NotFound as error:return self.send(404,{'error':str(error)})
                except (ValueError,KeyError,TypeError,AttributeError) as error:return self.send(400,{'error':str(error)})
            if self.path.startswith('/api/predictions/'):
                from . import prediction_eval
                action={'forecast':prediction_eval.forecast,'observe':prediction_eval.observe,'evaluate':prediction_eval.evaluate}[self.path.rsplit('/',1)[1]]
                try:return self.send(200,action(DB,payload))
                except ValueError as error:return self.send(400,{'error':str(error)})
            if self.path in ('/api/ai/decision-jobs','/api/ai/decision-optimizer'):
                try:return self.send(202,(ai_jobs.start_decision(DB,payload) if self.path.endswith('jobs') else ai_jobs.start_decision_optimizer(DB,payload)))
                except Conflict as error:return self.send(409,{'error':str(error)})
                except NotFound as error:return self.send(404,{'error':str(error)})
                except (ValueError,KeyError,TypeError) as error:return self.send(400,{'error':str(error)})
            if self.path in ('/api/research','/api/ai/benchmark-jobs','/api/ai/research-advisor'):
                try:
                    if self.path=='/api/ai/benchmark-jobs':return self.send(202,ai_jobs.start_benchmark(DB,payload))
                    if self.path=='/api/ai/research-advisor':return self.send(202,ai_jobs.start_research_advisor(DB,payload))
                    actions={'protocol':research.protocol,'candidate':research.candidate,'forecast':research.forecast,'observe':research.observe,
                        'evaluate':research.evaluate,'select':research.select,'calibrate':research.calibrate,'accept_advice':research.accept_advice}
                    if not isinstance(payload,dict) or payload.get('action') not in actions:raise ValueError('Acción de investigación inválida.')
                    return self.send(201,actions[payload['action']](DB,payload))
                except Conflict as error:return self.send(409,{'error':str(error)})
                except NotFound as error:return self.send(404,{'error':str(error)})
                except (ValueError,KeyError,TypeError,AttributeError) as error:return self.send(400,{'error':str(error)})
            if self.path == '/api/ai/reviews':
                try:return self.send(202,ai_jobs.start_review(DB,payload))
                except Conflict as error:return self.send(409,{'error':str(error)})
                except NotFound as error:return self.send(404,{'error':str(error)})
            if self.path == '/api/library/compare':
                try:return self.send(200,version_diff.compare(DB,payload))
                except KeyError:return self.send(404,{'error':'Versión no encontrada.'})
                except ValueError as error:return self.send(400,{'error':str(error)})
            if self.path == '/api/laboratories':
                try:return self.send(200,laboratories.save_from_version(DB,payload))
                except NotFound as error:return self.send(404,{'error':str(error)})
                except (ValueError,TypeError,KeyError) as error:return self.send(400,{'error':str(error) if isinstance(error,ValueError) else 'Configuración incompleta del laboratorio.'})
            if self.path == '/api/payoff-sweep':
                if payload.get('save') is True and payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión para guardar.')
                result=payoff_sweep.run(payload)
                if payload.get('save') is True:
                    if not payload.get('assumptions'):raise ValueError('Registrá los supuestos antes de guardar.')
                    result=payoff_sweep.save(DB,result)
                return self.send(200,result)
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
                    try:result=sequential.save(DB,result,payload.get('workflow_id'))
                    except NotFound as error:return self.send(404,{'error':str(error)})
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
            if self.path == '/api/graph/versions':
                try:return self.send(201,save_graph_version(DB,payload))
                except NotFound as error:return self.send(404,{'error':str(error)})
                except (ValueError,TypeError,KeyError):return self.send(400,{'error':'Revisá el título, fundamento y contenido de la red.'})
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

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from escenarios.server import Handler


class ApiTests(unittest.TestCase):
    def test_benchmark_http_background_export_and_replay(self):
        from escenarios import server,ai_jobs
        from test_laboratories import prepare_case
        case=prepare_case(server.DB);done=threading.Event();original=ai_jobs.worker
        def worker(*args):
            try:original(*args)
            finally:done.set()
        payload={'workflow_id':case['id'],'version':1,'conditions':[{'actor':0,'rounds':1,'seeds':[42,43],'baseline':'fixed0','opponent':'mirror','noise':0}], 'assumptions':'Batería sintética HTTP','reviewed':True}
        with patch('escenarios.ai_jobs.worker',side_effect=worker),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"action":1,"reason":"Ensayo sintético."}'}}):
            with urlopen(Request(self.base+'/api/ai/benchmark-jobs',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:
                job=json.load(response);self.assertEqual(response.status,202)
            self.assertTrue(done.wait(5))
        finished=ai_jobs.get_job(server.DB,job['id']);self.assertEqual(finished['state'],'ready')
        record=finished['result'];self.assertEqual(len(record['payload']['trials']),2)
        with patch('escenarios.local_ai.request',side_effect=AssertionError('No debe inferir')):
            with urlopen(self.base+'/api/ai/benchmark-replay?id='+record['id']) as response:self.assertTrue(json.load(response)['reproduced'])
        with urlopen(self.base+'/api/ai/benchmark-export?id='+record['id']) as response:self.assertEqual(json.load(response),record)

    def test_research_api_complete_temporal_workflow_and_private_routes(self):
        from escenarios import research,server,ai_jobs
        from test_laboratories import prepare_case
        from datetime import datetime,timezone,timedelta
        case=prepare_case(server.DB);start=datetime(2027,2,1,tzinfo=timezone.utc);current=[start]
        def post(data):
            with urlopen(Request(self.base+'/api/research',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return json.load(response)
        with patch('escenarios.research.clock',side_effect=lambda:current[0]):
            protocol=post({'action':'protocol','workflow_id':case['id'],'version':1,'title':'API sintética','target':'Resultado binario de prueba','horizon_hours':48,'sources':'Sintéticas','independence':'Unidades independientes sintéticas','baseline_method':'Fija 0.5','assumptions':'No evidencia real','synthetic':True,'development_end':(start+timedelta(days=2)).isoformat(),'validation_end':(start+timedelta(days=4)).isoformat(),'test_end':(start+timedelta(days=6)).isoformat(),'reviewed':True})
            candidate=post({'action':'candidate','protocol_id':protocol['id'],'name':'Original','method':'Probabilidad declarada','trained_through':start.isoformat(),'reviewed':True})
            def forecast(unit):return post({'action':'forecast','protocol_id':protocol['id'],'candidate_id':candidate['id'],'unit_id':unit,'deadline':(current[0]+timedelta(hours=1)).isoformat(),'candidate_probability':.8,'baseline_probability':.5,'feature_cutoff':current[0].isoformat(),'features':[{'reference':'Información previa sintética','available_at':start.isoformat()}]})
            def observe(event):return post({'action':'observe','event':event['event'],'outcome':1,'source':'Constatación sintética','observed_at':current[0].isoformat()})
            for i in range(5):
                event=forecast('dev-'+str(i));current[0]+=timedelta(hours=1);observe(event)
            done=threading.Event();original=ai_jobs.worker
            def worker(*args):
                try:original(*args)
                finally:done.set()
            with patch('escenarios.ai_jobs.worker',side_effect=worker),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"step":"propose_calibration","strength":2,"reason":"Ajuste acotado."}'}}):
                with urlopen(Request(self.base+'/api/ai/research-advisor',data=json.dumps({'protocol_id':protocol['id'],'candidate_id':candidate['id']}).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:job=json.load(response);self.assertEqual(response.status,202)
                self.assertTrue(done.wait(5))
            advice=ai_jobs.get_job(server.DB,job['id']);self.assertEqual(advice['state'],'ready')
            calibrated=post({'action':'accept_advice','advice_id':advice['result']['id'],'name':'Ajuste','reviewed':True})
            self.assertEqual(calibrated['payload']['version'],2)
            candidate=calibrated;current[0]=start+timedelta(days=2,hours=1);event=forecast('validation');current[0]=start+timedelta(days=4);observe(event)
            post({'action':'evaluate','protocol_id':protocol['id'],'candidate_id':candidate['id'],'partition':'validation'})
            post({'action':'select','protocol_id':protocol['id'],'candidate_id':candidate['id'],'reason':'Selección predefinida','reviewed':True})
            event=forecast('test');current[0]+=timedelta(hours=1)
            with self.assertRaises(HTTPError) as error:observe(event)
            self.assertEqual(error.exception.code,400)
            current[0]=start+timedelta(days=6);observe(event)
            final=post({'action':'evaluate','protocol_id':protocol['id'],'candidate_id':candidate['id'],'partition':'test'})
            with urlopen(self.base+'/api/research?id='+protocol['id']) as response:self.assertEqual(json.load(response)['evaluations'][0]['id'],final['id'])
            with urlopen(self.base+'/api/research/replay?id='+final['id']) as response:self.assertTrue(json.load(response)['reproduced'])
            with urlopen(self.base+'/api/research/export?id='+final['id']) as response:self.assertEqual(json.load(response),final)
            with urlopen(self.base+'/api/research/report?id='+final['id']) as response:self.assertIn('Prueba sintética',response.read().decode())
            with self.assertRaises(HTTPError) as error:post({'action':'evaluate','protocol_id':protocol['id'],'candidate_id':candidate['id'],'partition':'test'})
            self.assertEqual(error.exception.code,400)

    def test_decision_routes_bind_saved_version_and_export_replay(self):
        from escenarios import server,ai_jobs,decision_agents
        from test_laboratories import prepare_case
        from test_decision_jobs import ImmediateThread
        case=prepare_case(server.DB)
        payload={'workflow_id':case['id'],'version':1,'options':{'actor':0,'rounds':1,'seeds':[42],'baseline':'fixed0','opponent':'fixed0','noise':0},'assumptions':'Prueba sintética de API.','reviewed':True}
        def post(route,data):
            with urlopen(Request(self.base+route,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return response.status,json.load(response)
        # Preparar el trabajo sin sustituir los hilos del servidor HTTP.
        with patch('escenarios.ai_jobs.threading.Thread',ImmediateThread),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"action":1,"reason":"Ensayo de API."}'}}):job=ai_jobs.start_decision(server.DB,payload)
        with patch('escenarios.ai_jobs.start_decision',return_value=job) as start:
            status,value=post('/api/ai/decision-jobs',payload)
            self.assertEqual(status,202);self.assertEqual(value['id'],job['id']);self.assertEqual(start.call_args.args[1],payload)
        for endpoint in ['decision-export','decision-replay']:
            with urlopen(self.base+'/api/ai/'+endpoint+'?id='+job['result']['id']) as response:value=json.load(response)
            self.assertEqual(value['sha256'],job['result']['sha256'])
        with urlopen(self.base+'/api/ai/jobs?workflow=decisions:'+case['id']) as response:self.assertEqual(json.load(response)[0]['id'],job['id'])
        with self.assertRaises(HTTPError) as error:post('/api/ai/decision-jobs',{**payload,'reviewed':False})
        self.assertEqual(error.exception.code,400)
        with self.assertRaises(HTTPError) as error:post('/api/ai/decision-optimizer',{'job_id':'missing'})
        self.assertEqual(error.exception.code,404)

    def test_prediction_routes_preserve_forecasts_and_reject_unobserved_evaluation(self):
        from datetime import datetime,timezone,timedelta
        def post(route,payload):
            with urlopen(Request(self.base+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return json.load(response)
        payload={'event':'api-prospectivo','target':'Respuesta documentada','deadline':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),
            'candidate_probability':.6,'baseline_probability':.5,'candidate_ref':'api-v1','baseline_ref':'regla-v1'}
        saved=post('/api/predictions/forecast',payload)
        with urlopen(self.base+'/api/predictions') as response:self.assertIn(saved,json.load(response)['events'])
        for route,data in [('/api/predictions/forecast',payload),('/api/predictions/evaluate',payload),('/api/predictions/observe',{'event':payload['event'],'outcome':1,'source':'Prueba'})]:
            with self.assertRaises(HTTPError) as error:post(route,data)
            self.assertEqual(error.exception.code,400)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/predictions/replay?id=missing')
        self.assertEqual(error.exception.code,400)

    def test_review_rejects_stale_case_revision(self):
        def post(route,payload):
            with urlopen(Request(self.base+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return json.load(response)
        saved=post('/api/workflows',{'action':'create','title':'Revisión agentes','description':'Contexto hipotético para revisar con agentes.'})
        with self.assertRaises(HTTPError) as error:post('/api/ai/reviews',{'id':saved['id'],'revision':saved['revision']+1})
        self.assertEqual(error.exception.code,409)

    def test_network_version_routes_preserve_reviewed_graph(self):
        def post(route,payload):
            with urlopen(Request(self.base+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return json.load(response)
        case=post('/api/workflows',{'action':'create','title':'Red vinculada','description':'Contexto de relaciones hipotéticas.'})
        payload={'title':'Mapa conservado','assumptions':'Sin calibración causal.','reviewed':True,'workflow_id':case['id'],'graph':{'nodes':[{'id':0,'name':'Institución','type':0}],'edges':[]}}
        saved=post('/api/graph/versions',payload)
        with urlopen(self.base+'/api/graph/versions?workflow_id='+case['id']) as response:self.assertEqual(json.load(response),[saved])
        with self.assertRaises(HTTPError) as error:post('/api/graph/versions',{**payload,'reviewed':False})
        self.assertEqual(error.exception.code,400)
        with self.assertRaises(HTTPError) as error:post('/api/graph/versions',{**payload,'workflow_id':'missing'})
        self.assertEqual(error.exception.code,404)

    def test_laboratories_routes_use_saved_case_version(self):
        from test_laboratories import prepare_case,OPTIONS
        from escenarios import server
        case=prepare_case(server.DB)
        for kind in OPTIONS:
            payload={'kind':kind,'workflow_id':case['id'],'version':1,'options':OPTIONS[kind],'assumptions':'Supuestos de prueba revisados. '+('Contexto. '*300),'reviewed':True}
            with urlopen(Request(self.base+'/api/laboratories',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:record=json.load(response)
            self.assertEqual(record['workflow']['version'],1)
            with urlopen(self.base+'/api/laboratories?kind='+kind+'&workflow_id='+case['id']) as response:self.assertEqual([r['id'] for r in json.load(response)],[record['id']])
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/laboratories?kind=unknown')
        self.assertEqual(error.exception.code,400)

    def test_sequential_case_link_and_filter(self):
        from test_sequential import MODEL
        def post(route,payload):
            with urlopen(Request(self.base+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base})) as response:return json.load(response)
        case=post('/api/workflows',{'action':'create','title':'Expediente de árbol','description':'Contexto para un árbol vinculado.'})
        saved=post('/api/sequential',{**MODEL,'save':True,'reviewed':True,'workflow_id':case['id']})
        self.assertEqual(saved['workflow']['title'],case['title'])
        with urlopen(self.base+'/api/sequential?workflow_id='+case['id']) as response:self.assertEqual([x['id'] for x in json.load(response)],[saved['id']])
        with self.assertRaises(HTTPError) as error:post('/api/sequential',{**MODEL,'save':True,'reviewed':True,'workflow_id':'missing'})
        self.assertEqual(error.exception.code,404)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/sequential?workflow_id=missing')
        self.assertEqual(error.exception.code,404)

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.db_patch = patch('escenarios.server.DB', Path(cls.directory.name)/'test.sqlite3')
        cls.db_patch.start()
        cls.server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.db_patch.stop()
        cls.directory.cleanup()

    def test_analysis_and_nonfinite_input(self):
        with urlopen(self.base+'/api/analysis?q=0.6&cost=1') as response:
            data=json.load(response)
        self.assertEqual(data['recommendation'],'Competir')
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base+'/api/analysis?q=nan')
        self.assertEqual(error.exception.code,400)

    def test_library_routes(self):
        with urlopen(self.base+'/api/library') as response:self.assertIn('items',json.load(response))
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/library?offset=-1')
        self.assertEqual(error.exception.code,400)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/library/item?type=sweep&id=missing')
        self.assertEqual(error.exception.code,404)
        with urlopen(self.base+'/library.js') as response:self.assertIn(b'Consultar versi',response.read())

    def test_premium_assets_containment_and_missing_build(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            dist=root/'frontend'/'dist'
            dist.mkdir(parents=True)
            (dist/'index.html').write_text('<html lang="es">React</html>',encoding='utf-8')
            (dist/'bundle.js').write_text('export {};',encoding='utf-8')
            (root/'secret.txt').write_text('private',encoding='utf-8')
            with patch('escenarios.server.ROOT',root):
                with urlopen(self.base+'/app/') as response:self.assertIn(b'React',response.read())
                with urlopen(self.base+'/app/bundle.js') as response:self.assertEqual(response.headers['Content-Type'],'text/javascript')
                for path in ('/app/../../secret.txt','/app/missing.js'):
                    with self.assertRaises(HTTPError) as error:urlopen(self.base+path)
                    self.assertEqual(error.exception.code,404)
                (dist/'index.html').unlink()
                with self.assertRaises(HTTPError) as error:urlopen(self.base+'/app/')
                self.assertEqual(error.exception.code,404)

    def test_version_comparison_route(self):
        from escenarios.case_model import analyze_case,save_case
        from test_comparisons import MODEL
        from escenarios import server
        import copy
        a=save_case(server.DB,analyze_case(MODEL));m=copy.deepcopy(MODEL);m['a'][0][1]=2
        b=save_case(server.DB,analyze_case(m))
        p={'baseline':{'type':'case','id':str(a)},'candidate':{'type':'case','id':str(b)},'comparable_scales':True}
        def request():return Request(self.base+'/api/library/compare',data=json.dumps(p).encode(),headers={'Origin':self.base,'Content-Type':'application/json'})
        with urlopen(request()) as response:self.assertEqual(json.load(response)['cells'][0]['delta'],2)
        p['comparable_scales']=False
        with self.assertRaises(HTTPError) as error:urlopen(request())
        self.assertEqual(error.exception.code,400)
        self.assertIn('escalas',json.loads(error.exception.read())['error'])

    def test_comparison_report_requires_saved_record(self):
        from test_comparisons import payload
        p=payload();p.update(save=True,reviewed=True)
        with urlopen(Request(self.base+'/api/agent-comparisons',data=json.dumps(p).encode(),headers={'Origin':self.base,'Content-Type':'application/json'})) as response:
            saved=json.load(response)
        with urlopen(self.base+'/api/agent-comparisons/report.pdf?id='+saved['id']) as response:
            self.assertEqual(response.headers['Content-Type'],'application/pdf')
            self.assertTrue(response.read().startswith(b'%PDF'))
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/agent-comparisons/report.pdf?id=missing')
        self.assertEqual(error.exception.code,404)

    def test_payoff_sweep_endpoint_and_static_script(self):
        from test_payoff_sweep import payload
        p=payload()
        with urlopen(Request(self.base+'/api/payoff-sweep',data=json.dumps(p).encode(),headers={'Origin':self.base,'Content-Type':'application/json'})) as response:
            result=json.load(response)
        self.assertEqual(len(result['points']),101)
        self.assertEqual(result['points'][50]['pure'],[[0,1],[1,1]])
        with urlopen(self.base+'/payoff-sweep.js') as response:self.assertIn(b'sweep-position',response.read())
        with urlopen(self.base+'/comparisons.js') as response:self.assertIn(b'comparison-actor',response.read())

    def test_saved_sweep_review_history_and_csv(self):
        from test_payoff_sweep import payload
        p=payload();p.update(save=True,reviewed=False,assumptions='Pagos hipotéticos')
        def request():return Request(self.base+'/api/payoff-sweep',data=json.dumps(p).encode(),headers={'Origin':self.base,'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as error:urlopen(request())
        self.assertEqual(error.exception.code,400)
        p['reviewed']=True
        with urlopen(request()) as response:saved=json.load(response)
        with urlopen(self.base+'/api/payoff-sweep') as response:self.assertEqual(json.load(response)[0]['id'],saved['id'])
        with urlopen(self.base+'/api/payoff-sweep/scenarios.csv?id='+saved['id']) as response:
            self.assertIn('text/csv',response.headers['Content-Type']);self.assertIn(saved['id'].encode(),response.read())
        with urlopen(self.base+'/api/payoff-sweep/report.pdf?id='+saved['id']) as response:
            self.assertEqual(response.headers['Content-Type'],'application/pdf');self.assertTrue(response.read().startswith(b'%PDF'))
        with self.assertRaises(HTTPError) as missing_pdf:urlopen(self.base+'/api/payoff-sweep/report.pdf?id=missing')
        self.assertEqual(missing_pdf.exception.code,404)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/payoff-sweep/scenarios.csv?id=missing')
        self.assertEqual(error.exception.code,404)

    def test_disallowed_host_and_static_path(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.base+'/',headers={'Host':'outside.example'}))
        self.assertEqual(error.exception.code,403)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base+'/../escenarios/core.py')
        self.assertEqual(error.exception.code,404)

    def test_snapshot_origin_and_server_recalculation(self):
        payload=json.dumps({'cooperation':.6,'cost':3,'recommendation':'Inventada'}).encode()
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.base+'/api/snapshots',data=payload,headers={'Origin':'https://outside.example'}))
        self.assertEqual(error.exception.code,403)
        with urlopen(Request(self.base+'/api/snapshots',data=payload,headers={'Origin':self.base,'Content-Type':'application/json'})) as response:
            self.assertEqual(response.status,201)
        with urlopen(self.base+'/api/history') as response:
            data=json.load(response)
        self.assertEqual(data[0]['result']['recommendation'],'Cooperar')

    def test_frozen_workflow_pdf_route(self):
        from test_laboratories import prepare_case
        from escenarios import server
        case=prepare_case(server.DB)
        route=self.base+'/api/workflows/report.pdf?id='+case['id']+'&version=1'
        with urlopen(route) as response:
            self.assertEqual(response.headers['Content-Type'],'application/pdf')
            self.assertTrue(response.read().startswith(b'%PDF'))
        for suffix,status in [('&version=invalid',400)]:
            with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/workflows/report.pdf?id='+case['id']+suffix)
            self.assertEqual(error.exception.code,status)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/workflows/report.pdf?id=missing&version=1')
        self.assertEqual(error.exception.code,404)

    def test_workflow_creation_retrieval_and_revision_conflict(self):
        payload={'action':'create','title':'Caso API','description':'Una descripción suficiente del problema.'}
        headers={'Origin':self.base,'Content-Type':'application/json'}
        with urlopen(Request(self.base+'/api/workflows',data=json.dumps(payload).encode(),headers=headers)) as response:
            created=json.load(response)
        with urlopen(self.base+'/api/workflows?id='+created['id']) as response:
            self.assertEqual(json.load(response)['question']['key'],'objective')
        stale={'action':'message','id':created['id'],'revision':0,'text':'Respuesta'}
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.base+'/api/workflows',data=json.dumps(stale).encode(),headers=headers))
        self.assertEqual(error.exception.code,409)




    def test_sequential_api_requires_review_to_save(self):
        from test_sequential import MODEL
        payload={**MODEL,'save':True,'reviewed':False}
        def submit():
            return urlopen(Request(self.base+'/api/sequential',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.base}))
        with self.assertRaises(HTTPError) as error:submit()
        self.assertEqual(error.exception.code,400)
        payload['reviewed']=True
        payload['simulation']={'iterations':100,'seed':42,'radius':0}
        with submit() as response:record=json.load(response)
        self.assertEqual(record['equilibria'][0]['outcome'],[0,1])
        with urlopen(self.base+'/api/sequential') as response:rows=json.load(response)
        self.assertEqual(rows[0]['id'],record['id'])
        self.assertEqual(rows[0]['simulation']['decision_counts'],[100,0,0])
        with urlopen(self.base+'/api/sequential/report.pdf?id='+record['id']) as response:
            self.assertEqual(response.headers['Content-Type'],'application/pdf')
            self.assertTrue(response.read().startswith(b'%PDF-'))
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/sequential/report.pdf?id=missing')
        self.assertEqual(error.exception.code,404)

    def test_sequential_ai_application_and_saved_provenance(self):
        from escenarios import ai_jobs
        from test_sequential import MODEL
        from test_sequential_ai import proposal
        snapshot={'model':MODEL,'description':'La empresa decide antes que la contraparte.','simulation':None}
        path=Path(self.directory.name)/'test.sqlite3'
        job={'id':'api-tree-job','workflow_id':'sequential','kind':'sequential','state':'ready',
             'base_fingerprint':ai_jobs.fingerprint(ai_jobs.tree_snapshot(snapshot)),
             'result':{'proposal':proposal(),'metadata':{'model':'mistral:latest','digest':'test'}}}
        ai_jobs.store(path,job)
        headers={'Origin':self.base,'Content-Type':'application/json'}
        def post(route,payload):
            with urlopen(Request(self.base+route,data=json.dumps(payload).encode(),headers=headers)) as r:return json.load(r)
        applied=post('/api/sequential/ai-apply',{**snapshot,'job_id':job['id']})
        self.assertEqual(applied['model']['payoffs'],MODEL['payoffs'])
        saved=post('/api/sequential',{**applied['model'],'ai_job_id':job['id'],'save':True,'reviewed':True})
        self.assertEqual(saved['ai_proposal']['job_id'],job['id'])
        with self.assertRaises(HTTPError) as error:post('/api/sequential/ai-apply',{**snapshot,'description':'Cambió la descripción del caso.','job_id':job['id']})
        self.assertEqual(error.exception.code,409)


    def test_agent_simulation_save_requires_review_and_recovers_trace(self):
        from test_agents import payload
        data={**payload(),'save':True,'reviewed':False}
        def post():
            return urlopen(Request(self.base+'/api/agents',data=json.dumps(data).encode(),headers={'Origin':self.base,'Content-Type':'application/json'}))
        with self.assertRaises(HTTPError) as error:post()
        self.assertEqual(error.exception.code,400)
        data['reviewed']=True
        with post() as response:saved=json.load(response)
        with urlopen(self.base+'/api/agents') as response:rows=json.load(response)
        self.assertEqual(rows[0]['id'],saved['id']);self.assertEqual(rows[0]['rounds'][1]['memory'][0]['observed_rounds'],1)
        for endpoint,mime,signature in [('report.pdf','application/pdf',b'%PDF-'),('rounds.csv','text/csv; charset=utf-8',b'\xef\xbb\xbf')]:
            with urlopen(self.base+'/api/agents/'+endpoint+'?id='+saved['id']) as response:
                self.assertEqual(response.headers['Content-Type'],mime);self.assertTrue(response.read().startswith(signature))
            with self.assertRaises(HTTPError) as error:urlopen(self.base+'/api/agents/'+endpoint+'?id=missing')
            self.assertEqual(error.exception.code,404)

if __name__ == '__main__':unittest.main()

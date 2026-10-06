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

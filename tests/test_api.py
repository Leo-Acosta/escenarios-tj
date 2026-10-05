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

if __name__ == '__main__':unittest.main()

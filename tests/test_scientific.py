import hashlib
import io
import json
import tempfile
import unittest
import zipfile
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from pathlib import Path
from escenarios import scientific,laboratories,server
from escenarios.workflow import NotFound
from test_laboratories import prepare_case,OPTIONS

class ScientificTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'db.sqlite3';self.case=prepare_case(self.path)
    def test_frozen_reproducible_bundle_and_integrity(self):
        payload={'kind':'agents','workflow_id':self.case['id'],'version':1,'options':OPTIONS['agents'],'assumptions':'Ejemplo sintético','reviewed':True}
        run=laboratories.save_from_version(self.path,payload)
        data=scientific.bundle(self.path,self.case['id'],1)
        self.assertEqual(data,scientific.bundle(self.path,self.case['id'],1))
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            manifest=json.loads(z.read('manifest.json'))
            for name,digest in manifest['files'].items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
            self.assertIn(run['id'],z.read('rondas.csv').decode())
            self.assertEqual(len(z.read('sensibilidad.csv').splitlines()),203)
            self.assertEqual(json.loads(z.read('corridas.json'))[0]['model'],json.loads(z.read('version.json'))['model'])
            self.assertNotIn('documentos',z.namelist())
    def test_invalid_versions_fail_and_status_is_explicit(self):
        for version in [True,0,-1,'1']:
            with self.assertRaises(ValueError):scientific.bundle(self.path,self.case['id'],version)
        with self.assertRaises(NotFound):scientific.bundle(self.path,self.case['id'],99)
        self.assertEqual(scientific.status()['execution'],'local_bounded')
    def test_http_download_matches_core(self):
        previous=server.DB;server.DB=self.path
        http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{http.server_port}/api/scientific/bundle?workflow_id={self.case["id"]}&version=1'
            with urlopen(url) as response:
                self.assertEqual(response.headers['Content-Type'],'application/zip')
                self.assertEqual(response.read(),scientific.bundle(self.path,self.case['id'],1))
        finally:
            http.shutdown();http.server_close();thread.join();server.DB=previous

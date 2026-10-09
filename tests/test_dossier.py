import base64
import copy
import io
import json
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from escenarios import dossier,continuity,executive,executive_view,server
from escenarios.workflow import operate
from test_laboratories import prepare_case

class DossierTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'db.sqlite3'
        self.case=operate(self.path,{'action':'create','title':'Ejemplo sintético','description':'Verificación documental sintética, no caso real.'})
        self.scope=self.case['id']
    def save(self,**values):return dossier.save(self.path,{'workflow_id':self.scope,**values})
    def document(self):
        from reportlab.pdfgen import canvas
        stream=io.BytesIO();c=canvas.Canvas(stream);c.drawString(50,700,'Documento sintetico 3088');c.save()
        return self.save(kind='document',name='ejemplo.pdf',content=base64.b64encode(stream.getvalue()).decode(),note='Prueba sintética')
    def fact(self,doc,value,date='2026-09-28',**extra):return self.save(kind='fact',title='Lectura sintética',date=date,value=value,unit='kWh',evidence='documented_declared',document_id=doc['id'],locator='Página 1',uncertainty='Fecha y medidor declarados',reviewed=True,**extra)
    def test_document_review_correction_snapshot_export_and_backup(self):
        doc=self.document();a=self.fact(doc,'3088');b=self.fact(doc,'3285','2026-10-09');fixed=self.fact(doc,'3286','2026-10-09',supersedes=b['id'])
        result=dossier.consumption(self.path,self.scope,a['id'],fixed['id'])
        self.assertEqual((result['difference_kwh'],result['days'],result['daily_kwh']),('198',11,'18'))
        calc=self.save(kind='calculation',first_id=a['id'],last_id=fixed['id'],reviewed=True)
        altered=copy.deepcopy(calc);altered['payload']['result']['daily_kwh']='99';altered['sha256']=dossier.digest(altered['payload'])
        with self.assertRaises(ValueError):dossier.verify(altered)
        with self.assertRaises(ValueError):dossier.consumption(self.path,self.scope,a['id'],b['id'])
        self.save(kind='event',title='Reclamo sintético',actor='Distribuidora ficticia',date='2026-10-09',status='submitted',detail='Registro de prueba',document_id=doc['id'],reviewed=True)
        snap=self.save(kind='snapshot',title='Informe sintético',reviewed=True)
        self.fact(doc,'3400','2026-10-10')
        self.assertEqual(dossier.read(self.path,snap['id']),snap)
        z=zipfile.ZipFile(io.BytesIO(dossier.export_zip(snap)))
        self.assertIn('registro.json',z.namelist());self.assertTrue(any(n.startswith('originales/') for n in z.namelist()))
        self.assertEqual(json.loads(z.read('registro.json')),snap)
        self.assertIn('3286',dossier.report_html(snap))
        content,_=continuity.snapshot(self.path)
        recovered,_=continuity.recover(content,Path(self.tmp.name)/'recovered')
        self.assertEqual(dossier.read(recovered,snap['id']),snap)
    def test_cross_scope_missing_review_invalid_files_and_tampering(self):
        doc=self.document();other=operate(self.path,{'action':'create','title':'Otra prueba','description':'Expediente distinto'})
        self.scope=other['id']
        with self.assertRaises(ValueError):self.fact(doc,'100')
        self.scope=self.case['id']
        for name,content in [('../x.pdf',b'%PDF-x'),('x.html',b'<html>'),('x.pdf',b'notpdf')]:
            with self.assertRaises(ValueError):self.save(kind='document',name=name,content=base64.b64encode(content).decode())
        with self.assertRaises(ValueError):self.save(kind='fact',reviewed=False)
        changed=copy.deepcopy(doc);changed['payload']['content']=base64.b64encode(b'%PDF-bad').decode()
        changed['sha256']=dossier.digest(changed['payload'])
        with self.assertRaises(ValueError):dossier.verify(changed)
    def test_readings_reject_future_order_reset_nonfinite_and_assumptions(self):
        doc=self.document();a=self.fact(doc,'3088')
        for value,day in [('10','2026-10-09'),('NaN','2026-10-09'),('3286','2026-09-28')]:
            b=self.fact(doc,value,day)
            with self.assertRaises(ValueError):dossier.consumption(self.path,self.scope,a['id'],b['id'])
    def test_frozen_unified_report_includes_documentary_context(self):
        self.case=prepare_case(self.path);self.scope=self.case['id'];doc=self.document();self.fact(doc,'3088')
        report=executive.create(self.path,{'workflow_id':self.scope,'version':1,'title':'Sintético','sections':['matrix'],'references':[],'evidence_mode':'declared','reviewed':True})
        self.assertIn('Lectura sintética',executive_view.html(report))
        self.fact(doc,'3286','2026-10-09')
        self.assertNotIn('3286',executive_view.html(report))
        self.assertEqual(executive.read(self.path,report['id']),report)
    def test_http_journey_and_origin_protection(self):
        old=server.DB;server.DB=self.path;self.addCleanup(setattr,server,'DB',old)
        http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        worker=threading.Thread(target=http.serve_forever,daemon=True);worker.start()
        self.addCleanup(http.server_close);self.addCleanup(http.shutdown)
        root='http://127.0.0.1:'+str(http.server_port)
        payload={'workflow_id':self.scope,'kind':'snapshot','title':'Prueba HTTP','reviewed':True}
        with self.assertRaises(HTTPError):urlopen(Request(root+'/api/dossier',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}))
        r=json.load(urlopen(Request(root+'/api/dossier',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':root})))
        self.assertIn(b'Prueba HTTP',urlopen(root+'/api/dossier/html?id='+r['id']).read())
        self.assertEqual(json.load(urlopen(root+'/api/dossier/export?id='+r['id'])),r)

if __name__=='__main__':unittest.main()

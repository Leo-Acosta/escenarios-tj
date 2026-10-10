import base64
import copy
import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from escenarios import scientific_runtime as r,continuity,executive
from escenarios.workflow import Conflict
from test_laboratories import prepare_case

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'db.sqlite3';self.case=prepare_case(self.path)
    def test_temporal_schema_future_and_cross_boundary_rejected(self):
        data,cuts=r.synthetic();self.assertEqual(r.validate_data(data,cuts),[120,120,120])
        for bad in [data.replace('sintetica-0001','sintetica-0000'),data.replace('2020-01-01T00:00:00Z','2099-01-01T00:00:00Z'),data.replace('x1,x2','x99,x2'),data.replace('2020-04-29T12:00:00Z','2020-04-30T12:00:00Z')]:
            with self.assertRaises(ValueError):r.validate_data(bad,cuts)
    def fake_execute(self,script,folder,extra=None,deep=False):
        if script!='aprendizaje.R':return
        rows=list(csv.DictReader(io.StringIO((folder/'datos.csv').read_text())))
        dev=rows[:120];val=rows[120:240];test=rows[240:];baseline=sum(int(x['resultado']) for x in dev)/120
        target=folder/'evaluacion-final';target.mkdir()
        def write(name,headers,values):
            with (target/name).open('w',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(values)
        write('pronosticos.csv',['unidad','resultado','pronostico','referencia'],[(x['unidad'],x['resultado'],baseline,baseline) for x in test])
        write('pronosticos-validacion.csv',['unidad','resultado','referencia'],[(x['unidad'],x['resultado'],baseline) for x in val])
        write('validacion.csv',['metodo','brier_validacion'],[('referencia',sum((baseline-int(x['resultado']))**2 for x in val)/120)])
    def test_job_conservation_replay_backup_and_frozen_report(self):
        with patch.object(r,'executable',return_value='Rscript'),patch.object(r,'status',return_value={'ready':True}),patch.object(r,'execute',side_effect=self.fake_execute),patch.object(r.threading.Thread,'start'):
            job=r.start(self.path,{'workflow_id':self.case['id'],'version':1,'mode':'synthetic','reviewed':True})
            record=r.read(self.path,job['id']);r.worker(self.path,record)
        record=r.read(self.path,job['id']);self.assertEqual(record['state'],'ready')
        self.assertEqual(record['result']['metrics']['ties'],120)
        with patch.object(r,'execute',side_effect=AssertionError('No ejecutar R')):self.assertTrue(r.verify(record)['reproduced'])
        content,info=continuity.snapshot(self.path);self.assertIn('scientific_jobs',info['tables'])
        report=executive.create(self.path,{'workflow_id':self.case['id'],'version':1,'reviewed':True,'sections':['matrix'],'references':[],'title':'Prueba sintética','evidence_mode':'synthetic'})
        self.assertEqual(report['payload']['scientific'][0]['result'],record['result'])
        self.assertTrue(executive.verify(report)['reproduced'])
        changed=copy.deepcopy(report);changed['payload']['scientific'][0]['result']['metrics']['ties']=0
        changed['sha256']=r.fingerprint(changed['payload'])
        with self.assertRaises(ValueError):executive.verify(changed)
        damaged=copy.deepcopy(record);damaged['result']['metrics']['ties']=0
        with self.assertRaises(ValueError):r.verify(damaged)
    def test_worker_failure_is_preserved_and_lock_released(self):
        with patch.object(r,'executable',return_value='Rscript'),patch.object(r,'status',return_value={}),patch.object(r,'execute',side_effect=ValueError('Fallo deliberado de prueba')),patch.object(r.threading.Thread,'start'):
            job=r.start(self.path,{'workflow_id':self.case['id'],'version':1,'mode':'graphics','reviewed':True});r.worker(self.path,r.read(self.path,job['id']))
        self.assertIn('Fallo deliberado',r.read(self.path,job['id'])['error']);self.assertFalse(r.LOCK.locked())
    def test_live_job_survives_recovery_and_blocks_other_instance(self):
        with patch.object(r,'executable',return_value='Rscript'),patch.object(r.threading.Thread,'start'):
            job=r.start(self.path,{'workflow_id':self.case['id'],'version':1,'mode':'graphics','reviewed':True})
            try:
                r.recover(self.path);record=r.read(self.path,job['id']);self.assertEqual(record['state'],'running')
                other=copy.deepcopy(record);other['id']='other-instance'
                with self.assertRaises(Conflict):r.store(self.path,other,new=True)
            finally:r.LOCK.release()
        with patch.object(r,'process_alive',return_value=False):r.recover(self.path)
        self.assertEqual(r.read(self.path,job['id'])['state'],'failed')

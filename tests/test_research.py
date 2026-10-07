import copy
import json
import tempfile
import unittest
from contextlib import closing
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
from escenarios import research as r,prediction_eval,decision_agents,local_ai,ai_jobs
from test_laboratories import prepare_case

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'research.sqlite3';self.case=prepare_case(self.path)
        self.t=datetime(2027,1,1,tzinfo=timezone.utc);self.current=self.t
        self.patch=patch('escenarios.research.clock',side_effect=lambda:self.current);self.patch.start();self.addCleanup(self.patch.stop)
        self.config={'title':'Ensayo <script>','workflow_id':self.case['id'],'version':1,'target':'Respuesta documentada antes del plazo','horizon_hours':48,
            'sources':'Documento sintético','independence':'Unidades distintas de prueba','baseline_method':'Probabilidad fija 0.5','assumptions':'Caso de prueba, no EDESUR.',
            'synthetic':True,'development_end':(self.t+timedelta(days=2)).isoformat(),'validation_end':(self.t+timedelta(days=4)).isoformat(),'test_end':(self.t+timedelta(days=6)).isoformat(),'reviewed':True}
        self.protocol=r.protocol(self.path,self.config);self.candidate=r.candidate(self.path,{'protocol_id':self.protocol['id'],'name':'Original','method':'Probabilidad manual declarada','trained_through':self.t.isoformat(),'reviewed':True})
    def forecast(self,unit,candidate=None,**extra):
        payload={'protocol_id':self.protocol['id'],'candidate_id':(candidate or self.candidate)['id'],'unit_id':unit,'deadline':(self.current+timedelta(hours=1)).isoformat(),
            'candidate_probability':.8,'baseline_probability':.5,'feature_cutoff':self.current.isoformat(),'features':[{'reference':'Fuente sintética','available_at':self.t.isoformat()}]}
        return r.forecast(self.path,{**payload,**extra})
    def observe(self,event,outcome=1):
        return r.observe(self.path,{'event':event['event'],'outcome':outcome,'source':'Constatación sintética','observed_at':self.current.isoformat()})
    def evaluate(self,partition,candidate=None):return r.evaluate(self.path,{'protocol_id':self.protocol['id'],'candidate_id':(candidate or self.candidate)['id'],'partition':partition})
    def development(self,n=5):
        for i in range(n):
            event=self.forecast('dev-'+str(i));self.current+=timedelta(hours=1);self.observe(event,i%2)
    def validation(self,candidate=None):
        self.current=self.t+timedelta(days=2,hours=1);event=self.forecast('validation',candidate)
        self.current=self.t+timedelta(days=4);self.observe(event);return self.evaluate('validation',candidate)
    def test_end_to_end_calibrated_candidate_validation_selection_final_export_replay(self):
        self.development();calibrated=r.calibrate(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id'],'strength':2,'name':'Calibrado','reviewed':True})
        self.assertEqual(calibrated['payload']['version'],2);self.assertEqual(calibrated['payload']['calibration']['dataset_sha256'],decision_agents.fingerprint(calibrated['payload']['calibration']['dataset']))
        self.validation(calibrated)
        r.select(self.path,{'protocol_id':self.protocol['id'],'candidate_id':calibrated['id'],'reason':'Selección sintética predefinida','reviewed':True})
        event=self.forecast('test',calibrated)
        self.assertNotEqual(event['candidate_probability'],.8)
        self.current+=timedelta(hours=1)
        with self.assertRaises(ValueError):self.observe(event)
        self.current=self.t+timedelta(days=6)
        with self.assertRaises(ValueError):self.evaluate('test',calibrated)
        self.observe(event);final=self.evaluate('test',calibrated)
        self.assertEqual(final['payload']['result']['evidence'],'synthetic_only')
        self.assertFalse(final['payload']['result']['promotion_allowed'])
        with patch('escenarios.local_ai.request',side_effect=AssertionError('Sin inferencia')):self.assertTrue(r.replay(self.path,final['id'])['reproduced'])
        self.assertEqual(r.export(self.path,final['id']),final)
        self.assertIn('&lt;script&gt;',r.report(self.path,final['id']));self.assertNotIn('<script>',r.report(self.path,final['id']))
        with self.assertRaises(ValueError):self.evaluate('test',calibrated)
    def test_future_information_cross_window_units_and_duplicate_forecast_rejected(self):
        with self.assertRaises(ValueError):self.forecast('future',features=[{'reference':'Futuro','available_at':(self.current+timedelta(seconds=1)).isoformat()}])
        with self.assertRaises(ValueError):self.forecast('window',deadline=(self.t+timedelta(days=3)).isoformat())
        self.forecast('unit')
        with self.assertRaises(ValueError):self.forecast('unit')
        self.current=self.t+timedelta(days=2)
        with self.assertRaises(ValueError):self.forecast('unit')
        with self.assertRaises(ValueError):r.candidate(self.path,{'protocol_id':self.protocol['id'],'name':'Tardío','method':'Fuga','trained_through':self.current.isoformat(),'reviewed':True})
    def test_final_selection_requires_validation_and_is_immutable(self):
        with self.assertRaises(ValueError):r.select(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id'],'reason':'Prueba','reviewed':True})
        self.validation();r.select(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id'],'reason':'Predefinido','reviewed':True})
        with self.assertRaises(ValueError):r.select(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id'],'reason':'Cambiar','reviewed':True})
    def test_generic_prediction_api_cannot_open_reserved_observation_or_evaluate_it(self):
        event=self.forecast('reserved');self.current+=timedelta(hours=1);self.observe(event)
        self.assertEqual(prediction_eval.history(self.path),[])
        with self.assertRaises(ValueError):prediction_eval.observe(self.path,{'event':event['event'],'outcome':1,'source':'Otro endpoint'})
        with self.assertRaises(ValueError):prediction_eval.evaluate(self.path,{'candidate_ref':self.candidate['id'],'baseline_ref':self.protocol['id']})
    def test_real_development_and_validation_never_claim_final_improvement(self):
        with closing(r.connect(self.path)) as db,db:
            p=copy.deepcopy(self.protocol);p['payload']['synthetic']=False;p['sha256']=decision_agents.fingerprint(p['payload']);db.execute('UPDATE research_records SET payload=? WHERE id=?',(json.dumps(p),p['id']))
        self.development(35);evaluation=self.evaluate('development')
        self.assertEqual(evaluation['payload']['result']['evidence'],'development_only')
    def test_advisor_only_uses_development_requires_acceptance_and_rejects_stale_data(self):
        self.development()
        response={'done':True,'message':{'content':'{"step":"propose_calibration","strength":2,"reason":"Probar calibración sin promoción."}'}}
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=response) as request:
            advice=r.advisor(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id']})
        self.assertFalse(advice['payload']['auto_execution']);self.assertEqual(len(r.dashboard(self.path,self.protocol['id'])['candidates']),1)
        prompt=json.loads(request.call_args.args[1]['messages'][1]['content']);self.assertEqual(prompt['development_metrics']['partition'],'development')
        with self.assertRaises(ValueError):r.accept_advice(self.path,{'advice_id':advice['id'],'name':'Nuevo','reviewed':False})
        new=r.accept_advice(self.path,{'advice_id':advice['id'],'name':'Nuevo','reviewed':True});self.assertEqual(new['payload']['calibration']['advice_id'],advice['id'])
        event=self.forecast('new-data');self.current+=timedelta(hours=1);self.observe(event)
        with self.assertRaises(ValueError):r.accept_advice(self.path,{'advice_id':advice['id'],'name':'Otro','reviewed':True})
    def test_tampered_dataset_or_recomputed_metric_is_rejected(self):
        self.development();evaluation=self.evaluate('development')
        value=copy.deepcopy(evaluation);value['payload']['result']['delta']=999;value['sha256']=decision_agents.fingerprint(value['payload'])
        with closing(r.connect(self.path)) as db,db:db.execute('UPDATE research_records SET payload=? WHERE id=?',(json.dumps(value),value['id']))
        with self.assertRaises(ValueError):r.replay(self.path,value['id'])
    def test_advisor_transport_failure_preserves_failed_trace(self):
        from escenarios.local_ai import AIError
        self.development()
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',side_effect=AIError('Servicio no disponible')):
            with self.assertRaises(AIError) as failure:r.advisor(self.path,{'protocol_id':self.protocol['id'],'candidate_id':self.candidate['id']})
        trace=failure.exception.trace
        self.assertEqual(trace['state'],'failed');self.assertIn('Servicio no disponible',trace['error'])
        with closing(r.connect(self.path)) as db:
            stored=json.loads(db.execute('SELECT payload FROM decision_audits WHERE id=?',(trace['id'],)).fetchone()[0])
        self.assertEqual(stored['state'],'failed');self.assertIn('finished_at',stored)
    def test_reference_rule_fixed_seed_and_incomplete_validation_do_not_allow_selection(self):
        p=r.protocol(self.path,{**self.config,'baseline_probability':.5})
        c=r.candidate(self.path,{'protocol_id':p['id'],'name':'Original','method':'Declarado','trained_through':self.current.isoformat(),'reviewed':True})
        oldp,oldc=self.protocol,self.candidate;self.protocol,self.candidate=p,c
        with self.assertRaises(ValueError):self.forecast('bad-baseline',baseline_probability=.6)
        self.development()
        with self.assertRaises(ValueError):r.evaluate(self.path,{'protocol_id':p['id'],'candidate_id':c['id'],'partition':'development','seed':7})
        self.current=self.t+timedelta(days=2);first=self.forecast('validation-1');self.forecast('validation-2');self.current=self.t+timedelta(days=4);self.observe(first)
        self.evaluate('validation')
        with self.assertRaises(ValueError):r.select(self.path,{'protocol_id':p['id'],'candidate_id':c['id'],'reason':'Incompleto','reviewed':True})

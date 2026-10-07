import tempfile
import unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
from escenarios import prediction_eval as p,review_agents,local_ai


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'test.sqlite3'
        self.payload={'event':'reclamo-1','target':'Respuesta dentro del plazo definido',
            'deadline':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),
            'candidate_probability':.8,'baseline_probability':.5,
            'candidate_ref':'analista-v1','baseline_ref':'politica-v1'}

    def test_prospective_record_cannot_be_overwritten_or_observed_early(self):
        p.forecast(self.path,self.payload)
        with self.assertRaises(ValueError):p.forecast(self.path,self.payload)
        with self.assertRaises(ValueError):p.observe(self.path,{'event':'reclamo-1','outcome':1,'source':'Documento'})
        self.assertIsNone(p.history(self.path)[0]['observation'])

    def test_invalid_probabilities_and_unobserved_evaluation(self):
        for value in [True,float('nan'),float('inf'),-1,1.1]:
            with self.assertRaises(ValueError):p.forecast(self.path,{**self.payload,'candidate_probability':value})
        with self.assertRaises(ValueError):p.evaluate_rows([])

    def test_observation_immutable_and_evaluation_replay(self):
        p.forecast(self.path,self.payload)
        real=datetime
        with patch('escenarios.prediction_eval.datetime') as clock:
            clock.fromisoformat.side_effect=real.fromisoformat
            clock.now.return_value=real.now(timezone.utc)+timedelta(days=2)
            p.observe(self.path,{'event':'reclamo-1','outcome':1,'source':'Documento de prueba sintético'})
            with self.assertRaises(ValueError):p.observe(self.path,{'event':'reclamo-1','outcome':0,'source':'Cambio'})
        result=p.evaluate(self.path,self.payload)
        self.assertEqual(result['evidence'],'insufficient_evidence')
        self.assertTrue(p.replay(self.path,result['id'])['reproduced'])

    def test_synthetic_benchmark_distinguishes_better_and_worse(self):
        rows=[{'candidate_probability':.9 if i%2 else .1,'baseline_probability':.5,
            'observation':{'outcome':i%2}} for i in range(40)]
        a=p.evaluate_rows(rows);self.assertEqual(a,p.evaluate_rows(rows))
        self.assertEqual(a['evidence'],'provisional_improvement')
        for row in rows:row['candidate_probability']=1-row['candidate_probability']
        self.assertEqual(p.evaluate_rows(rows)['evidence'],'insufficient_evidence')

    def test_critic_rejects_inconsistent_verdict(self):
        for value in [{'verdict':'no_objection','issues':['Contradicción'],'questions':[]},
                      {'verdict':'revise','issues':[],'questions':[]}]:
            with self.assertRaises(local_ai.AIError):review_agents.validate_critic(value)

    def test_python_rejects_cross_actor_actions_missed_by_critic(self):
        proposal={'actors':['Usuario','Empresa de suministro'],'strategies':[['Usuario: reclamar','Empresa: revisar'],['Usuario: recurrir','Empresa: responder']]}
        self.assertEqual(len(review_agents.proposal_checks(proposal)),2)
        proposal['strategies']=[['Usuario: reclamar','Usuario: consultar'],['Empresa: revisar','Empresa: responder']]
        self.assertEqual(review_agents.proposal_checks(proposal),[])

    def test_review_never_certifies_missing_matrix(self):
        analyst={'proposal':{'actors':['Usuario','EDESUR'],'strategies':[['Reclamar','Consultar abogado'],['Responder','Rechazar']]},'input_context':{}}
        with patch('escenarios.local_ai.propose',return_value=analyst),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"verdict":"no_objection","issues":[],"questions":[]}'}}):
            result=review_agents.run(self.path,{'model':None})
        self.assertEqual(result['status'],'requires_revision')
        self.assertIsNone(result['calculation'])

    def test_incomplete_critic_keeps_failure_trace(self):
        analyst={'proposal':{'actors':['Usuario','EDESUR'],'strategies':[['Reclamar','Consultar'],['Responder','Rechazar']]},'input_context':{}}
        with patch('escenarios.local_ai.propose',return_value=analyst),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'done_reason':'length','message':{'content':'{}'}}):
            with self.assertRaises(review_agents.ReviewFailure) as error:review_agents.run(self.path,{'model':None})
        self.assertEqual(error.exception.trace['analyst'],analyst)
        self.assertEqual(error.exception.trace['critic_response']['done_reason'],'length')

    def test_failed_review_job_keeps_trace_and_releases_lock(self):
        from escenarios import ai_jobs
        value={'id':'failed-review','workflow_id':'review:test','kind':'review','state':'running','result':None,'error':None}
        ai_jobs.RUNNING=True
        with patch('escenarios.review_agents.run',side_effect=review_agents.ReviewFailure('Respuesta rechazada',{'critic_response':{'done_reason':'length'}})):
            ai_jobs.worker(self.path,{},value)
        saved=ai_jobs.get_job(self.path,value['id'])
        self.assertEqual(saved['state'],'failed');self.assertIsNone(saved['result'])
        self.assertEqual(saved['failure_trace']['critic_response']['done_reason'],'length')
        self.assertFalse(ai_jobs.RUNNING)

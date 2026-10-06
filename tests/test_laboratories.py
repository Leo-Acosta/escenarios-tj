import tempfile
import unittest
from pathlib import Path
from escenarios import laboratories
from escenarios.workflow import operate,QUESTIONS,NotFound

MODEL={'title':'Negociación','actors':['Municipio','Vecinos'],'strategies':[['Acuerdo','Competir'],['Acuerdo','Competir']],'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.6}
OPTIONS={'agents':{'rounds':5,'seed':42,'noise':0,'policies':['mirror','adaptive']},'comparison':{'rounds':5,'seed':42,'noise':0,'repetitions':2},'sweep':{'actor':'a','row':0,'column':0,'minimum':0,'maximum':10}}

def prepare_case(path):
    c=operate(path,{'action':'create','title':'Expediente de laboratorios','description':'Explorar escenarios de negociación con vecinos.'})
    for _ in QUESTIONS:c=operate(path,{'action':'message','id':c['id'],'revision':c['revision'],'text':'Respuesta hipotética del analista.'})
    c=operate(path,{'action':'calculate','id':c['id'],'revision':c['revision'],'model':MODEL,'evidence':[],'assumptions':'Pagos hipotéticos en puntos.','reviewed':True})
    return c

class LaboratoriesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'db.sqlite3';self.case=prepare_case(self.path)
    def payload(self,kind):return {'kind':kind,'workflow_id':self.case['id'],'version':1,'options':OPTIONS[kind],'assumptions':'Políticas e intervalos hipotéticos.','reviewed':True}
    def test_all_labs_use_frozen_matrix_and_preserve_source(self):
        for kind in OPTIONS:
            p=self.payload(kind);p['model']={**MODEL,'a':[[999,999],[999,999]]}
            r=laboratories.save_from_version(self.path,p)
            self.assertEqual(r['model'],MODEL)
            self.assertEqual(r['workflow'],{'id':self.case['id'],'title':MODEL['title'],'version':1})
            self.assertEqual(laboratories.history(self.path,kind,self.case['id']),[r])
            self.assertEqual(laboratories.history(self.path,kind),[r])
    def test_review_and_calculated_source_are_required(self):
        p=self.payload('agents');p['reviewed']=False
        with self.assertRaises(ValueError):laboratories.save_from_version(self.path,p)
        p=self.payload('agents');p['version']=2
        with self.assertRaises(NotFound):laboratories.save_from_version(self.path,p)
        p=self.payload('agents');p['options']=None
        with self.assertRaises(ValueError):laboratories.save_from_version(self.path,p)
        self.assertEqual(laboratories.history(self.path,'agents'),[])
    def test_history_filters_before_limit_and_does_not_modify_old_runs(self):
        from escenarios import agents
        linked=laboratories.save_from_version(self.path,self.payload('agents'))
        for _ in range(21):agents.save(self.path,agents.run({'model':MODEL,'options':OPTIONS['agents'],'assumptions':'Histórico independiente.'}))
        self.assertNotIn(linked,laboratories.history(self.path,'agents'))
        self.assertEqual(laboratories.history(self.path,'agents',self.case['id']),[linked])
    def test_invalid_kind_and_missing_case(self):
        with self.assertRaises(ValueError):laboratories.history(self.path,'unknown')
        with self.assertRaises(ValueError):laboratories.module([])
        with self.assertRaises(NotFound):laboratories.history(self.path,'sweep','missing')

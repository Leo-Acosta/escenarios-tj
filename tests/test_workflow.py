import tempfile
import unittest
from pathlib import Path
from escenarios.workflow import operate,get_workflow,get_version,list_workflows,Conflict,QUESTIONS


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'workflow.sqlite3'
        self.data=operate(self.path,{'action':'create','title':'Negociación','description':'Analizar una negociación sobre una obra pública.'})

    def action(self,action,**kwargs):
        self.data=operate(self.path,{'action':action,'id':self.data['id'],'revision':self.data['revision'],**kwargs})
        return self.data

    def model(self):
        return {'title':'Negociación','actors':['Municipio','Vecinos'],
                'strategies':[['Acuerdo','Competir'],['Acuerdo','Competir']],
                'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.6}

    def complete(self):
        for key,_ in QUESTIONS:self.action('message',text='Respuesta del analista para '+key)

    def calculate(self,**kwargs):
        return self.action('calculate',model=self.model(),evidence=[{'title':'Acta','reference':'Acta 12','claim':'Plazo indicado por el analista'}],assumptions='Pagos hipotéticos para explorar incentivos.',reviewed=True,**kwargs)

    def test_conversation_resumes_and_calculation_keeps_context(self):
        self.action('message',text='Priorizar un acuerdo.')
        recovered=get_workflow(self.path,self.data['id'])
        self.assertEqual(recovered['question']['key'],'horizon')
        self.assertEqual(recovered['messages'][2]['text'],'Priorizar un acuerdo.')
        for _ in range(4):self.action('message',text='Respuesta aportada por el analista.')
        calculated=self.calculate()
        result=calculated['result']
        self.assertAlmostEqual(result['values_a'][0],1.8)
        self.assertAlmostEqual(result['values_a'][1],3.4)
        self.assertEqual(result['context']['answers']['objective'],'Priorizar un acuerdo.')
        self.assertFalse(result['context']['evidence'][0]['verified'])
        self.assertEqual(result['context']['version'],1)
        self.assertEqual(len(result['context']['conversation']),12)
        self.assertEqual(list_workflows(self.path)[0]['stage'],'calculated')

    def test_questions_and_review_are_required_without_partial_write(self):
        original=get_workflow(self.path,self.data['id'])
        with self.assertRaises(ValueError):self.calculate()
        self.assertEqual(get_workflow(self.path,self.data['id'])['revision'],original['revision'])
        self.complete()
        with self.assertRaises(ValueError):self.action('calculate',model=self.model(),assumptions='Supuestos',reviewed=False)
        self.assertEqual(get_workflow(self.path,self.data['id'])['versions'],[])

    def test_stale_revision_and_immutable_versions(self):
        stale=self.data['revision']
        self.complete();first=self.calculate()['result']
        with self.assertRaises(Conflict):operate(self.path,{'action':'message','id':self.data['id'],'revision':stale,'text':'No debe entrar'})
        changed=self.model();changed['q']=0
        self.action('calculate',model=changed,evidence=[],assumptions='Otro supuesto',reviewed=True)
        self.assertEqual(get_version(self.path,self.data['id'],1),first)
        self.assertEqual(get_version(self.path,self.data['id'],2)['model']['q'],0)
        self.assertEqual(len(self.data['versions']),2)

    def test_incomplete_draft_does_not_fake_results(self):
        self.complete();self.calculate()
        incomplete=self.model();incomplete['a'][0][0]=None
        saved=self.action('draft',model=incomplete,evidence=[],assumptions='Borrador pendiente')
        self.assertIsNone(saved['result'])
        self.assertEqual(saved['stage'],'modeling')
        self.assertEqual(len(saved['versions']),1)
        with self.assertRaises(ValueError):self.action('calculate',model=incomplete,evidence=[],assumptions='Borrador',reviewed=True)

    def test_nonfinite_and_source_validation(self):
        self.complete()
        for value in [float('nan'),float('inf')]:
            invalid=self.model();invalid['a'][0][0]=value
            with self.assertRaises(ValueError):self.action('draft',model=invalid,evidence=[],assumptions='Prueba')
        with self.assertRaises(ValueError):self.action('draft',model=self.model(),evidence=[{'title':'Acta','reference':'','claim':'Dato'}],assumptions='Prueba')

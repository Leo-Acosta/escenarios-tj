import copy
import tempfile
import unittest
from pathlib import Path
from escenarios.sequential import analyze,save,history

MODEL={'title':'Entrada','actors':['Entrante','Instalada'],'actions':[['Entrar','No entrar'],['Competir','Acomodar'],['Mantener','Expandir']], 'payoffs':[[[-1,-1],[2,1]],[[0,3],[0,2]]],'assumptions':'Hipotético'}

class SequentialTests(unittest.TestCase):
    def test_backward_induction_accounts_for_response(self):
        r=analyze(MODEL)
        self.assertEqual(r['responses'],[[1],[0]])
        self.assertEqual(r['equilibria'],[{'first':0,'responses':[1,0],'outcome':[0,1],'payoffs':[2,1]}])
    def test_off_path_response_changes_first_decision(self):
        m=copy.deepcopy(MODEL);m['payoffs'][0][1]=[-2,1]
        self.assertEqual(analyze(m)['equilibria'][0]['first'],1)
    def test_all_ties_preserve_eight_complete_plans(self):
        m=copy.deepcopy(MODEL);m['payoffs']=[[[0,0],[0,0]],[[0,0],[0,0]]]
        self.assertEqual(len(analyze(m)['equilibria']),8)
    def test_invalid_payoffs_and_incomplete_model(self):
        for val in [float('nan'),float('inf'),True,1000001,'3']:
            m=copy.deepcopy(MODEL);m['payoffs'][0][0][0]=val
            with self.assertRaises(ValueError):analyze(m)
        with self.assertRaises(ValueError):analyze({})
    def test_saved_versions_are_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'db.sqlite3';r=analyze(MODEL);first=save(path,r)
            r['model']['title']='Otra';second=save(path,r)
            rows=history(path)
            self.assertEqual(rows[1]['model']['title'],'Entrada')
            self.assertNotEqual(first['id'],second['id'])

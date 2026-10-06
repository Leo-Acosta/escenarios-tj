import copy
import unittest
import tempfile
import csv
from pathlib import Path
from io import StringIO
from test_comparisons import MODEL
from escenarios.payoff_sweep import run
from escenarios.payoff_sweep import save,history,get_record,build_csv

def payload():return {'model':copy.deepcopy(MODEL),'options':{'actor':'a','row':0,'column':1,'minimum':0,'maximum':2}}

class SweepTests(unittest.TestCase):
    def test_equilibrium_changes_and_tie_are_preserved(self):
        p=payload();before=copy.deepcopy(p);r=run(p)
        self.assertEqual(p,before);self.assertEqual(len(r['points']),101)
        self.assertEqual(r['points'][0]['pure'],[[1,1]])
        self.assertEqual(r['points'][50]['pure'],[[0,1],[1,1]])
        self.assertEqual(r['points'][-1]['pure'],[[0,1]])
        self.assertEqual(len(r['changes']),2)
    def test_b_utility_uses_correct_column(self):
        p=payload();p['options'].update(actor='b',row=1,column=0)
        r=run(p);self.assertEqual(r['points'][0]['values_b'][0],1.5)
        self.assertEqual(r['points'][-1]['values_b'][0],2.5)
    def test_invalid_bounds_and_indices(self):
        for key,value in [('minimum',float('nan')),('maximum',0),('row',True),('actor','other'),('column',2),('maximum',1000001)]:
            p=payload();p['options'][key]=value
            with self.assertRaises(ValueError):run(p)

    def test_saved_version_preserves_matrix_and_points(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'sweep.sqlite3';r=run(payload());saved=save(path,r)
            r['model']['a'][0][0]=999;r['points'][0]['value']=999
            recovered=get_record(path,saved['id'])
            self.assertEqual(recovered['model']['a'][0][0],3)
            self.assertEqual(recovered['points'][0]['value'],0)
            self.assertEqual(history(path)[0]['id'],saved['id'])
            with self.assertRaises(KeyError):get_record(path,'missing')

    def test_csv_preserves_tie_and_neutralizes_formula_text(self):
        p=payload();p['model']['title']='=Unsafe';p['options']['minimum']=-2;p['assumptions']='@Hypothetical'
        r=run(p);r['id']='saved-version'
        rows=list(csv.DictReader(StringIO(build_csv(r).decode('utf-8-sig')),delimiter=';'))
        self.assertEqual(len(rows),101);self.assertEqual(rows[0]['pago'],'-2.0')
        self.assertEqual(rows[0]['caso'],"'=Unsafe");self.assertEqual(rows[0]['supuestos'],"'@Hypothetical")
        self.assertEqual(rows[75]['equilibrios_puros'],'1/2; 2/2')
        self.assertEqual(rows[-1]['version'],'saved-version')

    def test_invalid_assumptions(self):
        for value in ['',None,'x'*10001]:
            p=payload();p['assumptions']=value
            with self.assertRaises(ValueError):run(p)

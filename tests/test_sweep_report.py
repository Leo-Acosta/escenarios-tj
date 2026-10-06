import unittest
from io import BytesIO
from pypdf import PdfReader
from test_payoff_sweep import payload
from escenarios.payoff_sweep import run
from escenarios.sweep_report import build_pdf

class SweepReportTests(unittest.TestCase):
    def record(self):
        r=run(payload());r['id']='sweep-version-test';return r
    def test_pages_identity_range_and_tie(self):
        r=self.record();reader=PdfReader(BytesIO(build_pdf(r)))
        self.assertEqual(len(reader.pages),4)
        text=' '.join(p.extract_text() for p in reader.pages)
        for value in ['sweep-version-test','0 a 2','2 transiciones','Cooperar / Competir; Competir / Competir','no son umbrales exactos']:
            self.assertIn(value,text)
    def test_constant_negative_utilities_and_no_changes(self):
        r=self.record();r['changes']=[]
        for sample in r['points']:sample['values_a']=[-2,-2];sample['values_b']=[0,0]
        text=' '.join(p.extract_text() for p in PdfReader(BytesIO(build_pdf(r))).pages)
        self.assertIn('No se detectaron cambios',text);self.assertIn('-2',text)
    def test_literal_title_and_long_assumptions(self):
        r=self.record();r['model']['title']='Caso <b>literal</b>';r['assumptions']='Supuesto largo. '*500
        reader=PdfReader(BytesIO(build_pdf(r)))
        self.assertGreater(len(reader.pages),4)
        self.assertIn('<b>literal</b>',reader.pages[0].extract_text())

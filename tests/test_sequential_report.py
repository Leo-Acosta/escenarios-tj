import copy
import unittest
from io import BytesIO
from pypdf import PdfReader
from test_sequential import MODEL
from escenarios.sequential import analyze
from escenarios.simulation import simulate
from escenarios.sequential_report import build_pdf

class SequentialReportTests(unittest.TestCase):
    def record(self):
        r=analyze(MODEL);r['id']='version-test';return r
    def test_report_uses_saved_model_and_identifier(self):
        r=self.record();reader=PdfReader(BytesIO(build_pdf(r)))
        text=' '.join(page.extract_text() for page in reader.pages)
        self.assertIn('version-test',text);self.assertIn('Acomodar',text);self.assertIn('Hipotético',text)
        self.assertEqual(len(reader.pages),2)
    def test_simulation_is_included_with_its_seed_and_counts(self):
        r=self.record();r['simulation']=simulate(r['model'],{'iterations':100,'seed':42,'radius':0})
        reader=PdfReader(BytesIO(build_pdf(r)));text=' '.join(p.extract_text() for p in reader.pages)
        self.assertEqual(len(reader.pages),3)
        self.assertIn('semilla 42',text);self.assertIn('100 / 100',text);self.assertIn('100 %',text)
    def test_user_markup_is_literal_and_long_assumptions_paginate(self):
        r=self.record();r['model']['title']='Caso <b>literal</b> & revisión'
        r['model']['assumptions']='Supuesto de prueba. '*250
        reader=PdfReader(BytesIO(build_pdf(r)));text=' '.join(p.extract_text() for p in reader.pages)
        self.assertIn('<b>literal</b>',text);self.assertGreater(len(reader.pages),2)

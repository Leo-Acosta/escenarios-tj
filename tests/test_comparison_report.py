import unittest
from io import BytesIO
from pypdf import PdfReader
from test_comparisons import payload
from escenarios.comparisons import compare
from escenarios.comparison_report import build_pdf, summaries

class ComparisonReportTests(unittest.TestCase):
    def record(self):
        r=compare(payload());r['id']='comparison-test';return r
    def test_four_pages_and_saved_identity(self):
        r=self.record();reader=PdfReader(BytesIO(build_pdf(r)))
        self.assertEqual(len(reader.pages),4)
        text=' '.join(p.extract_text() for p in reader.pages)
        for value in ['comparison-test','42 a 44','Pagos hipotéticos','DE','no es un intervalo de confianza']:
            self.assertIn(value,text)
    def test_b_summary_uses_columns_and_own_payoffs(self):
        r=self.record()
        expected=[r['cells'][i*6+2]['statistics'][1]['mean'] for i in range(6)]
        summary=summaries(r,1)[2]
        self.assertEqual(summary['minimum'],min(expected));self.assertEqual(summary['maximum'],max(expected))
    def test_equal_and_negative_heatmap_and_literal_title(self):
        r=self.record();r['model']['title']='Caso <b>literal</b> & prueba'
        for c in r['cells']:
            for s in c['statistics']:s.update(mean=-2,std=0,min=-2,max=-2)
        text=' '.join(p.extract_text() for p in PdfReader(BytesIO(build_pdf(r))).pages)
        self.assertIn('<b>literal</b>',text);self.assertIn('-2',text)
    def test_long_assumptions_paginate(self):
        r=self.record();r['assumptions']='Supuesto largo. '*500
        self.assertGreater(len(PdfReader(BytesIO(build_pdf(r))).pages),4)

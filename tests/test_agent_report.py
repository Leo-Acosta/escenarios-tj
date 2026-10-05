import csv
import unittest
from io import BytesIO,StringIO
from pypdf import PdfReader
from test_agents import payload
from escenarios.agents import run,build_csv
from escenarios.agent_report import build_pdf

class AgentReportTests(unittest.TestCase):
    def record(self):
        p=payload();p['options']['rounds']=50;r=run(p);r['id']='agent-version-test';return r
    def test_pdf_preserves_saved_version_totals_and_policies(self):
        r=self.record();reader=PdfReader(BytesIO(build_pdf(r)));text=' '.join(p.extract_text() for p in reader.pages)
        self.assertEqual(len(reader.pages),3);self.assertIn('agent-version-test',text);self.assertIn('Copiar última alternativa rival',text)
        self.assertIn('49',text);self.assertIn('54',text);self.assertIn('semilla 42',text)
    def test_zero_trace_and_literal_markup_render(self):
        r=self.record();r['model']['title']='Caso <b>literal</b> & prueba'
        for row in r['rounds']:row['totals']=[0,0]
        text=' '.join(p.extract_text() for p in PdfReader(BytesIO(build_pdf(r))).pages)
        self.assertIn('<b>literal</b>',text)
    def test_long_assumptions_paginate(self):
        r=self.record();r['assumptions']='Supuesto de prueba. '*250
        self.assertGreater(len(PdfReader(BytesIO(build_pdf(r))).pages),3)
    def test_csv_contains_two_rows_per_round_and_memory(self):
        r=self.record();rows=list(csv.DictReader(StringIO(build_csv(r).decode('utf-8-sig')),delimiter=';'))
        self.assertEqual(len(rows),100);self.assertEqual(rows[2]['rondas_observadas'],'1')
        self.assertEqual(rows[-1]['acumulado'],'54');self.assertEqual(rows[0]['version'],'agent-version-test')
    def test_csv_formula_text_is_escaped_but_negative_payoffs_are_numeric(self):
        r=self.record();r['model']['title']='=HYPERLINK("bad")';r['rounds'][0]['payments'][0]=-2
        rows=list(csv.DictReader(StringIO(build_csv(r).decode('utf-8-sig')),delimiter=';'))
        self.assertTrue(rows[0]['caso'].startswith("'="));self.assertEqual(rows[0]['pago'],'-2')

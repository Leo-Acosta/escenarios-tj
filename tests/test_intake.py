import unittest
from unittest.mock import patch
from escenarios.intake import prepare


class IntakeTests(unittest.TestCase):
    def test_guided_mode_does_not_call_provider(self):
        with patch.dict('os.environ',{},clear=True),patch('escenarios.intake.urlopen') as remote:
            result=prepare('Negociación entre dos instituciones por una obra.')
            self.assertEqual(result['mode'],'guided')
            self.assertEqual(len(result['scenarios']),3)
            remote.assert_not_called()

    def test_invalid_prompt(self):
        for prompt in ['',None,'corto','x'*12001]:
            with self.assertRaises(ValueError):prepare(prompt)

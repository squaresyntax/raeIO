import types
import sys
import unittest

yaml_stub = types.ModuleType("yaml")
yaml_stub.safe_load = lambda x: {}
yaml_stub.dump = lambda data, f: None
sys.modules.setdefault("yaml", yaml_stub)

from energy_transformer_agent import GenerativeMediaManager

class TestModalConsistency(unittest.TestCase):
    def setUp(self):
        self.manager = GenerativeMediaManager(output_dir='test_outputs', consistency_threshold=0.9)

    def tearDown(self):
        import shutil
        shutil.rmtree('test_outputs', ignore_errors=True)

    def test_consistency_failure(self):
        with self.assertRaises(ValueError):
            self.manager.check_modal_consistency('a sunny day', 'a rainy night')

    def test_consistency_success(self):
        self.assertTrue(self.manager.check_modal_consistency('a sunny day', 'a sunny day'))

if __name__ == '__main__':
    unittest.main()

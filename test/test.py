import unittest
from ..src.forwarding.tests.test_graph import TestGraphFunctions
from ..src.forwarding.tests.test_path import TestPathFunctions
from ..src.forwarding.tests.test_solution import TestPathSolutionFunctions

if __name__ == '__main__':
    suite = unittest.TestSuite()
    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathSolutionFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGraphFunctions))
    unittest.TextTestRunner(verbosity=2).run(suite)

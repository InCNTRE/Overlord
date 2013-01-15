import unittest
#import TestGraph
#import TestMain
#import TestPath
from Forwarding.Tests.TestGraph import TestGraphFunctions
from Forwarding.Tests.TestPath import TestPathFunctions
from Forwarding.Tests.TestPathSolution import TestPathSolutionFunctions

if __name__ == '__main__':
    suite = unittest.TestSuite()
    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathSolutionFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGraphFunctions))
    unittest.TextTestRunner(verbosity=2).run(suite)

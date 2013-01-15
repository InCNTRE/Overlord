import unittest
#import TestGraph
#import TestMain
#import TestPath
from Forwarding.Tests.TestPathSolution import TestPathSolutionFunctions

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPathSolutionFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)

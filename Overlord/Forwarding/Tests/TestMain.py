import unittest
#import TestGraph
#import TestMain
#import TestPath
from Forwarding.tests.TestPathSolution import TestPathSolutionFunctions

suite = unittest.TestLoader().loadTestsFromTestCase(TestPathSolutionFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)

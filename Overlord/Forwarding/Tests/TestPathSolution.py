import unittest

from ..Graph import Switch
from ..PathSolution import dijkstra

class TestPathSolutionFunctions(unittest.TestCase):
    def setUp(self):
        self.tests = []

        # Graph Test 00
        graph = {}
        solution = {}
        self.tests.append( (graph, solution) )

        # Graph Test 01
        graph = {}
        graph["A"] = Switch("A")
        solution = {"A":-1}
        self.tests.append( (graph, solution) )

        # Graph Test 02
        graph = {}
        graph["A"] = Switch("A")
        graph["B"] = Switch("B")
        graph["C"] = Switch("C")
        graph["A"].add_link("B", 2)
        graph["B"].add_link("A", 1)
        graph["B"].add_link("C", 2)
        graph["C"].add_link("B", 1)
        solution = {"A":-1, "B":"A", "C":"B"}
        self.tests.append( (graph, solution) )

        # Graph Test 03
        graph = {}
        graph["A"] = Switch("A")
        graph["B"] = Switch("B")
        graph["C"] = Switch("C")
        graph["D"] = Switch("D")
        graph["A"].add_link("B", 2)
        graph["A"].add_link("D", 1)
        graph["B"].add_link("A", 1)
        graph["B"].add_link("C", 2)
        graph["C"].add_link("B", 1)
        graph["D"].add_link("A", 1)
        solution = {"A":-1, "B":"A", "C":"B", "D":"A"}
        self.tests.append( (graph, solution) )

    def test_dijkstra(self):
        for test in self.tests:
            pred = dijkstra(test[0], "A")
            self.assertEqual(pred, test[1])

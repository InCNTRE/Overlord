import unittest

from ..graph import Graph
from ..path import Path, PathNode
from ..solution import dijkstra

class TestGraphFunctions(unittest.TestCase):
    def setUp(self):
        g = Graph()
        g.add_switch("A")
        g.add_switch("B")
        g.add_switch("C")
        g.add_link("A", "B", 2)
        g.add_link("B", "A", 1)
        g.add_link("B", "C", 2)
        g.add_link("C", "B", 1)

        p = []
        a = PathNode("A", None, 2)
        b = PathNode("B", 1, 2)
        c = PathNode("C", 1, None)
        p.append(a)
        p.append(b)
        p.append(c)

        self.test_graph = g
        self.test_path = Path("A", "C", p)

    def test_new_path_nodes(self):
        pred = dijkstra(self.test_graph.get_switches(), "A")

        test_nodes = self.test_path.get_nodes()
        path_nodes = self.test_graph.new_path_nodes("A", "C", pred)
        self.assertEqual(test_nodes, path_nodes)

    def test_get_path(self):
        path = self.test_graph.get_path("A", "C")
        print(self.test_path)
        print(path)
        self.assertEqual(self.test_path, path)

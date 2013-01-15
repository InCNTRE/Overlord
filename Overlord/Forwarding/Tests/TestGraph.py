import unittest

from ..Graph import Graph
from ..Path import Path, PathNode
from ..PathSolution import dijkstra

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

        self.test_path = Path("A", "C", p)
        self.test_path.set_id(1)

        self.test_graph = g

    @unittest.skip("Not done")
    def test_get_path(self):
        code_path = self.test_graph.get_path("A", "B")
        self.assertEqual(self.test_path, code_path)

    def test_new_path_nodes(self):
        pred = dijkstra(self.test_graph.get_switches(), "A")
        print(pred)
        path_nodes = self.test_graph.new_path_nodes("A", "C", pred)

        self.assertEqual(self.test_path, path_nodes)

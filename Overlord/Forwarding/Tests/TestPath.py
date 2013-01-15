import unittest

from ..Path import Path, PathNode

class TestPathFunctions(unittest.TestCase):
    def setUp(self):
        p = []
        self.a = PathNode("A", None, 2)
        p.append(self.a)
        self.b = PathNode("B", 1, 2)
        p.append(self.b)
        self.c = PathNode("C", 1, None)
        p.append(self.c)
        self.path = Path("A", "C", p)
        self.path.set_id(99)
        self.path_id = 99

    def test_path_down(self):
        def down_handler(e):
            self.assertEquals(e.path_id, self.path_id)
            self.assertEquals(e.start, "A")
            self.assertEquals(e.end, "C")

        self.path.add_listener("path_down", down_handler)
        self.a.node_down()
        self.assertFalse(self.a.is_up())

    def test_path_up(self):
        def up_handler(e):
            self.assertEquals(e.path_id, self.path_id)
            self.assertEquals(e.start, "A")
            self.assertEquals(e.end, "C")

        self.a.node_down()
        self.assertFalse(self.a.is_up())
        self.a.node_up()
        self.path.add_listener("path_up", up_handler)
        self.assertTrue(self.a.is_up())

    def test_node_down(self):
        n = PathNode("A", None, 2)

        def handler(e):
            self.assertEquals(e.dpid, "A")

        n.add_listener("down", handler)
        n.node_down()
        self.assertFalse(n.is_up())

    def test_node_up(self):
        n = PathNode("B", 2, 3)

        def handler(e):
            self.assertEquals(e.dpid, "B")

        n.add_listener("up", handler)
        self.assertTrue(n.is_up())
        n.node_up()

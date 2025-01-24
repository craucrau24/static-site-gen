import unittest

from data.textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

        node = TextNode("This is a text node", TextType.BOLD, "http://foobar.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "http://foobar.com")
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, "http://foobar.com")
        self.assertNotEqual(node, node2)

        node = TextNode("This is a text node", TextType.BOLD, "http://foobar.com")
        node2 = TextNode("This is a text node", TextType.TEXT, "http://foobar.com")
        self.assertNotEqual(node, node2)

        node = TextNode("This is a text node", TextType.TEXT, "http://foobar.com")
        node2 = TextNode("This is not a text node", TextType.TEXT, "http://foobar.com")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()
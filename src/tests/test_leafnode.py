import unittest

from htmlnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_to_html(self):
        node = LeafNode("p", "this is a paragraph")
        self.assertEqual(node.to_html(), "<p>this is a paragraph</p>")

        node = LeafNode("span", "this is an inline text")
        self.assertEqual(node.to_html(), "<span>this is an inline text</span>")

        node = LeafNode(None, "this is a raw text")
        self.assertEqual(node.to_html(), "this is a raw text")

    def test_to_html_ko(self):
        with self.assertRaises(ValueError):
            node = LeafNode("p", None)
            node.to_html()

        with self.assertRaises(ValueError):
            node = LeafNode(None, None)
            node.to_html()
            
    def test_to_html_with_props(self):
        node = LeafNode("span", "this is an inline text", {"color": "darkgrey", "text-decoration": "underline"})
        self.assertEqual(node.to_html(), '<span color="darkgrey" text-decoration="underline">this is an inline text</span>')

        node = LeafNode("a", "this is a link", {"href": "http://foobar.com", "target": "_blank"})
        self.assertEqual(node.to_html(), '<a href="http://foobar.com" target="_blank">this is a link</a>')
        
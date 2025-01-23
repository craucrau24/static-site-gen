import unittest

from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode("p", "this is a paragraph", None, None)
        self.assertEqual(repr(node), "HTMLNode(p, this is a paragraph, None, None)")

        node = HTMLNode(None, "this is a text", None, None)
        self.assertEqual(repr(node), "HTMLNode(None, this is a text, None, None)")

        node = HTMLNode("div", "this is a text", [HTMLNode("p", "this is a nested paragraph")], None)
        self.assertEqual(repr(node), "HTMLNode(div, this is a text, [HTMLNode(p, this is a nested paragraph, None, None)], None)")

        node = HTMLNode("span", "this is a text", None, {"color": "blue", "font-weight": "bold"})
        self.assertEqual(repr(node), "HTMLNode(span, this is a text, None, {'color': 'blue', 'font-weight': 'bold'})")
    
    def test_props_to_html(self):
        node = HTMLNode("span", "this is a text", None, {"color": "blue", "font-weight": "bold"})
        self.assertEqual(node.props_to_html(), ' color="blue" font-weight="bold" ')

        node = HTMLNode("span", "this is a text", None, {"display": "inline-block", "margin": "10px"})
        self.assertEqual(node.props_to_html(), ' display="inline-block" margin="10px" ')

        node = HTMLNode("span", "this is a text", None, None)
        self.assertEqual(node.props_to_html(), "")

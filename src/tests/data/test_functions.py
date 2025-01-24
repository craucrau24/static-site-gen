import unittest

from data.functions import text_node_to_html_node, split_nodes_delimiter
from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode


class TestTextToHTMLNode(unittest.TestCase):
    def helper_test_leaf(self, html, tag, value, props=None):
        self.assertIsInstance(html, LeafNode)
        self.assertEqual(html.tag, tag)
        self.assertEqual(html.value, value)
        self.assertIs(html.children, None)
        self.assertEqual(html.props, props)

    def test_convert_text(self):
        node = TextNode("this is raw text", TextType.TEXT)
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, None, "this is raw text")

        node = TextNode("this is bold text", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "b", "this is bold text")

        node = TextNode("this is italic text", TextType.ITALIC)
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "i", "this is italic text")

        node = TextNode("this is code text", TextType.CODE)
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "code", "this is code text")

    def test_convert_with_url(self):
        node = TextNode("this is a link", TextType.LINK, "http://foobar.com/baz")
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "a", "this is a link", {"href": "http://foobar.com/baz"})

        node = TextNode("this is an image", TextType.IMAGE, "http://foobar.com/baz.png")
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "img", "", {"src": "http://foobar.com/baz.png", "alt": "this is an image"})

        node = TextNode(None, TextType.IMAGE, "http://foobar.com/baz.png")
        html = text_node_to_html_node(node)
        self.helper_test_leaf(html, "img", "", {"src": "http://foobar.com/baz.png"})

    def test_convert_ko(self):
        with self.assertRaisesRegex(ValueError, "invalid text type"):
            text_node_to_html_node(TextNode("empty text type", None))

        with self.assertRaisesRegex(ValueError, "invalid text type"):
            text_node_to_html_node(TextNode("wrong text type", "foobar"))

        with self.assertRaisesRegex(ValueError, "link needs a target url"):
            text_node_to_html_node(TextNode("link without url", TextType.LINK))

        with self.assertRaisesRegex(ValueError, "image needs a source url"):
            text_node_to_html_node(TextNode("image without url", TextType.IMAGE))

class TestSplitNodesDelimiter(unittest.TestCase):
    def helper_test_node_list(self, nodes, expected):
        self.assertEqual(len(nodes), len(expected))
        for node, exp in zip(nodes, expected):
            text, ttype = exp
            self.assertIsInstance(node, TextNode)
            self.assertEqual(node.text, text)
            self.assertEqual(node.text_type, ttype)

    def test_single(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" word", TextType.TEXT),
        ])

        node = TextNode("This is text with a *italic word*", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.helper_test_node_list(nodes, [
            ("This is bold text with a ", TextType.TEXT),
            ("italic word", TextType.ITALIC),
        ])

        node = TextNode("**Bold text** in a regular text", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.helper_test_node_list(nodes, [
            ("Bold text", TextType.BOLD),
            (" in a code block", TextType.TEXT),
        ])

        node = TextNode("There is **Bold text** next to *italic words*", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.helper_test_node_list(nodes, [
            ("There is ", TextType.TEXT),
            ("Bold text", TextType.BOLD),
            (" next to *italic words*", TextType.TEXT),
        ])
        nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.helper_test_node_list(nodes, [
            ("There is **Bold text** next to ", TextType.TEXT),
            ("italic words", TextType.ITALIC),
        ])
    
    def test_multi(self):
        text = "Begin with *italic* followed by `code block` and **bold** next to *italic* words"
        nodes = [
            TextNode("Begin with *italic* followed by ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and **bold** next to *italic* words", TextType.TEXT),
        ]
        res = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.helper_test_node_list(res, [
            ("Begin with ", TextType.TEXT),
            ("italic", TextType.ITALIC),
            (" followed by ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" and **bold** next to ", TextType.TEXT),
            ("italic", TextType.ITALIC),
            ("words", TextType.TEXT),
        ])

    def test_multicall(self):
        node = TextNode("There is **Bold text** next to *italic words*", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.helper_test_node_list(nodes, [
            ("There is ", TextType.TEXT),
            ("Bold text", TextType.BOLD),
            (" next to ", TextType.TEXT),
            ("italic words", TextType.ITALIC),
        ])
    
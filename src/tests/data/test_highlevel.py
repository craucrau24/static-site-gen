import unittest

from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode
from data.highlevel import text_to_textnodes, text_node_to_html_node
from .test_functions import MixinTestTextNodes

class MixinTestLeaf:
    def helper_test_leaf(self, html, tag, value, props=None):
        self.assertIsInstance(html, LeafNode)
        self.assertEqual(html.tag, tag)
        self.assertEqual(html.value, value)
        self.assertIs(html.children, None)
        self.assertEqual(html.props, props)

class TestTextToTextNodes(unittest.TestCase, MixinTestTextNodes):
    def test_ok(self):
        text = "This is **bold words** among normal words"
        nodes = text_to_textnodes(text)
        self.helper_test_node_list(nodes, [
            ("This is ", TextType.TEXT),
            ("bold words", TextType.BOLD),
            (" among normal words", TextType.TEXT),
        ])

        text = "This is **bold words** and *italic words* with normal words"
        nodes = text_to_textnodes(text)
        self.helper_test_node_list(nodes, [
            ("This is ", TextType.TEXT),
            ("bold words", TextType.BOLD),
            (" and ", TextType.TEXT),
            ("italic words", TextType.ITALIC),
            (" with normal words", TextType.TEXT),
        ])

        text = "This is a [link](https://foobar.com/baz) and *italic words* with normal words"
        nodes = text_to_textnodes(text)
        self.helper_test_node_list(nodes, [
            ("This is a ", TextType.TEXT),
            ("link", TextType.LINK, "https://foobar.com/baz"),
            (" and ", TextType.TEXT),
            ("italic words", TextType.ITALIC),
            (" with normal words", TextType.TEXT),
        ])

        text = "This is a [link](https://foobar.com/baz) and a ![dummy image](https://foobar.com/baz.jpeg)"
        nodes = text_to_textnodes(text)
        self.helper_test_node_list(nodes, [
            ("This is a ", TextType.TEXT),
            ("link", TextType.LINK, "https://foobar.com/baz"),
            (" and a ", TextType.TEXT),
            ("dummy image", TextType.IMAGE, "https://foobar.com/baz.jpeg"),
        ])

        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.helper_test_node_list(nodes, [
            ("This is ", TextType.TEXT),
            ("text", TextType.BOLD),
            (" with an ", TextType.TEXT),
            ("italic", TextType.ITALIC),
            (" word and a ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" and an ", TextType.TEXT),
            ("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            (" and a ", TextType.TEXT),
            ("link", TextType.LINK, "https://boot.dev"),
        ])

class TestTextToHTMLNode(unittest.TestCase, MixinTestLeaf):

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

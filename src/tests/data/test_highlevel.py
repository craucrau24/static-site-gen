import unittest

from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode, ParentNode
from data.highlevel import text_to_textnodes, text_node_to_html_node, markdown_to_html_node
from data.highlevel import process_paragraph, process_heading, process_code, process_quote, process_ordered_list, process_unordered_list
from data.blocks import block_to_block_type, BlockType

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

class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_ok(self):
        self.maxDiff = None
        text = "## This is a heading"
        expected = ParentNode("div", [ParentNode("h2", [LeafNode(None, "This is a heading")])])
        self.assertEqual(markdown_to_html_node(text), expected)

        text = """# This is a heading

        First paragraph with **bold text** and *italic* word
        """
        expected = ParentNode("div", [
            ParentNode("h1", [LeafNode(None, "This is a heading")]),
            ParentNode("p", [LeafNode(None, "First paragraph with "), LeafNode("b", "bold text"), LeafNode(None, " and "), LeafNode("i", "italic"), LeafNode(None, " word")])])
        self.assertEqual(markdown_to_html_node(text), expected)

        text = """# This is a heading

        First paragraph with **bold text** and *italic* word

        Second paragraph with `code sample`

>I must say
>I would be very impressed
>if it works!

        ## This is a second heading

* First line
* Second *line*

        """
        expected = ParentNode("div", [
            ParentNode("h1", [LeafNode(None, "This is a heading")]),
            ParentNode("p", [LeafNode(None, "First paragraph with "), LeafNode("b", "bold text"), LeafNode(None, " and "), LeafNode("i", "italic"), LeafNode(None, " word")]),
            ParentNode("p", [LeafNode(None, "Second paragraph with "), LeafNode("code", "code sample")]),
            ParentNode("blockquote", [LeafNode(None, "I must say\nI would be very impressed\nif it works!")]),
            ParentNode("h2", [LeafNode(None, "This is a second heading")]),
            ParentNode("ul", [ParentNode("li", [LeafNode(None, "First line")]), ParentNode("li", [LeafNode(None, "Second "), LeafNode("i", "line")])])
        ])
        self.assertEqual(markdown_to_html_node(text), expected)

        text = """# This is a heading

[link](https://foobar.com/baz)
![image](https://foobar.com/baz.png)

```
def dummy_function():
    print('Hello, world!')
```

        #### This is a second heading

1. First line
2. Second **line**

        """
        expected = ParentNode("div", [
            ParentNode("h1", [LeafNode(None, "This is a heading")]),
            ParentNode("p", [LeafNode("a", "link", {"href": "https://foobar.com/baz"}), LeafNode("img", "", {"src": "https://foobar.com/baz.png", "alt": "image"})]),
            ParentNode("pre", [LeafNode("code", "\ndef dummy_function():\n    print('Hello, world!')\n")]),
            ParentNode("h4", [LeafNode(None, "This is a second heading")]),
            ParentNode("ol", [ParentNode("li", [LeafNode(None, "First line")]), ParentNode("li", [LeafNode(None, "Second "), LeafNode("b", "line")])])
        ])
        self.assertEqual(markdown_to_html_node(text), expected)

    def test_illformed(self):
        text = "####### toto\n\n* blabla\n- blibli"
        expected = ParentNode("div", [
            ParentNode("p", [LeafNode(None, "####### toto")]),
            ParentNode("p", [LeafNode(None, "* blabla\n- blibli")]),
        ])
        self.assertEqual(markdown_to_html_node(text), expected)
    
    def test_process_paragraph(self):
        text = "This is a text with **bold words** and *italic* word"
        expected = ParentNode("p", [LeafNode(None, "This is a text with "), LeafNode("b", "bold words"), LeafNode(None, " and "), LeafNode("i", "italic"), LeafNode(None, " word")])
        self.assertEqual(block_to_block_type(text), BlockType.PARAGRAPH)
        self.assertEqual(process_paragraph(text), expected)

    def test_process_quote(self):
        text = ">I must say\n>I would be impressed\n>if it works"
        expected = ParentNode("blockquote", [LeafNode(None, "I must say\nI would be impressed\nif it works")])
        self.assertEqual(block_to_block_type(text), BlockType.QUOTE)
        self.assertEqual(process_quote(text), expected)
    
    def test_process_heading(self):
        text = "### This is a 3rd level heading"
        expected = ParentNode("h3", [LeafNode(None, "This is a 3rd level heading")])
        self.assertEqual(block_to_block_type(text), BlockType.HEADING)
        self.assertEqual(process_heading(text), expected)
    
    def test_process_code(self):
        text = "```\ndef dummy():\n    print('Dummy!')\n```"
        expected = ParentNode("pre", [LeafNode("code", "\ndef dummy():\n    print('Dummy!')\n")])
        self.assertEqual(block_to_block_type(text), BlockType.CODE)
        self.assertEqual(process_code(text), expected)
    
    def test_process_unordered(self):
        text = "- First line\n- Second **line**"
        expected = ParentNode("ul", [ParentNode("li", [LeafNode(None, "First line")]), ParentNode("li", [LeafNode(None, "Second "), LeafNode("b", "line")])])
        self.assertEqual(block_to_block_type(text), BlockType.UNORDERED_LIST)
        self.assertEqual(process_unordered_list(text), expected)
    
    def test_process_ordered(self):
        text = "1. First line\n2. Second **line**"
        expected = ParentNode("ol", [ParentNode("li", [LeafNode(None, "First line")]), ParentNode("li", [LeafNode(None, "Second "), LeafNode("b", "line")])])
        self.assertEqual(block_to_block_type(text), BlockType.ORDERED_LIST)
        self.assertEqual(process_ordered_list(text), expected)
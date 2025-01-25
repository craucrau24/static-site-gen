import unittest
import re

from data.functions import text_node_to_html_node, split_nodes_delimiter, split_node_delimiter, strip_empty_node, extract_markdown_images, extract_markdown_links, split_nodes_images, split_nodes_links
from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode

class MixinTestLeaf:
    def helper_test_leaf(self, html, tag, value, props=None):
        self.assertIsInstance(html, LeafNode)
        self.assertEqual(html.tag, tag)
        self.assertEqual(html.value, value)
        self.assertIs(html.children, None)
        self.assertEqual(html.props, props)

class MixinTestTextNodes:
    def helper_test_node_list(self, nodes, expected):
        self.assertEqual(len(nodes), len(expected))
        for node, exp in zip(nodes, expected):
            try:
                text, ttype, url = exp
            except ValueError:
                text, ttype = exp
                url = None

            self.assertIsInstance(node, TextNode)
            self.assertEqual(node.text, text)
            self.assertEqual(node.text_type, ttype)
            self.assertEqual(node.url, url)


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

class TestSplitNodesDelimiter(unittest.TestCase, MixinTestTextNodes):
    def helper_test_single_with_func(self, func):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        nodes = func(node, "`", TextType.CODE)
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" word", TextType.TEXT),
        ])

        node = TextNode("This is text with a *italic word*", TextType.TEXT)
        nodes = func(node, "*", TextType.ITALIC)
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("italic word", TextType.ITALIC),
        ])

        node = TextNode("**Bold text** in a regular text", TextType.TEXT)
        nodes = func(node, "**", TextType.BOLD)
        self.helper_test_node_list(nodes, [
            ("Bold text", TextType.BOLD),
            (" in a regular text", TextType.TEXT),
        ])

        node = TextNode("There is `code block` next to *italic words*", TextType.TEXT)
        nodes = func(node, "`", TextType.CODE)
        self.helper_test_node_list(nodes, [
            ("There is ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" next to *italic words*", TextType.TEXT),
        ])
        nodes = func(node, "*", TextType.ITALIC)
        self.helper_test_node_list(nodes, [
            ("There is `code block` next to ", TextType.TEXT),
            ("italic words", TextType.ITALIC),
        ])

    def test_trim_empty_nodes(self):
        nodes = [
            TextNode("This is bold text with a ", TextType.TEXT),
            TextNode("italic word", TextType.ITALIC),
            TextNode("", TextType.TEXT),
        ]
        self.assertEqual(strip_empty_node(nodes, TextType.BOLD), nodes[:-1])
        self.assertEqual(strip_empty_node(nodes, TextType.TEXT), nodes)

        nodes = [
            TextNode("", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode(" in a code block", TextType.TEXT),
        ]
        self.assertEqual(strip_empty_node(nodes, TextType.BOLD), nodes[1:])
        self.assertEqual(strip_empty_node(nodes, TextType.TEXT), nodes)

        nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]

        for ttype in (TextType.BOLD, TextType.CODE, TextType.ITALIC, TextType.TEXT):
            self.assertEqual(strip_empty_node(nodes, ttype), nodes)

        nodes = [
            TextNode("", TextType.TEXT),
        ]
        for ttype in (TextType.BOLD, TextType.CODE, TextType.ITALIC, TextType.TEXT):
            self.assertEqual(strip_empty_node(nodes, ttype), nodes)

    def test_nodes_single(self):
        split_nodes = lambda n, d, tt: split_nodes_delimiter([n], d, tt)
        self.helper_test_single_with_func(split_nodes)

    def test_node_single(self):
        split_node = lambda n, d, tt: split_node_delimiter(n, d, tt)
        self.helper_test_single_with_func(split_node)


    def test_node_single_ko(self):
        node = TextNode("This is text with a *italic word*", TextType.ITALIC)
        with self.assertRaisesRegex(ValueError, "cannot split text node with the same text type"):
            split_node_delimiter(node, "*", TextType.ITALIC)

    
    def test_multi(self):
        nodes = [
            TextNode("Begin with **bold** followed by ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and **bold** next to *italic* words", TextType.TEXT),
        ]
        res = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.helper_test_node_list(res, [
            ("Begin with ", TextType.TEXT),
            ("bold", TextType.BOLD),
            (" followed by ", TextType.TEXT),
            ("code block", TextType.CODE),
            (" and ", TextType.TEXT),
            ("bold", TextType.BOLD),
            (" next to *italic* words", TextType.TEXT),
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
    

class TestExtractMarkdown(unittest.TestCase, MixinTestTextNodes):
    def test_extract_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(extract_markdown_images(text), [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

        text = "This is text with a ![foobar](https://foobar.com/baz.png), that's all folks!"
        self.assertEqual(extract_markdown_images(text), [("foobar", "https://foobar.com/baz.png")])

        text = "This is text with no image"
        self.assertEqual(extract_markdown_images(text), [])

    def test_extract_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(extract_markdown_links(text), [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

        text = "This is text with a link [to foobar](https://foobar.com) and that's all."
        self.assertEqual(extract_markdown_links(text), [("to foobar", "https://foobar.com")])

        text = "This is text with no link"
        self.assertEqual(extract_markdown_links(text), [])
    
    def test_extract_links_with_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(extract_markdown_links(text), [])

        text = "This is text with a ![foobar](https://foobar.com/baz.png), that's all folks!"
        self.assertEqual(extract_markdown_links(text), [])

        text = "This is text with no image"
        self.assertEqual(extract_markdown_links(text), [])

    def test_split_nodes_images(self):
        node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", TextType.TEXT)
        nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            (" and ", TextType.TEXT),
            ("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ])

        node = TextNode("This is text with a ![foobar](https://foobar.com/baz.png), that's all folks!", TextType.TEXT)
        nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("foobar", TextType.IMAGE, "https://foobar.com/baz.png"),
            (", that's all folks!", TextType.TEXT),
        ])

        node = TextNode("![rick roll](https://i.imgur.com/aKaOqIh.gif) is a picture at beginning", TextType.TEXT)
        nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            (" is a picture at beginning", TextType.TEXT),
        ])

        node = TextNode("Warning: picture at end ![rick roll](https://i.imgur.com/aKaOqIh.gif)", TextType.TEXT)
        nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("Warning: picture at end ", TextType.TEXT),
            ("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
        ])

    def test_split_nodes_images_other_types(self):
        for ttype in [TextType.BOLD, TextType.CODE, TextType.ITALIC, TextType.IMAGE, TextType.LINK]:
            node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", ttype)
            nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", ttype)
        ])

        nodes = [
            TextNode("This is a bold text", TextType.BOLD),
            TextNode("![rick roll](https://i.imgur.com/aKaOqIh.gif) is a picture at beginning", TextType.TEXT),
            TextNode("This is an unsupported italic text with embedded ![foobar](https://foobar.com/baz.jpeg) image", TextType.ITALIC),
        ]
        nodes = split_nodes_images(nodes)
        self.helper_test_node_list(nodes, [
            ("This is a bold text", TextType.BOLD),
            ("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            (" is a picture at beginning", TextType.TEXT),
            ("This is an unsupported italic text with embedded ![foobar](https://foobar.com/baz.jpeg) image", TextType.ITALIC),
        ])


    def test_split_nodes_links(self):
        node = TextNode("This is text with a [foobar](https://foobar.com/baz) and [to google](https://google.com)", TextType.TEXT)
        nodes = split_nodes_links([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("foobar", TextType.LINK, "https://foobar.com/baz"),
            (" and ", TextType.TEXT),
            ("to google", TextType.LINK, "https://google.com"),
        ])

        node = TextNode("This is text with a [foobar](https://foobar.com/baz), that's all folks!", TextType.TEXT)
        nodes = split_nodes_links([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ", TextType.TEXT),
            ("foobar", TextType.LINK, "https://foobar.com/baz"),
            (", that's all folks!", TextType.TEXT),
        ])

        node = TextNode("[to google](https://google.com) is a link at beginning", TextType.TEXT)
        nodes = split_nodes_links([node])
        self.helper_test_node_list(nodes, [
            ("to google", TextType.LINK, "https://google.com"),
            (" is a link at beginning", TextType.TEXT),
        ])

        node = TextNode("Warning: link at end [to google](https://google.com)", TextType.TEXT)
        nodes = split_nodes_links([node])
        self.helper_test_node_list(nodes, [
            ("Warning: link at end ", TextType.TEXT),
            ("to google", TextType.LINK, "https://google.com"),
        ])

    def test_split_nodes_links_other_types(self):
        for ttype in [TextType.BOLD, TextType.CODE, TextType.ITALIC, TextType.IMAGE, TextType.LINK]:
            node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", ttype)
            nodes = split_nodes_images([node])
        self.helper_test_node_list(nodes, [
            ("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", ttype)
        ])

        nodes = [
            TextNode("This is a bold text", TextType.BOLD),
            TextNode("![rick roll](https://i.imgur.com/aKaOqIh.gif) is a picture at beginning", TextType.TEXT),
            TextNode("This is an unsupported italic text with embedded ![foobar](https://foobar.com/baz.jpeg) image", TextType.ITALIC),
        ]
        nodes = split_nodes_images(nodes)
        self.helper_test_node_list(nodes, [
            ("This is a bold text", TextType.BOLD),
            ("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            (" is a picture at beginning", TextType.TEXT),
            ("This is an unsupported italic text with embedded ![foobar](https://foobar.com/baz.jpeg) image", TextType.ITALIC),
        ])


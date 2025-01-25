import unittest
import re
from unittest.mock import MagicMock, call

from data.functions import text_node_to_html_node, split_nodes_delimiter, split_node_delimiter, strip_empty_node, split_result_mkparser
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
    
class TestExtractMarkdown(unittest.TestCase):
    @unittest.skip("to be updated")
    def test_extract_markdown_with_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(extract_markdown_images(text), [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

        text = "This is text with a ![foobar](https://foobar.com/baz.png), that's all folks!"
        self.assertEqual(extract_markdown_images(text), [("foobar", "https://foobar.com/baz.png")])

        text = "This is text with no image"
        self.assertEqual(extract_markdown_images(text), [])

    def helper_test_split_result(self, calls1, calls2, calls, splits):
        fn1 = MagicMock()
        fn2 = MagicMock()
        fnall = MagicMock()
        parser = split_result_mkparser(2, fn1, fn2)
        parser(splits)
        fn1.assert_has_calls(calls1)
        fn2.assert_has_calls(calls2)
        parser = split_result_mkparser(2, fnall, fnall)
        parser(splits)
        fnall.assert_has_calls(calls)

    def test_split_result_mkparser(self):
        regex = r"(\d+)-(\d+)"
        text = "... 4-67 toto 4"
        calls1 = [call("... "), call(" toto 4")]
        calls2 = [call("4", "67")]
        calls = [call("... "), call("4", "67"), call(" toto 4")]
        self.helper_test_split_result(calls1, calls2, calls, re.split(regex, text))
        text = "12-432 toto 4 3-56aa d"
        calls1 = [call(" toto 4 "), call("aa d")]
        calls2 = [call("12", "432"), call("3", "56")]
        calls = [call("12", "432"), call(" toto 4 "), call("3", "56"), call("aa d")]
        self.helper_test_split_result(calls1, calls2, calls, re.split(regex, text))
        text = "12-432 toto 4 3-56aa d 45-321"
        calls1 = [call(" toto 4 "), call("aa d ")]
        calls2 = [call("12", "432"), call("3", "56"), call("45", "321")]
        calls = [call("12", "432"), call(" toto 4 "), call("3", "56"), call("aa d " ), call("45", "321")]
        self.helper_test_split_result(calls1, calls2, calls, re.split(regex, text))

        text = "toto 4 3-56aa d 45-321"
        calls1 = [call("toto 4 "), call("aa d ")]
        calls2 = [call("3", "56"), call("45", "321")]
        calls = [call("toto 4 "), call("3", "56"), call("aa d " ), call("45", "321")]
        self.helper_test_split_result(calls1, calls2, calls, re.split(regex, text))

    @unittest.skip("to be updated")
    def test_extract_markdown_with_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(extract_markdown_links(text), [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

        text = "This is text with a link [to foobar](https://foobar.com) and that's all."
        self.assertEqual(extract_markdown_links(text), [("to foobar", "https://foobar.com")])

        text = "This is text with no link"
        self.assertEqual(extract_markdown_links(text), [])
    
    @unittest.skip("to be updated")
    def test_extract_markdown_interleaved(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(extract_markdown_links(text), [])

        text = "This is text with a ![foobar](https://foobar.com/baz.png), that's all folks!"
        self.assertEqual(extract_markdown_links(text), [])

        text = "This is text with no image"
        self.assertEqual(extract_markdown_links(text), [])
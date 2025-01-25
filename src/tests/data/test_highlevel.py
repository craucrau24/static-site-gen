import unittest

from data.textnode import TextNode, TextType
from data.highlevel import text_to_textnodes
from .test_functions import MixinTestTextNodes

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
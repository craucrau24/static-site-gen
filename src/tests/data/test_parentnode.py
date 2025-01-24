import unittest
from data.htmlnode import ParentNode, LeafNode

class TestParentNode(unittest.TestCase):
    def test_to_html(self):
        node = ParentNode("div", [LeafNode("strong", "this is a strong text")])
        self.assertEqual(node.to_html(), "<div><strong>this is a strong text</strong></div>")

        node = ParentNode("div", [LeafNode(None, "raw text"), LeafNode("strong", "this is a strong text")])
        self.assertEqual(node.to_html(), "<div>raw text<strong>this is a strong text</strong></div>")

        node = ParentNode("ul", [ParentNode("li", [LeafNode(None, "raw text"), LeafNode("strong", "this is a strong text")]),
                                 LeafNode("li", "this is a sample text"),
                                 ParentNode("li", [LeafNode("span", "this is an inline text")])
                                 ])
        self.assertEqual(node.to_html(), "<ul><li>raw text<strong>this is a strong text</strong></li><li>this is a sample text</li><li><span>this is an inline text</span></li></ul>")

    def test_to_html_with_props(self):
        node = ParentNode("div", [LeafNode(None, "raw text"), LeafNode("strong", "this is a strong text")], {"class": "flex flex-row", "style": "margin: 10px;"})
        self.assertEqual(node.to_html(), '<div class="flex flex-row" style="margin: 10px;">raw text<strong>this is a strong text</strong></div>')

        node = ParentNode("ul", [ParentNode("li", [LeafNode(None, "raw text"), LeafNode("strong", "this is a strong text", {"id": "strongTxt"})]),
                                 LeafNode("li", "this is a sample text"),
                                 ParentNode("li", [LeafNode("span", "this is an inline text", {"class": "underline"})])
                                 ],
                                 {"class": "bg-teal-700"}
                                )
        self.assertEqual(node.to_html(), '<ul class="bg-teal-700"><li>raw text<strong id="strongTxt">this is a strong text</strong></li><li>this is a sample text</li><li><span class="underline">this is an inline text</span></li></ul>')

    def test_to_html_boot_dev(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")


    def test_to_html_ko(self):
        with self.assertRaisesRegex(ValueError, "ParentNode needs a tag"):
            node = ParentNode(None, [LeafNode(None, "foobar")])
            node.to_html()

        with self.assertRaisesRegex(ValueError, "ParentNode needs at least one child"):
            node = ParentNode("p", [])
            node.to_html()

        with self.assertRaisesRegex(ValueError, "ParentNode needs at least one child"):
            node = ParentNode("p", None)
            node.to_html()

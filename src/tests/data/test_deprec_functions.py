import unittest

from data.functions import extract_markdown_images, extract_markdown_links

@unittest.skip("unused functions")
class TestExtractMarkdown(unittest.TestCase):
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
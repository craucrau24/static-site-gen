import unittest

from data.functions import markdown_to_blocks

class TestMarkdownToBlocks(unittest.TestCase):
    def test_ok(self):
        text = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item
"""
        self.assertEqual(markdown_to_blocks(text), [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
            "* This is the first list item in a list block\n* This is a list item\n* This is another list item"
        ])

        text = """# This is a heading      

   \t This is a paragraph of text. It has some **bold** and *italic* words inside of it.  """

        self.assertEqual(markdown_to_blocks(text), [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
        ])

        text = """# This is a heading


This is a paragraph of text. It has some **bold** and *italic* words inside of it.





* This is the first list item in a list block
* This is a list item
* This is another list item
"""
        self.assertEqual(markdown_to_blocks(text), [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
            "* This is the first list item in a list block\n* This is a list item\n* This is another list item"
        ])
import unittest

from data.blocks import markdown_to_blocks, block_to_block_type, BlockType

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

class TestBlockToBlockType(unittest.TestCase):
    def test_ok(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        block = "#### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        block = "This is a paragraph of text. It has some **bold** and *italic* words inside of it."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

        block = "```def dummy_func():\n    print('dummy')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

        block = "> I must say\n> I am very impressed!"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

        block = "* This is the first list item in a list block\n* This is a list item\n* This is another list item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

        block = "- This is the first list item in a list block\n- This is a list item\n- This is another list item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

        block = "1. This is the first list item in a list block\n2. This is a list item\n3. This is another list item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_illformed(self):
        blocks = [
            "####### This is not a heading",
            "############# This is not a heading",
            "This is not a ## heading",
            "def dummy_func():\n    print('dummy')\n```",
            "```def dummy_func():\n    print('dummy')",
            "```def dummy_func():\n    print('dummy')\n``",
            "``def dummy_func():\n    print('dummy')\n```",
            "``def dummy_func():\n    print('dummy')\n``",
            "> I must say\n I am very impressed!\n>Well not so...",
            "* This is the first list item in a list block\n- This is a list item\n* This is another list item",
            "* This is the first list item in a list block\n*This is a list item\n* This is another list item",
            "- This is the first list item in a list block\n* This is a list item\n- This is another list item",
            "- This is the first list item in a list block\n-This is a list item\n- This is another list item",
            "1. This is the first list item in a list block\n3. This is a list item\n3. This is another list item",
            "0. This is the first list item in a list block\n1. This is a list item\n2. This is another list item",
            "2. This is the first list item in a list block\n3. This is a list item\n4. This is another list item",
            "1. This is the first list item in a list block\n2. This is a list item\n1. This is another list item",
            "1. This is the first list item in a list block\n2.This is a list item\n3. This is another list item",
        ]

        for block in blocks:
            self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

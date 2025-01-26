from enum import Enum
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ORDERED_LIST = "ordered list"
    UNORDERED_LIST = "unordered list"

def markdown_to_blocks(text):
    blocks = text.split("\n\n")
    return list(
        filter(
            lambda s: len(s) != 0,
            map(lambda s: s.strip(), blocks)
        ))

def line_starts_with_prefix(pre):
    def process(line):
        return line.startswith(pre)
    return process

def line_starts_with_successive_numbers():
    idx = 0
    def process(line):
        nonlocal idx
        idx += 1
        return line.startswith(f"{idx}. ")
    return process

def block_to_block_type(block):
    if re.search(r"^#{1,6} ", block) is not None:
        return BlockType.HEADING
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    lines = block.splitlines()
    if all(map(line_starts_with_prefix(">"), lines)):
        return BlockType.QUOTE
    if all(map(line_starts_with_prefix("* "), lines)) or all(map(line_starts_with_prefix("- "), lines)):
        return BlockType.UNORDERED_LIST
    if all(map(line_starts_with_successive_numbers(), lines)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

    

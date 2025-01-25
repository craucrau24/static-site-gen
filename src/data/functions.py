from data.htmlnode import LeafNode
from data.textnode import TextNode, TextType

from functools import reduce
from itertools import islice
from operator import add
import re

from string import Template

###########################################################
####          INLINE ELEMENTS CONVERSION           ########
###########################################################
def strip_empty_node(nodes, ttype):
    if len(nodes) <= 1:
        return nodes

    start = 0
    end = len(nodes)
    if nodes[start].text == "" and nodes[start].text_type != ttype:
        start += 1

    if nodes[end - 1].text == "" and nodes[end - 1].text_type != ttype:
        end -= 1

    return nodes[start:end]

def split_node_delimiter(node, delimiter, text_type):
    if node.text_type == text_type:
        raise ValueError("cannot split text node with the same text type")

    parts = node.text.split(delimiter)
    types = [node.text_type, text_type]

    def append_node(acc, txt):
        ttype = types.pop(0)
        types.append(ttype)
        acc.append(TextNode(txt, ttype))

        return acc

    return strip_empty_node(list(reduce(append_node, parts, [])), text_type)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    return list(reduce(add, map(lambda n: split_node_delimiter(n, delimiter, text_type), old_nodes)))

def extract_markdown_images(text):
    regex = r"!\[(.*?)\]\((.*?)\)"
    return  re.findall(regex, text)

def extract_markdown_links(text):
    regex = r"(?<!!)\[(.*?)\]\((.*?)\)"
    return  re.findall(regex, text)

def make_split_nodes_link_node(extract_markdown, text_type, template_string):
    template = Template(template_string)

    def process(nodes, current=None):
        if len(nodes) == 0:
            return []
        if current is None:
            if nodes[0].text_type != TextType.TEXT:
                return [nodes[0]] + process(nodes[1:])
            current = extract_markdown(nodes[0].text), nodes[0].text
        
        md_items, remainder = current
        if len(md_items) == 0:
            if remainder != "":
                head = [TextNode(remainder, TextType.TEXT)]
            else:
                head = []
            return head + process(nodes[1:])

        pattern = template.substitute(text=md_items[0][0], url=md_items[0][1])
        head, tail = remainder.split(pattern, maxsplit=1)
        if head != "":
            head = [TextNode(head, TextType.TEXT)]
        else:
            head = []
        head.append(TextNode(md_items[0][0], text_type, md_items[0][1]))
        return head + process(nodes, (md_items[1:], tail))
    return process

split_nodes_images = make_split_nodes_link_node(extract_markdown_images, TextType.IMAGE, "![$text]($url)")
split_nodes_links = make_split_nodes_link_node(extract_markdown_links, TextType.LINK, "[$text]($url)")

###########################################################
####           BLOCK ELEMENTS CONVERSION           ########
###########################################################

def markdown_to_blocks(text):
    blocks = text.split("\n\n")
    return list(
        filter(
            lambda s: len(s) != 0,
            map(lambda s: s.strip(), blocks)
        ))
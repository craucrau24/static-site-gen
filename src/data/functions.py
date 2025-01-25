from data.htmlnode import LeafNode
from data.textnode import TextNode, TextType

from functools import reduce
from operator import add
import re
from itertools import islice

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        
        case TextType.BOLD:
            return LeafNode("b", text_node.text)

        case TextType.ITALIC:
            return LeafNode("i", text_node.text)

        case TextType.CODE:
            return LeafNode("code", text_node.text)

        case TextType.LINK:
            if text_node.url is None:
                raise ValueError("link needs a target url")

            return LeafNode("a", text_node.text, {"href": text_node.url})

        case TextType.IMAGE:
            if text_node.url is None:
                raise ValueError("image needs a source url")

            props = {"src": text_node.url}
            if text_node.text is not None:
                props["alt"] = text_node.text

            return LeafNode("img", "", props)

        case _:
            raise ValueError("invalid text type")

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

def split_result_mkparser(nb_groups, fn_inter, fn_match):
    def fn_odd(splits):
        txt = next(splits)
        if txt != "":
            fn_inter(txt)

    def fn_even(splits):
        args = list(islice(splits, 0, nb_groups))
        if len(args) == 0:
            raise StopIteration
        fn_match(*args)

    funcs = [fn_odd, fn_even]

    def parser(splits):
        it = iter(splits)
        try:
            while 1:
                func = funcs.pop(0)
                funcs.append(func)
                func(it)
        except StopIteration:
            pass

    return parser

def imlink_to_text_node(imlink):
    pass
from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode, ParentNode
from data.functions import split_nodes_delimiter, split_nodes_images, split_nodes_links
from data.blocks import BlockType, block_to_block_type, markdown_to_blocks

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    text_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    text_nodes = split_nodes_delimiter(text_nodes, "*", TextType.ITALIC)
    text_nodes = split_nodes_delimiter(text_nodes, "`", TextType.CODE)
    text_nodes = split_nodes_images(text_nodes)
    return list(filter(lambda n: n.text.strip() != "", split_nodes_links(text_nodes)))

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

def process_paragraph(block):
    return ParentNode("p", list(map(text_node_to_html_node, text_to_textnodes(block) )))

def process_heading(block):
    head, tail = block.split(" ", maxsplit=1)
    return ParentNode(f"h{len(head)}", [LeafNode(None, tail)])

def process_code(block):
    return ParentNode("pre", [LeafNode("code", block[3:-3])])

def process_quote(block):
    lines = "\n".join(map(lambda line: line[1:], block.splitlines()))
    return ParentNode("blockquote", [LeafNode(None, lines)])

def process_list_data(block):
    lines = block.splitlines()
    return list(
        map(
            lambda line: ParentNode("li", list(map(text_node_to_html_node, text_to_textnodes(line.split(" ", maxsplit=1)[1])))),
            lines
        )
    )

def process_unordered_list(block):
    return ParentNode("ul", process_list_data(block))

def process_ordered_list(block):
    return ParentNode("ol", process_list_data(block))

def process_block(block):
    block_processors = {
        BlockType.PARAGRAPH: process_paragraph,
        BlockType.HEADING: process_heading,
        BlockType.CODE: process_code,
        BlockType.QUOTE: process_quote,
        BlockType.UNORDERED_LIST: process_unordered_list,
        BlockType.ORDERED_LIST: process_ordered_list,
    }

    try:
        func = block_processors[block_to_block_type(block)]
    except KeyError:
        raise Exception("unexpected block type")
    return func(block)

def markdown_to_html_node(text):
    blocks = markdown_to_blocks(text)
    children = list(map(process_block, blocks))
    return ParentNode("div", children)
from data.textnode import TextNode, TextType
from data.htmlnode import LeafNode
from data.functions import split_nodes_delimiter, split_nodes_images, split_nodes_links

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    text_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    text_nodes = split_nodes_delimiter(text_nodes, "*", TextType.ITALIC)
    text_nodes = split_nodes_delimiter(text_nodes, "`", TextType.CODE)
    text_nodes = split_nodes_images(text_nodes)
    return split_nodes_links(text_nodes)

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

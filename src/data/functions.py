from data.htmlnode import LeafNode
from data.textnode import TextNode, TextType

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

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    return [
        TextNode("This is text with a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" word", TextType.TEXT),
    ]
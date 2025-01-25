from data.textnode import TextNode, TextType
from data.functions import split_nodes_delimiter, split_nodes_images, split_nodes_links

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    text_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    text_nodes = split_nodes_delimiter(text_nodes, "*", TextType.ITALIC)
    text_nodes = split_nodes_delimiter(text_nodes, "`", TextType.CODE)
    text_nodes = split_nodes_images(text_nodes)
    return split_nodes_links(text_nodes)
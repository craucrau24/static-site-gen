class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is None:
            return ""

        props_str = " ".join(
            map(
                lambda t: f'{t[0]}="{t[1]}"',
                self.props.items()
                )
            )
        return " " + props_str + " "

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
    def __eq__(self, rhs):
        return (
            self.tag == rhs.tag and
            self.value == rhs.value and
            self.children == rhs.children and
            self.props == rhs.props
        )

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("VLeafNode needs a value")

        if self.tag is None:
            return self.value

        props = self.props_to_html().rstrip()

        return f"<{self.tag}{props}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode needs a tag")

        if self.children is None or self.children == []:
            raise ValueError("ParentNode needs at least one child")

        children = "".join(map(lambda nd: nd.to_html(), self.children))

        props = self.props_to_html().rstrip()

        return f"<{self.tag}{props}>{children}</{self.tag}>"
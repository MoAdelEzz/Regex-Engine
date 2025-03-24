from __future__ import annotations
from lexer import Lexer

node_id = 0
class Node:
    id: int
    start: int
    end: int
    val_range: tuple
    def __init__(self, val_range: tuple):
        global node_id
        node_id += 1
        self.id = node_id
        self.val_range = val_range

    def type(self):
        return self.__class__.__name__
    
    def get_value(self):
        start = self.val_range[0]
        end = self.val_range[1]
        return str(start) if start == end else f"{start}-{end}"

class GroupNode(Node):
    children: Node
    def __init__(self, val_range: tuple):
        super().__init__(val_range)
        self.children = []

    def type(self):
        return self.__class__.__name__

class MatcherNode(Node):
    children: Node
    def __init__(self, val_range: tuple):
        super().__init__(val_range)
        self.children = []

    def type(self):
        return self.__class__.__name__

class QuantifierNode(Node):
    quantifier: str
    child: Node
    def __init__(self, quantifier: str, val_range: tuple):
        super().__init__(val_range)
        self. quantifier = quantifier
        self.child = None

    def type(self):
        return self.__class__.__name__

class Parser:
    nodes: list[Node]
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.states = {}
        self.nodes = []
        self.parse()

    def parse(self, tokens: list[str] = None):
        if tokens is None:
            tokens = self.lexer.tokenized_regex

        nodes = []
        for token in tokens:
            node = None

            if token.startswith("GROUP-"):
                node = GroupNode((0, 0))
                node.children = self.parse(self.lexer.groups[int(token[6:])])
            
            elif token.startswith("MATCHER-"):
                node = MatcherNode((0, 0))
                node.children = self.parse(self.lexer.matchers[int(token[8:])])
            
            elif token.startswith("QUANTIFIER-"):
                quantifier, childTokens = self.lexer.quantifiers[int(token[11:])] 
                node = QuantifierNode(quantifier, (0, 0))
                node.child = self.parse([childTokens])[0]
            
            elif token.startswith("RANGE-"):
                rangeValues = self.lexer.ranges[int(token[6:])]
                node = Node((rangeValues[0], rangeValues[1]))
            
            else:
                node = Node((token, token))
            
            nodes.append(node)

        self.nodes = nodes
        return nodes
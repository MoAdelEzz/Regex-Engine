from __future__ import annotations
from lexer import Lexer
from helper import *

class Parser:
    nodes: list[Node]
    def __init__(self: Parser, lexer: Lexer):
        self.lexer = lexer
        self.states = {}
        self.nodes = self.parse(lexer.tokenizedRegex)

    def parse(self, tokens: list[str]) -> list[Node]:
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
                node.children = [self.parse([childTokens])[0]]
            
            elif token.startswith("RANGE-"):
                rangeValues = self.lexer.ranges[int(token[6:])]
                node = Node((rangeValues[0], rangeValues[1]))
            
            else:
                node = Node((token, token))
            
            nodes.append(node)
        return nodes
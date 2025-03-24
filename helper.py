from __future__ import annotations

NODE_ID = 0
STATE_COUNTER = 0
EPSILON = "ε"

class State:
    id: int
    name: str
    isTerminatingState: bool
    transitions: dict[str, set[int]]

    def __init__(self: State):
        global STATE_COUNTER
        self.id = STATE_COUNTER
        STATE_COUNTER += 1

        self.isTerminatingState = False
        self.transitions = {}
        self.name = ""

class Node:
    id: int
    startState: int
    exitState: int
    valueRange: tuple[int, int]
    def __init__(self, val_range: tuple):
        global NODE_ID
        NODE_ID += 1
        self.id = NODE_ID
        self.valueRange = val_range

    def type(self):
        return self.__class__.__name__
    
    def GetValue(self):
        l   = self.valueRange[0]
        r   = self.valueRange[1]
        return str(l) if l == r else f"{l}-{r}"

class GroupNode(Node):
    children: list[Node]
    def __init__(self, val_range: tuple):
        super().__init__(val_range)
        self.children = []

    def type(self):
        return self.__class__.__name__

class MatcherNode(Node):
    children: list[Node]
    def __init__(self, val_range: tuple):
        super().__init__(val_range)
        self.children = []

    def type(self):
        return self.__class__.__name__

class QuantifierNode(Node):
    quantifier: str
    children: list[Node]
    def __init__(self, quantifier: str, val_range: tuple):
        super().__init__(val_range)
        self. quantifier = quantifier
        self.children = []

    def type(self):
        return self.__class__.__name__ + f"({self.quantifier})"
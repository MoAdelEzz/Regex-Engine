from __future__ import annotations
import graphviz
import json

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
    
def DrawSM(regex: str, stateMachine: dict, title: str=""):
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")
    dot.attr(overlap='false')
    dot.node('start', '', shape='none')

    startNode = stateMachine["entryState"]
    states = stateMachine["states"]

    for state, properties in states.items():
        if properties.get("isTerminatingState", False):
            dot.node(state, state, shape='doublecircle')
        else:
            dot.node(state, state, shape='circle')

    dot.edge('start', startNode)
    for state, properties in states.items():
        for symbol, destinations in properties.items():
            if symbol in ["isTerminatingState", "isEntry"]:
                continue
            for dest in destinations:
                dot.edge(state, dest, label=symbol)

    dot.attr(label=f"Regular Expression: {regex}", fontsize='20', labelloc='t', labeljust='c')
    dot.render(f"output/Figures/{title}", format='png', cleanup=True)

def WriteJson(stateMachine: dict, title: str=""):
    with open(f"output/stateMachines/{title}.json", "w+") as f:
        json.dump(stateMachine, f, indent=4)
    f.close()


def EpsilonMoves(stateMachine: dict, state: str) -> set[str]:
    result = { state }

    queue = [ state ]
    while len(queue) > 0:
        state = queue.pop(0)
        for symbol, destinations in stateMachine["states"][state].items():
            if symbol == EPSILON:
                for dest in destinations:
                    if dest not in result:
                        result.add(dest)
                        queue.append(dest)
                    else:
                        continue
    return result    

def MatchValue(value: str, stateKeys: str) -> str | None:
    for key in stateKeys:
        if "-" in key:
            l, r = key.split("-")
            if ord(l) <= ord(value) < ord(r):
                return key
        elif key == value:
            return key        
    return None

def Test(stateMachine: dict, input: str) -> bool:
    state = stateMachine["entryState"]

    queue = [ (EpsilonMoves(stateMachine, state), 0) ]

    while len(queue) > 0:
        states, index = queue.pop(0)
        for state in states:
            if index == len(input) and stateMachine["states"][state]["isTerminatingState"] == True:
                return True
            
            if index == len(input):
                continue

            key = MatchValue(input[index], stateMachine["states"][state].keys())

            if key is None:
                continue

            for dest in stateMachine["states"][state][key]:
                queue.append((EpsilonMoves(stateMachine, dest), index + 1))

    return False


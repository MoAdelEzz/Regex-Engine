from __future__ import annotations
from helper import *

class NFA:
    states: dict[int, State]
    entryState: int

    def __init__(self: NFA, nodes: list[Node]):
        self.states = {}
        self.entryState = -1
        self.GenerateNFA(nodes, main=True)
    
    def CreateState(self: NFA) -> State:
        state = State()
        self.states[state.id] = state
        return state
    
    def AddTransition(self: NFA, startId: int, endId: int, characters: str) -> None:
        self.states[startId].transitions.setdefault(characters, set()).add(endId)
    
    def MergeTopLevel(self: NFA, nodes: list[Node]) -> None:
        for l, r in zip(nodes[:-1], nodes[1:]):
            self.AddTransition(l.exitState, r.startState, EPSILON)

    def CreateValuesState(self: NFA, node: Node) -> None:
        entryState  = self.CreateState()
        exitState   = self.CreateState()    
        self.AddTransition(entryState.id, exitState.id, node.GetValue())
        node.startState  = entryState.id
        node.exitState    = exitState.id
     
    def CreateGroupState(self: NFA, groupNode: GroupNode) -> None:
        for l, r in zip(groupNode.children[:-1], groupNode.children[1:]):
            self.AddTransition( l.exitState, r.startState, EPSILON )

        groupNode.startState = groupNode.children[0].startState
        groupNode.exitState   = groupNode.children[-1].exitState

    def CreateMatcherState(self: NFA, matcherNode: MatcherNode) -> None:
        matcherNode.startState   = matcherNode.children[0].startState
        matcherNode.exitState     = matcherNode.children[0].exitState
        if len(matcherNode.children) > 1:
            entry   = self.CreateState()
            exit    = self.CreateState()
            for node in matcherNode.children:
                self.AddTransition(entry.id, node.startState, EPSILON)
                self.AddTransition(node.exitState, exit.id, EPSILON)
            matcherNode.startState = entry.id
            matcherNode.exitState = exit.id

    def CreateQuantifierState(self: NFA, node: QuantifierNode, connections: list[int]) -> None:
        entryState   = self.CreateState()
        exitState    = self.CreateState()
        node.startState   = entryState.id
        node.exitState     = exitState.id

        for connection in connections:
            if connection   == 1:
                self.AddTransition(entryState.id, node.children[0].startState, EPSILON)
            elif connection == 2:
                self.AddTransition(entryState.id, exitState.id, EPSILON)
            elif connection == 3:
                self.AddTransition(node.children[0].exitState, exitState.id, EPSILON)
            elif connection == 4:
                self.AddTransition(node.children[0].exitState, entryState.id, EPSILON)

    def CreateZeroMoreState(self: NFA, node: QuantifierNode) -> None:
        self.CreateQuantifierState(node, [1, 2, 3, 4])

    def CreateOneMoreState(self, quantifier: QuantifierNode) -> None:
        self.CreateQuantifierState(quantifier, [1, 3, 4])

    def CreateOneZeroState(self, quantifier: QuantifierNode) -> None:
        self.CreateQuantifierState(quantifier, [1, 2, 3])

    def GenerateNFA(self, nodes: list[Node], main: bool = True) -> None:
        for node in nodes:
            if node.type() != "Node":
                self.GenerateNFA(node.children, False)

            match node.type():
                case "Node":
                    self.CreateValuesState(node)
                case "GroupNode":
                    self.CreateGroupState(node)
                case "MatcherNode":
                    self.CreateMatcherState(node)
                case "QuantifierNode(*)":
                    self.CreateZeroMoreState(node)
                case "QuantifierNode(+)":
                    self.CreateOneMoreState(node)
                case "QuantifierNode(?)":
                    self.CreateOneZeroState(node)

        if main:
            if len(nodes) > 1:
                self.MergeTopLevel(nodes)
            self.entryState = nodes[0].startState
            self.states[ nodes[-1].exitState ].isTerminatingState = True
    
    def ToJson(self: NFA) -> dict:
        return {
            "entryState": f"S{self.entryState}",
            "states": {
                f"S{state.id}": {
                    "isTerminatingState": state.isTerminatingState,
                    **{key: [f"S{v}" for v in value] for key, value in state.transitions.items()}
                } for state in self.states.values()
            }
        }
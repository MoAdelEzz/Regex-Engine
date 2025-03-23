from __future__ import annotations
from parser import *
import json

state_id = 0
EPSILON = "ε"

class State:
    id: int
    name: str
    isTerminatingState: bool
    isEntry: bool
    transitions: dict[str, set[int]]

    def __init__(self, isTerminatingState: bool = False, isEntry: bool = False):
        global state_id
        state_id += 1
        self.id = state_id
        self.isTerminatingState = isTerminatingState
        self.isEntry = isEntry
        self.transitions = {}
        self.name = ""

class NFA:
    states: dict[int, State]
    entry_state: int

    def __init__(self, nodes: list[Node]):
        self.states = {}
        self.generate_nfa(nodes)
        if len(nodes) > 1:
            self.concat_top_level(nodes)
        self.entry_state = nodes[0].start
        self.states[ nodes[0].start ].isEntry = True
        self.states[ nodes[-1].end ].isTerminatingState = True
    
    def create_state(self):
        state = State()
        self.states[state.id] = state
        return state
    
    def add_transition(self, start, end, value):
        if value not in self.states[start].transitions.keys():
            self.states[start].transitions[value] = set()
        self.states[start].transitions[value].add(end)
        

    def to_json(self):
        jsonObj = {}

        for state in self.states.values():
            transitions = {}
            for key, value in state.transitions.items():
                transitions[key] = [ f"S{v}" for v in value ]

            jsonObj.update({
                f"S{state.id}" : { 
                    "isTerminatingState" : state.isTerminatingState, 
                    "isEntry" : state.isEntry, 
                } | transitions
            })

        return {
            "entryState" : f"S{self.entry_state}",
            "states" : jsonObj
        }
    
    def concat_top_level(self, nodes: list[Node]):
        for i in range(len(nodes) - 1):
            l = nodes[i]
            r = nodes[i + 1]
            self.add_transition(l.end, r.start, EPSILON)


    def values_state(self, node: Node):
        entry = self.create_state()
        exit = self.create_state()
        self.add_transition(entry.id, exit.id, node.get_value())
        node.start = entry.id
        node.end = exit.id
    
    def group_state(self, group: GroupNode):
        for i in range(len(group.children) - 1):
            l = group.children[i]
            r = group.children[i + 1]
            self.add_transition(l.end, r.start, EPSILON)

        group.start = group.children[0].start
        group.end = group.children[-1].end

    def matcher_state(self, matcher: MatcherNode):
        if len(matcher.children) == 1:
            matcher.start = matcher.children[0].start
            matcher.end = matcher.children[0].end
        else:
            entry = self.create_state()
            exit = self.create_state()
            for node in matcher.children:
                self.add_transition(entry.id, node.start, EPSILON)
                self.add_transition(node.end, exit.id, EPSILON)
            matcher.start = entry.id
            matcher.end = exit.id

    def asterisk_state(self, quantifier: QuantifierNode):
        entry = self.create_state()
        exit = self.create_state()
        self.add_transition(entry.id, quantifier.child.start, EPSILON) # 1
        self.add_transition(entry.id, exit.id, EPSILON) # 2
        self.add_transition(quantifier.child.end, exit.id, EPSILON) # 3
        self.add_transition(quantifier.child.end, entry.id, EPSILON) # 4
        quantifier.start = entry.id
        quantifier.end = exit.id


    def plus_state(self, quantifier: QuantifierNode):
        entry = self.create_state()
        exit = self.create_state()
        self.add_transition(entry.id, quantifier.child.start, EPSILON) # 1
        self.add_transition(quantifier.child.end, exit.id, EPSILON) # 3
        self.add_transition(quantifier.child.end, entry.id, EPSILON) # 4
        quantifier.start = entry.id
        quantifier.end = exit.id


    def question_state(self, quantifier: QuantifierNode):
        entry = self.create_state()
        exit = self.create_state()
        self.add_transition(entry.id, quantifier.child.start, EPSILON) # 1
        self.add_transition(entry.id, exit.id, EPSILON) # 2
        self.add_transition(quantifier.child.end, exit.id, EPSILON) # 3
        quantifier.start = entry.id
        quantifier.end = exit.id

    def generate_nfa(self, nodes: list[Node]):
        for node in nodes:
            match node.type():
                case "Node":
                    self.values_state(node)
                case "GroupNode":
                    self.generate_nfa(node.children)
                    self.group_state(node)
                case "MatcherNode":
                    self.generate_nfa(node.children)
                    self.matcher_state(node)
                case "QuantifierNode":
                    self.generate_nfa([node.child])
                    match node.quantifier:
                        case "*":
                            self.asterisk_state(node)
                        case "+":
                            self.plus_state(node)
                        case "?":
                            self.question_state(node)


    def test(self, string: str):
        queue = [(self.entry_state, 0)]
        while len(queue) > 0:
            current_state, it = queue.pop()

            if current_state == 8:
                ""

            if self.states[current_state].isTerminatingState and it == len(string):
                return True
            
            for symbol, destinations in self.states[current_state].transitions.items():
                value_range = [ symbol, symbol ] if symbol.find("-") == -1 else symbol.split("-")
                if symbol in EPSILON:
                    queue.extend([(dest, it) for dest in destinations])
                elif it < len(string) and ord(value_range[0]) <= ord(string[it]) <= ord(value_range[1]):
                    queue.extend([(dest, it + 1) for dest in destinations])
        return False
from __future__ import annotations
from helper import *

class DFA:
    entryState: int
    states: dict[int, State]
    def __init__(self: DFA, nfaJson: dict):
        global STATE_COUNTER
        STATE_COUNTER = 0

        self.states = {}
        self.entryState = 0
        self.nfaJson = nfaJson

        self.Convert()

    def CreateMegaState(self: DFA, nodeName: str):
        state = State()
        self.states[nodeName] = state
        return state

    def AddTransition(self: DFA, startState: int, exitState: int, characters: str):
        self.states[startState].transitions.setdefault(characters, set()).add(exitState)

    def GetMergedTransitions(self: DFA, states_set: list[int]):
        states = self.nfaJson["states"]
        mergedTransitions = {}
        for state in states_set:
            mergedTransitions.update({
                key: mergedTransitions.get(key, set()).union(value)
                for key, value in states[state].items()
                if key not in [EPSILON, "isTerminatingState"]
            })
        return mergedTransitions

    def EpsilonMoveNeighbors(self: DFA, root: list[int], visited: set = None) -> list[int]:
        if visited is None:
            visited = set()

        rootKey = "-".join(list(set(root)))
        if rootKey in visited: return []
        visited.add(rootKey)

        states = self.nfaJson["states"]
        epsilonMoveNeighbor = [ states[state][EPSILON] for state in root if EPSILON in states[state].keys() ] 

        for neighbor in epsilonMoveNeighbor:
            root += self.EpsilonMoveNeighbors(neighbor, visited)

        return list(set(root))
    
    def ToJson(self: DFA):
        name_id = { state.name: f"S{idx}" for idx, state in enumerate(self.states.values()) }

        return {
            "entryState": name_id[self.entryState],
            "states": {
                f"{name_id[state.name]}": {
                    "isTerminatingState": state.isTerminatingState,
                    **{key: [name_id[v] for v in value] for key, value in state.transitions.items()}
                } for state in self.states.values()
            }
        }


    def Convert(self: DFA):
        entryState = self.nfaJson["entryState"]
        states = self.nfaJson["states"]

        queue = [([entryState], None, None)]
        while len(queue) > 0:
            current_states, parent, key = queue.pop(0)

            mega_state_components = self.EpsilonMoveNeighbors(list(current_states), set())
            mega_state_transitions = self.GetMergedTransitions(mega_state_components)
            mega_state_name = "-".join(sorted([ c for c in mega_state_components ]))

            if mega_state_name in self.states.keys():
                self.AddTransition(parent, mega_state_name, key)
                continue
            
            mega_state = self.CreateMegaState(mega_state_name)
            mega_state.name = mega_state_name

            if parent is not None:
                self.AddTransition(parent, mega_state.name, key)
            else:
                self.entryState = mega_state_name

            for key, next_states in mega_state_transitions.items():
                queue.append( (next_states, mega_state_name, key) )

        for state in self.states.keys():
            components = state.split("-")
            for component in components:
                self.states[state].isTerminatingState |= states[component]["isTerminatingState"]

        return self.states
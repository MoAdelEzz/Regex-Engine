from nfa import NFA, State


EPSILON = "ε"
class DFA:
    entry_state: int
    states: dict[int, State]
    def __init__(self):
        self.states = {}
        self.entry_state = 0
        pass

    def create_mega_state(self, name):
        state = State()
        self.states[name] = state
        return state

    def add_transition(self, start, end, value):
        if value not in self.states[start].transitions.keys():
            self.states[start].transitions[value] = set()
        self.states[start].transitions[value].add(end)

    def get_set_transitions(self, states: dict, states_set: list[int]):
        transitions = {}
        for state in states_set:
            for key, value in states[state].items():
                if key in ["isTerminatingState", "isEntry", EPSILON]: continue
                if key not in transitions.keys():
                    transitions[key] = set()
                transitions[key].update(value)
        return transitions

    def epsilon_closure_states(self, states: dict, start_states: list[int], visited: set = set()):
        ret = start_states
        epsilon_moves = [ states[state][EPSILON] for state in start_states if EPSILON in states[state].keys() ] 
        for state in epsilon_moves:
            key = "-".join(list(set(state)))
            if key in visited: continue
            visited.add(key)
            ret += self.epsilon_closure_states(states, state, visited)
        return list(set(ret))
    
    def to_json(self):
        jsonObj = {}

        for state in self.states.values():
            transitions = {}
            for key, value in state.transitions.items():
                print(value)
                transitions[key] = [ f"{v}" for v in value ]

            jsonObj.update({
                f"{state.name}" : { 
                    "isTerminatingState" : state.isTerminatingState, 
                    "isEntry" : state.isEntry, 
                } | transitions
            })

        return {
            "entryState" : f"{self.entry_state}",
            "states" : jsonObj
        }


    def convert(self, jsonObj: dict):
        entry_state = jsonObj["entryState"]
        states = jsonObj["states"]

        queue = [([entry_state], None, None)]
        while len(queue) > 0:
            current_states, parent, key = queue.pop(0)

            mega_state_components = self.epsilon_closure_states(states, list(current_states), set())
            mega_state_transitions = self.get_set_transitions(states, mega_state_components)
            mega_state_name = "-".join(sorted([ c for c in mega_state_components ]))

            if mega_state_name in self.states.keys():
                self.add_transition(parent, mega_state_name, key)
                continue
            
            mega_state = self.create_mega_state(mega_state_name)
            mega_state.name = mega_state_name

            if parent is not None:
                self.add_transition(parent, mega_state.name, key)
            else:
                self.entry_state = mega_state_name
                mega_state.isEntry = True

            for key, next_states in mega_state_transitions.items():
                queue.append( (next_states, mega_state_name, key) )

        for state in self.states.keys():
            components = state.split("-")
            for component in components:
                self.states[state].isTerminatingState |= states[component]["isTerminatingState"]

        return self.states

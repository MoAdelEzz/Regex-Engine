from dfa import DFA

class MinDfa:
    def __init__(self, dfaJson: dict):
        self.entry_state = dfaJson["entryState"]
        state_count = len(dfaJson["states"])
        self.dfa_states = dfaJson["states"]
        self.key_idx = { key: idx for idx, key in enumerate(dfaJson["states"].keys()) }
        self.idx_key = { idx: key for idx, key in enumerate(dfaJson["states"].keys()) }
        self.distinguishable = [[True for _ in range(state_count)] for __ in range(state_count)]


    def init_distinguishables(self):
        terminal_states = [ key for key, state in self.dfa_states.items() if state["isTerminatingState"] ]

        for key in self.dfa_states.keys():
            self.distinguishable[self.key_idx[key]][self.key_idx[key]] = False
            if key not in terminal_states:
                for key2 in terminal_states:
                    self.distinguishable[self.key_idx[key]][self.key_idx[key2]] = False
                    self.distinguishable[self.key_idx[key2]][self.key_idx[key]] = False
    
    def get_common_transitions(self, state1, state2):
        transition_1 = self.dfa_states[state1].keys()
        transition_2 = self.dfa_states[state2].keys()

        if transition_1 != transition_2: return False, []
        else: return True, list([ t for t in transition_1 if t not in ["isTerminatingState", "isEntry"] ])
    

    def same_destinations(self, state1, state2, transition):
        destination_1 = self.dfa_states[state1][transition]
        destination_2 = self.dfa_states[state2][transition]
        return set(destination_1) == set(destination_2)

   

    def minimize(self):
        self.init_distinguishables()
        print(self.idx_key)

        for i in range(len(self.distinguishable)):
            for j in range(i):
                same_transitions, transitions = self.get_common_transitions(self.idx_key[i], self.idx_key[j])
                same_desitinations = True

                for t in transitions:
                    same_desitinations &= self.same_destinations(self.idx_key[i], self.idx_key[j], t)

                if same_transitions and same_desitinations: 
                    self.distinguishable[i][j] = False
                    self.distinguishable[j][i] = False

                else:
                    self.distinguishable[i][j] = True
                    self.distinguishable[j][i] = True


        # print(self.distinguishable)
    
    def get_set_object(self, sets: dict[int, set], state_set_map: dict[int, int]):
        set_objects: dict = {
            "entryState": None,
            "states": {

            }
        }

        for key, states in sets.items():
            set_object = {}
            set_object["isTerminatingState"] = False

            if set_objects["entryState"] is None:
                for state in states:
                    if state == self.entry_state: 
                        set_objects["entryState"] = f"S{state_set_map[state]}"

            for token, destinations in self.dfa_states[list(states)[0]].items():
                if token in ["isTerminatingState", "isEntry"]: 
                    set_object["isTerminatingState"] |= destinations if token == "isTerminatingState" else False
                    continue

                for dest in destinations:

                    if token not in set_object.keys():
                        set_object[token] = set()

                    set_object[token].add(f"S{state_set_map[dest]}")
            
            set_objects["states"] |= { f"S{key}": set_object}

        return set_objects

    def merge(self):
        sets: dict[int, set] = {}
        state_set_map: dict[int, int] = {}

        for i in range(len(self.distinguishable)):
            if self.idx_key[i] not in state_set_map:
                sets[len(sets)] = set()
                state_set_map[self.idx_key[i]] = len(sets) - 1

            for j in range(len(self.distinguishable)):
                if self.distinguishable[i][j] == False:
                    sets[state_set_map[self.idx_key[i]]].add(self.idx_key[j])
                    state_set_map[self.idx_key[j]] = state_set_map[self.idx_key[i]]

        return self.get_set_object(sets, state_set_map)


                
from dfa import DFA

class MinDfa:
    def __init__(self, dfaJson: dict):
        self.entryState = dfaJson["entryState"]
        self.dfaStates  = dfaJson["states"]
        self.key_idx    = { key: idx for idx, key in enumerate(dfaJson["states"].keys()) }
        self.idx_key    = { idx: key for idx, key in enumerate(dfaJson["states"].keys()) }

    def GetIntersectedTransitions(self, state1, state2):
        transition_1 = self.dfaStates[state1].keys()
        transition_2 = self.dfaStates[state2].keys()
        if transition_1 != transition_2: return False, []
        else: return True, list([ t for t in transition_1 if t not in ["isTerminatingState"] ])
    
    def WhichPartition(self, state):
        for idx, partition in enumerate(self.partition):
            if state in partition: return idx
        return -1

    def SameDestinations(self, state1, state2, transition):
        destination_1 = [ self.WhichPartition(s) for s in self.dfaStates[state1][transition] ]
        destination_2 = [ self.WhichPartition(s) for s in self.dfaStates[state2][transition] ]
        return set(destination_1) == set(destination_2)
    
    def Split(self, group: set[str]):


        split_groups = [ set() ]
        representative = next(iter(group))
        current_group = { representative }

        for state in group:
            if state == representative: continue

            isSame, transitions = self.GetIntersectedTransitions(representative, state)
            for t in transitions:
                isSame &= self.SameDestinations(representative, state, t)

            if isSame:
                current_group.add(state)
            else:
                split_groups[-1].add(state)

        if len(split_groups[-1]) == 0: split_groups.pop()
        return split_groups + [ current_group ]

    def Minimize(self):
        self.partition = [
            { key for key, state in self.dfaStates.items() if state["isTerminatingState"] },
            { key for key, state in self.dfaStates.items() if not state["isTerminatingState"] }
        ]
        self.partition = [ s for s in self.partition if len(s) > 0 ]

        while True:
            new_partition = []
            for group in self.partition:
                if len(group) == 1: 
                    new_partition.append(group)
                else:
                    new_partition.extend(self.Split(group))

            if len(new_partition) == len(self.partition): break
            self.partition = new_partition

        return True
    
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
                    if state == self.entryState: 
                        set_objects["entryState"] = f"S{state_set_map[state]}"

            for token, destinations in self.dfaStates[list(states)[0]].items():
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
        state_set_map = {}

        for p in self.partition:
            sets[len(sets)] = p
            for state in p:
                state_set_map[state] = len(sets) - 1 

        return self.get_set_object(sets, state_set_map)


                
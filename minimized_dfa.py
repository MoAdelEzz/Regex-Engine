from __future__ import annotations
import json

class MinDfa:
    def __init__(self: MinDfa, dfaJson: dict):
        self.partitions = []
        self.entryState = dfaJson["entryState"]
        self.dfaStates  = dfaJson["states"]
        self.key2Idx    = { key: idx for idx, key in enumerate(dfaJson["states"].keys()) }
        self.idx2Key    = { idx: key for idx, key in enumerate(dfaJson["states"].keys()) }
        self.Minimize()

    def GetIntersectedTransitions(self: MinDfa, s1Key: str, s2Key: str) -> tuple[bool, list[str]]:
        t1 = self.dfaStates[s1Key].keys()
        t2 = self.dfaStates[s2Key].keys()
        if t1 != t2: return False, []
        else: return True, list([ t for t in t1 if t not in ["isTerminatingState"] ])
    
    def WhichPartition(self: MinDfa, stateKey: str) -> int:
        for idx, partition in enumerate(self.partitions):
            if stateKey in partition: return idx
        return -1

    def SameDestinations(self: MinDfa, s1Key: str, s2Key: str, t: str) -> bool:
        d1 = [ self.WhichPartition(s) for s in self.dfaStates[s1Key][t] ]
        d2 = [ self.WhichPartition(s) for s in self.dfaStates[s2Key][t] ]
        return set(d1) == set(d2)
    
    def Split(self: MinDfa, group: set[str]) -> list[set[str]]:
        result = [ set() ]
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
                result[-1].add(state)

        if len(result[-1]) == 0: result.pop()
        return result + [ current_group ]

    def Minimize(self: MinDfa) -> bool:
        self.partitions = [
            { key for key, state in self.dfaStates.items() if state["isTerminatingState"] },
            { key for key, state in self.dfaStates.items() if not state["isTerminatingState"] }
        ]
        self.partitions = [ s for s in self.partitions if len(s) > 0 ]

        while True:
            new_partition = []
            for group in self.partitions:
                if len(group) == 1: 
                    new_partition.append(group)
                else:
                    new_partition.extend(self.Split(group))

            if len(new_partition) == len(self.partitions): break
            self.partitions = new_partition

        return True
                
    def ToJson(self: MinDfa) -> dict:
        jsonObj = { "entryState": f"S{self.WhichPartition(self.entryState)}", "states": {} }

        for idx, partition in enumerate(self.partitions):
            set_object = {"isTerminatingState": False}
            
            # if all states belongs to the same set, then taking representative
            # transition is enough
            representative = self.dfaStates[next(iter(partition))]
            for token, destinations in representative.items():
                if token == "isTerminatingState":
                    set_object["isTerminatingState"] |= destinations
                else:
                    set_object[token] = list({f"S{self.WhichPartition(dest)}" for dest in destinations})
            jsonObj["states"][f"S{idx}"] = set_object

        return jsonObj
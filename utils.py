from __future__ import annotations
from typing import TypedDict
from colorama import Fore, Style
import colorama
colorama.init()
EPSILON = "ε"
ANY = "."
class NodeType(TypedDict):
    CHAR = "CHAR"
    AND = "AND"
    OR = "OR"

state_id = -1
def get_state_id():
    global state_id
    state_id += 1
    return state_id

states = {}
node_state_map = {}

def create_state(transitions: dict = {}, end_state: bool = False): 
    id = get_state_id()
    states[f"S{id}"] = { 'isTerminatingState': end_state, 'isEntry': False } | transitions
    return f"S{id}"

def add_transitions(state_id: int, transitions: dict):
    for key, value in transitions.items():
        if key not in states[state_id].keys():
            states[state_id][key] = set()
        states[state_id][key].update(value)
    return states[state_id]

def handle_zero_or_one(root: Node):
    if not root.zeroOrOne:
        return
    root_start_id = node_state_map[root.id]["start"]
    root_end_id   = node_state_map[root.id]["end"]
    add_transitions(root_start_id, { EPSILON: { root_end_id } })

def handle_zero_or_more(root: Node):
    if not root.zeroOrMore:
        return

    start_node_id = create_state()
    end_node_id   = create_state()

    root_start_id = node_state_map[root.id]["start"]
    root_end_id   = node_state_map[root.id]["end"]

    add_transitions(start_node_id, { EPSILON: { root_start_id, end_node_id } })
    add_transitions(root_end_id, { EPSILON: { start_node_id, end_node_id  } })
    
    node_state_map[root.id] = {
        "start": start_node_id,
        "end": end_node_id
    }

def handle_one_or_more(root: Node):
    if not root.oneOrMore:
        return
    
    start_node_id = create_state()
    end_node_id   = create_state()

    root_start_id = node_state_map[root.id]["start"]
    root_end_id   = node_state_map[root.id]["end"]

    add_transitions(start_node_id, { EPSILON: { root_start_id } })
    add_transitions(root_end_id, { EPSILON: { start_node_id, end_node_id } })
    
    node_state_map[root.id] = {
        "start": start_node_id,
        "end": end_node_id
    }

def create_character_state(root: Node):
    start_node_id = create_state()
    end_node_id   = create_state()
    add_transitions(start_node_id, { root.get_value(): { end_node_id } })
    node_state_map[root.id] = {
        "start": start_node_id,
        "end": end_node_id
    }
    handle_one_or_more(root)
    handle_zero_or_one(root)
    handle_zero_or_more(root)

def create_and_state(root: Node):
    previous_node_id = node_state_map[root.children[0].id]["end"]

    for child in root.children[1:]:
        current_node_id = node_state_map[child.id]["start"]
        add_transitions(previous_node_id, { EPSILON: { current_node_id } })
        previous_node_id = node_state_map[child.id]["end"]

    node_state_map[root.id] = {
        "start": node_state_map[root.children[0].id]["start"],
        "end": node_state_map[root.children[-1].id]["end"]
    }

    if root.id == 0:
        states[node_state_map[root.id]["start"]].update({ "isEntry": True })
        states[node_state_map[root.id]["end"]].update({ "isTerminatingState": True })

    handle_one_or_more(root)
    handle_zero_or_one(root)
    handle_zero_or_more(root)

def create_or_state(root: Node):
    if len(root.children) == 1:
        node_state_map[root.id] = {
            "start": node_state_map[root.children[0].id]["start"],
            "end": node_state_map[root.children[0].id]["end"]
        }
    else:
        start_state_id = create_state()
        end_state_id = create_state()

        for child in root.children:
            add_transitions(start_state_id, { EPSILON: { node_state_map[child.id]["start"] } })
            add_transitions(node_state_map[child.id]["end"], { EPSILON: { end_state_id } })

        node_state_map[root.id] = {
            "start": start_state_id,
            "end": end_state_id
        }

    handle_one_or_more(root)
    handle_zero_or_one(root)
    handle_zero_or_more(root)

##############################################################################
root_id = 0
def get_node_id():
    global root_id
    root_id += 1
    return root_id
    
class Node:
    type: NodeType
    children: Node
    def __init__(self, id):
        self.id = id
        self.type = NodeType.CHAR
        self.value = []
        self.isMatcher = False

        self.any = False
        self.oneOrMore = False
        self.zeroOrMore = False
        self.zeroOrOne = False

        self.children = []
   
    def get_value(self):
        return "-".join(self.value) if self.value[0] != self.value[1] else self.value[0]
    
    @staticmethod
    def create_root_node():
        root = Node(id=0)
        root.type = NodeType.AND
        return root
    def appendChild(self, node: Node):
        if len(self.children) > 0 and self.children[-1].type == NodeType.OR and len(self.children[-1].children) == 1:
            self.children[-1].children.append(node)
        else:
            self.children.append(node)
    def parse(self, regex: str):
        groups_stack = []
        matcher_stack = []

        def chech_for_errors(character: str, index: int):
            if character == ")" and len(groups_stack) == 0:
                print(f"{Fore.RED}Invalid, No opening parenthesis for closing parenthesis at position {index + 1} {Style.RESET_ALL}")
                exit(400)
            
            if character == "]" and not self.isMatcher and len(matcher_stack) == 0:
                print(f"{Fore.RED}Invalid, No opening bracket for closing bracket at position {index + 1} {Style.RESET_ALL}")
                exit(400)

            if len(matcher_stack) > 0 or len(groups_stack) > 0:
                return

            if character in ["*", "+", "?"] and len(self.children) == 0:
                print(f"{Fore.RED}Invalid, No character before quantifier at position {index + 1} {Style.RESET_ALL}")
                exit(400)

            if self.isMatcher and character == "-" and len(self.children) == 0:
                print(f"{Fore.RED}Invalid, No character before range at position {index + 1} {Style.RESET_ALL}")
                exit(400)
            
            if self.isMatcher and character == "-" and (r + 1 >= len(regex) or regex[r + 1].isalnum() == False):
                print(f"{Fore.RED}Invalid, No character after range at position {index + 1} {Style.RESET_ALL}")
                exit(400)

            if character in ["*", "+", "?"] and r + 1 < len(regex) and regex[r + 1] in ["*", "+", "?"]:
                print(f"{Fore.RED}Invalid, Multiple quantifiers at position {index + 1} {Style.RESET_ALL}")
                exit(400)

            if character in ["|"] and len(self.children) == 0:
                print(f"{Fore.RED}Invalid, No character before pipe at position {index + 1} {Style.RESET_ALL}")
                exit(400)

            if character in ["|"] and r == len(regex) - 1:
                print(f"{Fore.RED}Invalid, No character after pipe at position {index + 1} {Style.RESET_ALL}")
                exit(400)

        skip = False
        for r, char in enumerate(regex):
            chech_for_errors(char, r)
            if skip:
                skip = False
                continue

            if char == "(":
                groups_stack.append((char, r))
            elif char == ")":
                _, lg = groups_stack[-1]
                groups_stack.pop()

            if not self.isMatcher and char == "[":
                matcher_stack.append((char, r))
            elif not self.isMatcher and char == "]":
                _, lm = matcher_stack[-1]
                matcher_stack.pop()

            # this part of the regex doesn't belong to the current node
            # so we skip it
            if len(groups_stack) > 0 or len(matcher_stack) > 0:
                continue
            elif not self.isMatcher and char == "]":
                node = Node(get_node_id())
                node.type = NodeType.OR
                node.isMatcher = True
                node.parse(regex[lm+1:r])
                self.appendChild(node)
            elif char == ")":
                node = Node(get_node_id())
                node.type = NodeType.AND
                node.parse(regex[lg+1:r])
                self.appendChild(node)
            elif char == "|":
                node = Node(get_node_id())
                node.type = NodeType.OR
                node.appendChild(self.children[-1])
                self.children.pop()
                self.appendChild(node)
            elif self.isMatcher and char == "-":
                self.children[-1].value = [self.children[-1].value[0], regex[r+1]]
                skip = True
            elif char in ["*", "+", "?"]:
                self.children[-1].oneOrMore = char == "+"
                self.children[-1].zeroOrMore = char == "*"
                self.children[-1].zeroOrOne = char == "?"
            else:
                node = Node(get_node_id())
                node.type = NodeType.CHAR
                node.value = [ANY, ANY] if char == "." else [char, char]
                node.any = char == "."
                self.appendChild(node)
    def to_state_machine(self):
        if self.type == NodeType.CHAR:
            create_character_state(self)
        else:
            for child in self.children:
                child.to_state_machine()
            create_and_state(self) if self.type == NodeType.AND else create_or_state(self)
    def debug_tree(self, depth=0):
        indent = "  " * depth
        print(f"{indent}Type: {self.type}")
        print(f"{indent}Value: {self.get_value()}")
        print(f"{indent} {self.any}, {self.oneOrMore}, {self.zeroOrMore}, {self.zeroOrOne}")
        for i, child in enumerate(self.children):
            print(f"{indent}Child {i}:")
            child.debug_tree(depth + 1)

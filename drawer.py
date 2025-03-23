import json
import graphviz
from utils import *

def draw_NFA(states: dict):
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")
    dot.attr(overlap='false')  # Prevents overlapping nodes

    startNode = None
    dot.node('start', '', shape='none')
    for state, properties in states.items():
        if properties.get("isTerminatingState", False):
            dot.node(state, state, shape='doublecircle')
        else:
            startNode = state if properties.get("isEntry", True) else startNode
            dot.node(state, state, shape='circle')

    dot.edge('start', startNode)
    for state, properties in states.items():
        for symbol, destinations in properties.items():
            if symbol in ["isTerminatingState", "isEntry"]:
                continue
            
            # Add edges for each destination
            for dest in destinations:
                dot.edge(state, dest, label=symbol)

    dot.render('nfa_graph', format='png', cleanup=True)
    print("NFA graph visualization has been saved as 'nfa_graph.png'")
    print(dot.source)
import graphviz

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
    dot.render(title, format='png', cleanup=True)

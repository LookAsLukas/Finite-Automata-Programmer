import igraph as ig

def convert_automaton_to_igraph(attr):
    g = ig.Graph(directed=True)
    g.add_vertices(attr.states)
    edges = []
    labels = []
    for (src, symbol), dst_list in attr.transitions.items():
        for dst in dst_list:
            edges.append((src, dst))
            labels.append(symbol)
    g.add_edges(edges)
    g.es["label"] = labels
    return g
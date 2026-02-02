from grandalf.graphs import Graph, Vertex, Edge

def create_architecture_graph():
    nodes = {
        name: Vertex(name)
        for name in [
            "Planner",
            "Paper Retrieval",
            "PDF Download",
            "Text Extraction",
            "Analysis",
            "Draft Generation",
            "Review"
        ]
    }

    edges = [
        Edge(nodes["Planner"], nodes["Paper Retrieval"]),
        Edge(nodes["Paper Retrieval"], nodes["PDF Download"]),
        Edge(nodes["PDF Download"], nodes["Text Extraction"]),
        Edge(nodes["Text Extraction"], nodes["Analysis"]),
        Edge(nodes["Analysis"], nodes["Draft Generation"]),
        Edge(nodes["Draft Generation"], nodes["Review"]),
    ]

    return Graph(list(nodes.values()), edges)

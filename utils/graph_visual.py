# utils/graph_visual.py

from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout
import matplotlib.pyplot as plt


class VertexView:
    def __init__(self, w=100, h=40):
        self.w = w
        self.h = h
        self.xy = (0, 0)


def create_vertex(name):
    v = Vertex(name)
    v.view = VertexView()
    return v


def visualize_workflow():

    # -------- Nodes --------
    planner = create_vertex("Planner")
    retrieval = create_vertex("Paper Retrieval")
    downloader = create_vertex("PDF Downloader")
    extractor = create_vertex("Text Extractor")
    analyzer = create_vertex("Analyzer")
    draft = create_vertex("Draft Generator")
    reviewer = create_vertex("Reviewer")
    output = create_vertex("Final Output")

    vertices = [
        planner, retrieval, downloader, extractor,
        analyzer, draft, reviewer, output
    ]

    # -------- Edges --------
    edges = [
        Edge(planner, retrieval),
        Edge(retrieval, downloader),
        Edge(downloader, extractor),
        Edge(extractor, analyzer),
        Edge(analyzer, draft),
        Edge(draft, reviewer),
        Edge(reviewer, output),
    ]

    graph = Graph(vertices, edges)

    # -------- Layout --------
    component = graph.C[0]   # ← YOUR VERSION NEEDS THIS
    layout = SugiyamaLayout(component)
    layout.init_all()
    layout.draw()

    # -------- Plot --------
    fig, ax = plt.subplots(figsize=(12, 8))

    for v in component.V():
        x, y = v.view.xy
        ax.text(
            x, y, v.data,
            bbox=dict(boxstyle="round", facecolor="lightblue"),
            ha="center",
            va="center"
        )

    for e in component.E():
        x1, y1 = e.v[0].view.xy
        x2, y2 = e.v[1].view.xy
        ax.plot([x1, x2], [y1, y2])

    ax.set_title("AI Research Review Workflow (Grandalf DAG Layout)")
    ax.set_axis_off()
    plt.show()


if __name__ == "__main__":
    visualize_workflow()

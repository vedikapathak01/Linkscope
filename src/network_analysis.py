from __future__ import annotations

from typing import Iterable

import networkx as nx
import pandas as pd
import plotly.graph_objects as go


def build_bipartite_graph(
    df: pd.DataFrame,
    min_connections: int = 1,
    category: str | None = None,
    domain: str | None = None,
) -> nx.Graph:
    """Create a user-to-website bipartite graph with weighted edges."""
    graph = nx.Graph()
    if df.empty:
        return graph

    working = df.copy()
    if category and category != "All":
        working = working[working["category"] == category]
    if domain and domain != "All":
        working = working[working["domain"] == domain]

    for _, row in working.iterrows():
        user = row["user_id"]
        website = row["domain"]
        graph.add_node(user, node_type="user")
        graph.add_node(website, node_type="website", category=row["category"])
        if graph.has_edge(user, website):
            graph[user][website]["weight"] = graph[user][website].get("weight", 0) + 1
        else:
            graph.add_edge(user, website, weight=1)

    if min_connections > 1:
        nodes_to_remove = []
        for node in list(graph.nodes):
            if graph.nodes[node].get("node_type") == "user" and graph.degree(node) < min_connections:
                nodes_to_remove.append(node)
            if graph.nodes[node].get("node_type") == "website" and graph.degree(node) < min_connections:
                nodes_to_remove.append(node)
        graph.remove_nodes_from(nodes_to_remove)

    return graph


def compute_graph_measures(graph: nx.Graph) -> pd.DataFrame:
    """Return summary measures for graph nodes."""
    if graph.number_of_nodes() == 0:
        return pd.DataFrame(columns=["node", "node_type", "degree", "weighted_degree", "betweenness", "pagerank"])

    degree = dict(graph.degree(weight="weight"))
    weighted_degree = {node: sum(data.get("weight", 1) for _, data in graph[node].items()) for node in graph.nodes}
    betweenness = nx.betweenness_centrality(graph, weight="weight") if graph.number_of_edges() > 0 else {node: 0.0 for node in graph.nodes}
    pagerank = nx.pagerank(graph, weight="weight") if graph.number_of_edges() > 0 else {node: 0.0 for node in graph.nodes}

    rows = []
    for node in graph.nodes:
        rows.append(
            {
                "node": node,
                "node_type": graph.nodes[node].get("node_type", "unknown"),
                "degree": degree.get(node, 0),
                "weighted_degree": weighted_degree.get(node, 0),
                "betweenness": betweenness.get(node, 0.0),
                "pagerank": pagerank.get(node, 0.0),
            }
        )

    return pd.DataFrame(rows).sort_values(["weighted_degree", "degree"], ascending=False).reset_index(drop=True)


def plot_bipartite_network(graph: nx.Graph, max_nodes: int = 80) -> go.Figure:
    """Create a Plotly network visualization for the user-to-website graph."""
    if graph.number_of_nodes() == 0:
        return go.Figure()

    all_nodes = list(graph.nodes)
    if len(all_nodes) > max_nodes:
        degree_ranking = sorted(all_nodes, key=lambda n: graph.degree(n, weight="weight"), reverse=True)[:max_nodes]
        graph = graph.subgraph(degree_ranking).copy()

    positions = nx.spring_layout(graph, seed=42, k=1.5)
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node in graph.nodes:
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)
        label = node
        node_type = graph.nodes[node].get("node_type", "node")
        info = f"Node: {label}<br>Type: {node_type}<br>Degree: {graph.degree(node, weight='weight')}"
        node_text.append(info)
        if node_type == "user":
            node_color.append("#4C78A8")
            node_size.append(18)
        else:
            node_color.append("#F58518")
            node_size.append(24)

    edge_x = []
    edge_y = []
    for u, v in graph.edges():
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1, color="#9aa0a6"),
            hoverinfo="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=[node for node in graph.nodes],
            textposition="top center",
            marker=dict(size=node_size, color=node_color, line=dict(width=1, color="#ffffff")),
            hovertemplate="%{text}<br>%{customdata}<extra></extra>",
            customdata=node_text,
        )
    )
    fig.update_layout(
        title="User–Website Sharing Network",
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=5, r=5, t=40, b=5),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=640,
    )
    return fig


def build_website_relationship_graph(df: pd.DataFrame) -> nx.Graph:
    """Build a website co-sharing graph: site A ↔ site B when same users share both."""
    graph = nx.Graph()
    if df.empty:
        return graph

    user_to_sites = df.groupby("user_id")["domain"].apply(lambda x: sorted(set(x))).to_dict()
    for user, domains in user_to_sites.items():
        for i, source in enumerate(domains):
            for target in domains[i + 1 :]:
                if source == target:
                    continue
                if graph.has_edge(source, target):
                    graph[source][target]["weight"] = graph[source][target].get("weight", 0) + 1
                else:
                    graph.add_edge(source, target, weight=1)
    return graph


def plot_website_relationship_graph(graph: nx.Graph, max_nodes: int = 60) -> go.Figure:
    """Visualize strongest website co-sharing relationships."""
    if graph.number_of_nodes() == 0:
        return go.Figure()

    if graph.number_of_nodes() > max_nodes:
        ranking = sorted(graph.nodes, key=lambda n: graph.degree(n, weight="weight"), reverse=True)[:max_nodes]
        graph = graph.subgraph(ranking).copy()

    positions = nx.spring_layout(graph, seed=7, k=1.1)
    edge_x, edge_y = [], []
    for u, v in graph.edges():
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [positions[n][0] for n in graph.nodes]
    node_y = [positions[n][1] for n in graph.nodes]
    hover_labels = [
        f"Website: {node}<br>Co-share connections: {graph.degree(node, weight='weight')}<br>Neighbors: {len(list(graph.neighbors(node)))}"
        for node in graph.nodes
    ]

    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#7a7a7a"), hoverinfo="none"))
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=list(graph.nodes),
            textposition="top center",
            marker=dict(size=16, color="#00A676", line=dict(width=1, color="#ffffff")),
            hovertemplate="%{text}<br>%{customdata}<extra></extra>",
            customdata=hover_labels,
        )
    )
    fig.update_layout(
        title="Website Co-sharing Network",
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=5, r=5, t=40, b=5),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=620,
    )
    return fig


def summarize_relationships(graph: nx.Graph) -> pd.DataFrame:
    """Return strongest linked pairs of websites."""
    if graph.number_of_edges() == 0:
        return pd.DataFrame(columns=["source", "target", "shared_users", "weight"])

    rows = []
    for source, target, data in graph.edges(data=True):
        rows.append({"source": source, "target": target, "shared_users": data.get("weight", 0), "weight": data.get("weight", 0)})
    return pd.DataFrame(rows).sort_values("weight", ascending=False).reset_index(drop=True)

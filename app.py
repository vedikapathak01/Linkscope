from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    apply_filters,
    compute_category_summary,
    compute_category_distribution,
    compute_domain_detail,
    compute_domain_summary,
    compute_overview_metrics,
    compute_post_timeline,
    compute_top_pairs,
    compute_top_users,
    summarize_website_pairs,
)
from src.data_loader import load_data
from src.network_analysis import (
    build_bipartite_graph,
    build_website_relationship_graph,
    compute_graph_measures,
    plot_bipartite_network,
    plot_website_relationship_graph,
    summarize_relationships,
)
from src.utils import format_number


st.set_page_config(page_title="LinkScope", page_icon="🔗", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(180deg, #f6f9ff 0%, #ffffff 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        [data-testid="stSidebar"] {
            background: #0b1736;
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            background: #eef3ff;
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 0.5rem 1rem;
        }
        div[data-testid="metric-container"] {
            background: white;
            border: 1px solid #e6ebf5;
            border-radius: 0.75rem;
            padding: 0.8rem;
            box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_styles()


@st.cache_data
def get_dataset() -> pd.DataFrame:
    return load_data()


def filter_sidebar(df: pd.DataFrame):
    st.sidebar.title("LinkScope")
    st.sidebar.caption("Social Media Hyperlink Intelligence")
    st.sidebar.markdown("Demo / Synthetic Dataset")

    if "linkscope_category" not in st.session_state:
        st.session_state.linkscope_category = "All"
    if "linkscope_domain" not in st.session_state:
        st.session_state.linkscope_domain = "All"

    category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
    if st.session_state.linkscope_category not in category_options:
        st.session_state.linkscope_category = "All"

    category = st.sidebar.selectbox(
        "Category",
        category_options,
        index=category_options.index(st.session_state.linkscope_category),
    )
    st.session_state.linkscope_category = category

    filtered_by_category = df if category == "All" else df[df["category"] == category]
    domain_options = ["All"] + sorted(filtered_by_category["domain"].dropna().unique().tolist())
    if st.session_state.linkscope_domain not in domain_options:
        st.session_state.linkscope_domain = "All"

    domain = st.sidebar.selectbox(
        "Domain",
        domain_options,
        index=domain_options.index(st.session_state.linkscope_domain),
    )
    st.session_state.linkscope_domain = domain

    default_start = df["timestamp"].min().date() if not df.empty else pd.Timestamp.today().date()
    default_end = df["timestamp"].max().date() if not df.empty else pd.Timestamp.today().date()

    start_date = st.sidebar.date_input("Start date", value=default_start, min_value=default_start, max_value=default_end)
    end_date = st.sidebar.date_input("End date", value=default_end, min_value=default_start, max_value=default_end)
    min_shares = st.sidebar.number_input("Minimum shares", min_value=0, step=10, value=0)
    min_engagement = st.sidebar.number_input("Minimum engagement", min_value=0, step=10, value=0)

    if start_date > end_date:
        st.sidebar.warning("The selected start date is after the end date. Please correct the range.")

    return {
        "category": category,
        "domain": domain,
        "start_date": pd.Timestamp(start_date).strftime("%Y-%m-%d") if not isinstance(start_date, str) else start_date,
        "end_date": pd.Timestamp(end_date).strftime("%Y-%m-%d") if not isinstance(end_date, str) else end_date,
        "min_shares": int(min_shares),
        "min_engagement": int(min_engagement),
    }


def render_kpi_cards(metrics: dict):
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    cards = [
        ("Total Posts", metrics["total_posts"]),
        ("Total URLs", metrics["total_urls"]),
        ("Unique Users", metrics["unique_users"]),
        ("Unique Websites", metrics["unique_websites"]),
        ("Total Shares", metrics["total_shares"]),
        ("Total Engagement", metrics["total_engagement"]),
    ]
    for i, (label, value) in enumerate(cards):
        cols = [col1, col2, col3, col4, col5, col6][i]
        cols.metric(label, format_number(value))


def show_empty_filters_message(df: pd.DataFrame) -> bool:
    if df.empty:
        st.info("No data available for the selected filters")
        return True
    return False


def overview_page(df: pd.DataFrame):
    st.title("LINKSCOPE")
    st.caption("Social Media Hyperlink Intelligence")
    st.subheader("Discover how information sources spread through social networks.")
    st.markdown("Demo / Synthetic Dataset")

    if show_empty_filters_message(df):
        return

    metrics = compute_overview_metrics(df)
    render_kpi_cards(metrics)

    st.markdown("### Overview")
    col1, col2 = st.columns(2)
    with col1:
        top_domains = df.groupby("domain")["shares"].sum().sort_values(ascending=False).head(10).reset_index()
        if top_domains.empty:
            st.info("No data available for the selected filters")
        else:
            fig = px.bar(top_domains, x="domain", y="shares", color="shares", title="Top 10 most shared domains")
            fig.update_layout(xaxis_tickangle=-45, height=420)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        category_distribution = compute_category_distribution(df)
        if category_distribution.empty:
            st.info("No data available for the selected filters")
        else:
            fig = px.bar(category_distribution, x="category", y="domains", title="Domains by category")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        category_summary = compute_category_summary(df)
        if category_summary.empty:
            st.info("No data available for the selected filters")
        else:
            fig = px.bar(category_summary, x="category", y="engagement", title="Engagement by category")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        timeline = compute_post_timeline(df)
        if timeline.empty:
            st.info("No data available for the selected filters")
        else:
            fig = px.line(timeline, x="date", y="posts", markers=True, title="Posts over time")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)


def hyperlink_analytics_page(df: pd.DataFrame):
    st.title("Hyperlink Analytics")
    if show_empty_filters_message(df):
        return

    domain_summary = compute_domain_summary(df)

    if domain_summary.empty:
        st.info("No data available for the selected filters")
        return

    st.subheader("Most shared domains")
    st.dataframe(
        domain_summary[["domain", "category", "posts", "unique_users", "shares", "engagement", "average_engagement", "influence_score"]]
        .sort_values("influence_score", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Demo Influence Score")
    st.write(
        "Influence Score = 0.4 × normalized shares + 0.3 × normalized unique users + 0.2 × normalized engagement + 0.1 × normalized posts. This is a demo metric for a prototype, not a validated scientific ranking."
    )

    top_categories = compute_category_summary(df)
    if not top_categories.empty:
        fig = px.bar(top_categories, x="category", y="shares", title="Top categories by shares")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters")


def network_analysis_page(df: pd.DataFrame, filters_dict: dict):
    st.title("Network Analysis")
    st.caption("Users are nodes, websites are nodes, and an edge represents a sharing relationship.")

    if show_empty_filters_message(df):
        return

    min_connections = st.slider("Minimum number of connections", min_value=1, max_value=20, value=2)
    graph = build_bipartite_graph(df, min_connections=min_connections, category=filters_dict["category"], domain=filters_dict["domain"])
    network_df = compute_graph_measures(graph)

    st.subheader("User–Website Network")
    if graph.number_of_nodes() == 0:
        st.info("No data available for the selected filters")
    else:
        fig = plot_bipartite_network(graph)
        st.plotly_chart(fig, use_container_width=True)

    if not network_df.empty:
        st.dataframe(network_df.head(20), use_container_width=True, hide_index=True)

    st.subheader("Website–Website Relationship Network")
    website_graph = build_website_relationship_graph(df)
    if website_graph.number_of_nodes() == 0:
        st.info("No data available for the selected filters")
    else:
        relationship_fig = plot_website_relationship_graph(website_graph)
        st.plotly_chart(relationship_fig, use_container_width=True)

    pair_df = summarize_relationships(website_graph)
    st.subheader("Most strongly connected website pairs")
    if pair_df.empty:
        st.info("No data available for the selected filters")
    else:
        st.dataframe(pair_df.head(15), use_container_width=True, hide_index=True)


def information_sources_page(df: pd.DataFrame):
    st.title("Information Sources")
    if show_empty_filters_message(df):
        return

    domains = sorted(df["domain"].dropna().unique().tolist())
    if not domains:
        st.info("No data available for the selected filters")
        return

    selected_domain = st.selectbox("Select a domain", options=domains, index=0)

    info = compute_domain_detail(df, selected_domain)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Posts", info["posts"])
    col2.metric("Users", info["users"])
    col3.metric("Total Shares", info["shares"])
    col4.metric("Avg Engagement", round(info["avg_engagement"], 2))

    st.markdown("### Categories")
    st.write(", ".join(info["categories"]) if info["categories"] else "No category label noted")

    st.markdown("### Top users sharing this domain")
    if info["top_users"].empty:
        st.write("No user activity available for this domain.")
    else:
        st.dataframe(info["top_users"], use_container_width=True, hide_index=True)

    website_graph = build_website_relationship_graph(df)
    related = []
    if website_graph.has_node(selected_domain):
        neighbors = sorted(website_graph.neighbors(selected_domain), key=lambda n: website_graph[selected_domain][n].get("weight", 0), reverse=True)[:10]
        related = [{"related_domain": n, "shared_users": website_graph[selected_domain][n].get("weight", 0)} for n in neighbors]
    related_df = pd.DataFrame(related)

    st.markdown("### Related websites")
    if related_df.empty:
        st.write("No strong related-domain links were found.")
    else:
        st.dataframe(related_df, use_container_width=True, hide_index=True)

    timeline = compute_post_timeline(df[df["domain"] == selected_domain])
    if not timeline.empty:
        fig = px.line(timeline, x="date", y="posts", markers=True, title=f"Sharing activity for {selected_domain}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters")


def user_analytics_page(df: pd.DataFrame):
    st.title("User Analytics")
    if show_empty_filters_message(df):
        return

    bipartite_graph = build_bipartite_graph(df, min_connections=1)
    graph_metrics = compute_graph_measures(bipartite_graph)

    if graph_metrics.empty:
        st.info("No data available for the selected filters")
        return

    user_degree = graph_metrics[graph_metrics["node_type"] == "user"][["node", "degree"]].rename(columns={"node": "user_id", "degree": "network_degree"})
    user_df = compute_top_users(df, user_degree)
    if user_df.empty:
        st.info("No data available for the selected filters")
        return

    st.subheader("Top Users")
    columns = ["user_id", "posts", "unique_domains", "shares", "engagement", "network_degree"]
    st.dataframe(user_df[columns].head(15), use_container_width=True, hide_index=True)

    fig = px.bar(user_df.head(10), x="user_id", y="engagement", color="network_degree", title="High-engagement users")
    st.plotly_chart(fig, use_container_width=True)


def privacy_page():
    st.title("Privacy & Methodology")
    st.markdown(
        """
        ### Privacy & Ethics
        - The prototype uses synthetic and anonymized user IDs.
        - No personally identifiable information is collected.
        - Precise user location is not used.
        - Real social-media data should be handled according to platform policies and applicable privacy laws.
        - Network analysis can reveal behavioral relationships, so data minimization and anonymization are important.
        - No invasive tracking or behavioral profiling is implemented in this demo.
        """
    )

    st.markdown(
        """
        ### Methodology
        Social Media Posts
        ↓
        URL Extraction
        ↓
        Domain Identification
        ↓
        Data Cleaning
        ↓
        Hyperlink Analytics
        ↓
        Network Construction
        ↓
        Centrality & Influence Analysis
        ↓
        Visualization & Insights
        """
    )

    with st.expander("Concepts in social media analytics"):
        st.markdown(
            """
            - Nodes: individual users or websites represented in the network.
            - Edges: a sharing relationship or connection between nodes.
            - Ties: repeated or weighted connections between network members.
            - Degree centrality: how many direct connections a node has.
            - Betweenness centrality: how often a node bridges otherwise disconnected clusters.
            - Bipartite network: two different node types connected by a relation, such as user-to-website.
            - Website co-sharing network: two websites linked when the same users share both.
            """
        )


def main():
    df = get_dataset()
    filters = filter_sidebar(df)
    filtered_df = apply_filters(
        df,
        category=filters["category"],
        domain=filters["domain"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        min_shares=filters["min_shares"],
        min_engagement=filters["min_engagement"],
    )

    pages = {
        "Overview": lambda: overview_page(filtered_df),
        "Hyperlink Analytics": lambda: hyperlink_analytics_page(filtered_df),
        "Network Analysis": lambda: network_analysis_page(filtered_df, filters),
        "Information Sources": lambda: information_sources_page(filtered_df),
        "User Analytics": lambda: user_analytics_page(filtered_df),
        "Privacy & Methodology": lambda: privacy_page(),
    }

    selected_page = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[selected_page]()


if __name__ == "__main__":
    main()

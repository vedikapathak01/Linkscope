from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from src.utils import normalize_series, safe_numeric


def apply_filters(
    df: pd.DataFrame,
    category: str | None = None,
    domain: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    min_shares: int = 0,
    min_engagement: int = 0,
) -> pd.DataFrame:
    """Apply dashboard filters while avoiding failures on empty inputs."""
    working = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    if working.empty:
        return working

    working["timestamp"] = pd.to_datetime(working.get("timestamp", pd.NaT), errors="coerce")
    working["engagement"] = pd.to_numeric(working.get("engagement", 0), errors="coerce").fillna(0)
    working["shares"] = pd.to_numeric(working.get("shares", 0), errors="coerce").fillna(0)

    if category and category != "All":
        working = working[working["category"] == category]
    if domain and domain != "All":
        working = working[working["domain"] == domain]
    if start_date:
        working = working[working["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        working = working[working["timestamp"] <= pd.to_datetime(end_date)]
    if min_shares > 0:
        working = working[working["shares"] >= min_shares]
    if min_engagement > 0:
        working = working[working["engagement"] >= min_engagement]

    return working.reset_index(drop=True)


def compute_overview_metrics(df: pd.DataFrame) -> dict:
    """Compute KPI cards for the dashboard."""
    if df.empty:
        return {
            "total_posts": 0,
            "total_urls": 0,
            "unique_users": 0,
            "unique_websites": 0,
            "total_shares": 0,
            "total_engagement": 0,
        }

    return {
        "total_posts": int(df["post_id"].nunique()),
        "total_urls": int(df["url"].nunique()),
        "unique_users": int(df["user_id"].nunique()),
        "unique_websites": int(df["domain"].nunique()),
        "total_shares": int(df["shares"].sum()),
        "total_engagement": int(df["engagement"].sum()),
    }


def compute_domain_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate website-level metrics for hyperlink analytics."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "domain",
                "category",
                "posts",
                "unique_users",
                "shares",
                "likes",
                "comments",
                "engagement",
                "average_engagement",
                "influence_score",
            ]
        )

    domain_stats = (
        df.groupby("domain", as_index=False)
        .agg(
            category=("category", "first"),
            posts=("post_id", "count"),
            unique_users=("user_id", "nunique"),
            shares=("shares", "sum"),
            likes=("likes", "sum"),
            comments=("comments", "sum"),
            engagement=("engagement", "sum"),
        )
        .sort_values("engagement", ascending=False)
        .reset_index(drop=True)
    )

    domain_stats["average_engagement"] = domain_stats["engagement"] / domain_stats["posts"]
    domain_stats["influence_score"] = compute_influence_score(domain_stats)
    return domain_stats


def compute_influence_score(domain_stats: pd.DataFrame) -> pd.Series:
    """Compute a demo influence score: 0.4 shares + 0.3 unique users + 0.2 engagement + 0.1 posts."""
    if domain_stats.empty:
        return pd.Series(dtype=float)

    score_df = domain_stats[["shares", "unique_users", "engagement", "posts"]].copy()
    for col in score_df.columns:
        score_df[col] = normalize_series(score_df[col])

    weighted = (
        0.4 * score_df["shares"]
        + 0.3 * score_df["unique_users"]
        + 0.2 * score_df["engagement"]
        + 0.1 * score_df["posts"]
    )
    return weighted.round(4)


def compute_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by category for category analysis and charts."""
    if df.empty:
        return pd.DataFrame(columns=["category", "domains", "posts", "unique_users", "shares", "engagement"])

    category_stats = (
        df.groupby("category", as_index=False)
        .agg(
            domains=("domain", "nunique"),
            posts=("post_id", "count"),
            unique_users=("user_id", "nunique"),
            shares=("shares", "sum"),
            engagement=("engagement", "sum"),
        )
        .sort_values("engagement", ascending=False)
        .reset_index(drop=True)
    )
    return category_stats


def compute_post_timeline(df: pd.DataFrame, date_bin: str = "D") -> pd.DataFrame:
    """Aggregate posts by time for the overview and information-source view."""
    if df.empty:
        return pd.DataFrame(columns=["date", "posts"])

    timeline = df.copy()
    timeline["timestamp"] = pd.to_datetime(timeline["timestamp"], errors="coerce")
    timeline = timeline.dropna(subset=["timestamp"])
    if timeline.empty:
        return pd.DataFrame(columns=["date", "posts"])

    timeline["date"] = timeline["timestamp"].dt.floor(date_bin)
    timeline = timeline.groupby("date", as_index=False).agg(posts=("post_id", "count"))
    return timeline.sort_values("date").reset_index(drop=True)


def compute_top_users(df: pd.DataFrame, bipartite_degree: pd.DataFrame | None = None) -> pd.DataFrame:
    """Summarize user-level engagement and social connectivity."""
    if df.empty:
        return pd.DataFrame(columns=["user_id", "posts", "unique_domains", "shares", "engagement", "network_degree"])

    user_stats = (
        df.groupby("user_id", as_index=False)
        .agg(
            posts=("post_id", "count"),
            unique_domains=("domain", "nunique"),
            shares=("shares", "sum"),
            engagement=("engagement", "sum"),
        )
        .sort_values("engagement", ascending=False)
        .reset_index(drop=True)
    )

    if bipartite_degree is not None:
        degree_col = "degree" if "degree" in bipartite_degree.columns else "network_degree"
        degree_df = bipartite_degree[["user_id", degree_col]].copy()
        user_stats = user_stats.merge(degree_df, on="user_id", how="left")
        if degree_col != "network_degree":
            user_stats = user_stats.rename(columns={degree_col: "network_degree"})
    else:
        user_stats["network_degree"] = user_stats["unique_domains"]

    if "network_degree" not in user_stats.columns:
        user_stats["network_degree"] = 0

    return user_stats.fillna({"network_degree": 0}).sort_values(["engagement", "posts", "network_degree"], ascending=False).reset_index(drop=True)


def compute_domain_detail(df: pd.DataFrame, domain: str) -> dict:
    """Build a domain detail view for a selected website."""
    domain_df = df[df["domain"] == domain].copy() if not df.empty else pd.DataFrame()
    if domain_df.empty:
        return {
            "posts": 0,
            "users": 0,
            "shares": 0,
            "avg_engagement": 0,
            "categories": [],
            "top_users": pd.DataFrame(),
            "related": pd.DataFrame(),
            "timeline": pd.DataFrame(),
        }

    top_users = (
        domain_df.groupby("user_id", as_index=False)
        .agg(posts=("post_id", "count"), shares=("shares", "sum"), engagement=("engagement", "sum"))
        .sort_values(["engagement", "shares"], ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    timeline = compute_post_timeline(domain_df)
    categories = sorted(domain_df["category"].dropna().unique().tolist())

    return {
        "posts": int(domain_df.shape[0]),
        "users": int(domain_df["user_id"].nunique()),
        "shares": int(domain_df["shares"].sum()),
        "avg_engagement": float(domain_df["engagement"].mean()) if not domain_df.empty else 0.0,
        "categories": categories,
        "top_users": top_users,
        "related": pd.DataFrame(),
        "timeline": timeline,
    }


def compute_top_pairs(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Compute website-to-website co-sharing relationships across users."""
    if df.empty:
        return pd.DataFrame(columns=["source", "target", "shared_users", "weight"])

    user_to_sites = df.groupby("user_id")["domain"].apply(lambda x: sorted(set(x))).to_dict()
    pair_counts = {}

    for domains in user_to_sites.values():
        for i, source in enumerate(domains):
            for target in domains[i + 1 :]:
                if source == target:
                    continue
                pair = tuple(sorted((source, target)))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    if not pair_counts:
        return pd.DataFrame(columns=["source", "target", "shared_users", "weight"])

    rows = []
    for (source, target), weight in pair_counts.items():
        rows.append({"source": source, "target": target, "shared_users": weight, "weight": weight})

    pair_df = pd.DataFrame(rows).sort_values(["weight", "shared_users"], ascending=False).head(top_n).reset_index(drop=True)
    return pair_df


def summarize_website_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """Return top related domains with both direction and weight context."""
    return compute_top_pairs(df, top_n=20)


def compute_category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return counts of domains by category for the 'Domains by category' chart."""
    if df.empty:
        return pd.DataFrame(columns=["category", "domains"])
    return df.groupby("category")["domain"].nunique().reset_index(name="domains").sort_values("domains", ascending=False)

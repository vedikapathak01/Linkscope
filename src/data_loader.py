from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "social_media_links.csv"


DOMAIN_LIBRARY = {
    "Technology": [
        "github.com",
        "stackoverflow.com",
        "arxiv.org",
        "microsoft.com",
        "google.com",
        "towardsdatascience.com",
        "mit.edu",
        "keras.io",
        "openai.com",
        "huggingface.co",
        "tensorflow.org",
        "dev.to",
    ],
    "News": [
        "reuters.com",
        "bbc.com",
        "cnn.com",
        "theguardian.com",
        "nytimes.com",
        "aljazeera.com",
        "washingtonpost.com",
        "wsj.com",
        "apnews.com",
        "npr.org",
    ],
    "Education": [
        "coursera.org",
        "edx.org",
        "khanacademy.org",
        "udemy.com",
        "harvard.edu",
        "stanford.edu",
        "berkeley.edu",
        "mit.edu",
        "openstax.org",
        "cambridge.org",
    ],
    "Research": [
        "nature.com",
        "sciencedirect.com",
        "nih.gov",
        "who.int",
        "biorxiv.org",
        "cell.com",
        "plos.org",
        "annualreviews.org",
        "ieee.org",
        "scholar.google.com",
    ],
    "Entertainment": [
        "youtube.com",
        "netflix.com",
        "spotify.com",
        "tiktok.com",
        "imdb.com",
        "hulu.com",
        "disneyplus.com",
        "amazonprimevideo.com",
        "soundcloud.com",
        "spotify.com",
    ],
    "Business": [
        "forbes.com",
        "bloomberg.com",
        "marketwatch.com",
        "linkedin.com",
        "shopify.com",
        "stripe.com",
        "salesforce.com",
        "hbr.org",
        "entrepreneur.com",
        "economist.com",
    ],
    "Government": [
        "usa.gov",
        "gov.uk",
        "un.org",
        "cdc.gov",
        "nasa.gov",
        "whitehouse.gov",
        "europa.eu",
        "fda.gov",
        "worldbank.org",
        "state.gov",
    ],
    "Health": [
        "cdc.gov",
        "mayoclinic.org",
        "webmd.com",
        "healthline.com",
        "who.int",
        "medrxiv.org",
        "nih.gov",
        "rxlist.com",
        "verywellhealth.com",
        "clevelandclinic.org",
    ],
}

CATEGORY_LABELS = list(DOMAIN_LIBRARY.keys())

POST_TEMPLATES = [
    "Useful read for today: {topic}.",
    "This is a useful resource on {topic}.",
    "Worth sharing: {topic} explained clearly.",
    "Interesting update about {topic}.",
    "I found this helpful for understanding {topic}.",
    "Strong perspective on {topic}.",
    "Relevant reading on {topic} for students and professionals.",
    "Thinking about {topic} and how it matters right now.",
    "A practical resource for {topic}.",
    "Important perspective on {topic}.",
]

TOPICS = {
    "Technology": ["AI safety", "cloud infrastructure", "cybersecurity", "data ethics", "software engineering", "open-source collaboration"],
    "News": ["election coverage", "global markets", "public policy", "climate reporting", "international affairs", "daily briefing"],
    "Education": ["online learning", "higher education", "instructional design", "curriculum innovation", "student support", "digital classrooms"],
    "Research": ["scientific reproducibility", "public health research", "machine learning methods", "advances in climate science", "peer review", "experimental design"],
    "Entertainment": ["streaming trends", "culture analysis", "digital media", "creator economy", "film discussions", "music discovery"],
    "Business": ["market strategy", "workplace innovation", "startup growth", "digital transformation", "supply chain resilience", "leadership trends"],
    "Government": ["public service delivery", "policy analysis", "civic technology", "digital governance", "transparency", "public administration"],
    "Health": ["wellness planning", "disease prevention", "mental health resources", "care quality", "population health", "healthy habits"],
}


def _weighted_domain_choice(rng: np.random.Generator, category: str | None = None) -> str:
    if category is not None:
        options = DOMAIN_LIBRARY.get(category, [])
        if not options:
            category = None
    if category is None:
        category = rng.choice(CATEGORY_LABELS)
    options = DOMAIN_LIBRARY.get(category, [])
    return rng.choice(options)


def generate_synthetic_data(n_posts: int = 1600, seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible synthetic social-media dataset for demo analytics."""
    rng = np.random.default_rng(seed)
    user_count = 240
    users = [f"U{idx:04d}" for idx in range(1, user_count + 1)]

    rows = []
    category_weights = [0.22, 0.17, 0.14, 0.13, 0.12, 0.10, 0.07, 0.05]

    for idx in range(1, n_posts + 1):
        user_id = rng.choice(users, p=np.full(user_count, 1 / user_count))
        category = rng.choice(CATEGORY_LABELS, p=np.array(category_weights) / sum(category_weights))
        domain = _weighted_domain_choice(rng, category)
        topic = rng.choice(TOPICS.get(category, ["digital media"]))
        post_text = rng.choice(POST_TEMPLATES).format(topic=topic)
        likes = int(rng.integers(5, 2400))
        comments = int(rng.integers(1, 900))
        shares = int(rng.integers(0, 1800))

        if idx % 9 == 0:
            user_id = rng.choice(users[:80])
        if idx % 13 == 0:
            domain = rng.choice(DOMAIN_LIBRARY["Technology"])
        if idx % 17 == 0:
            domain = rng.choice(DOMAIN_LIBRARY["News"])

        url = f"https://{domain}/post/{rng.integers(1000, 999999)}-{rng.integers(1000, 999999)}"
        timestamp = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 180)), hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60)))

        rows.append(
            {
                "post_id": f"P{idx:05d}",
                "user_id": user_id,
                "post_text": post_text,
                "url": url,
                "domain": domain,
                "category": category,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "timestamp": timestamp,
            }
        )

    df = pd.DataFrame(rows)
    df["engagement"] = df["likes"] + df["comments"] + df["shares"]
    df = df[["post_id", "user_id", "post_text", "url", "domain", "category", "likes", "comments", "shares", "timestamp", "engagement"]]
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def save_dataset(df: pd.DataFrame, data_path: Path | str = DATA_PATH) -> Path:
    """Persist the dataset to disk as CSV."""
    path = Path(data_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def load_data(data_path: Path | str = DATA_PATH, regenerate_if_missing: bool = True) -> pd.DataFrame:
    """Load the demo dataset and create it if it does not exist."""
    path = Path(data_path)
    if not path.exists() and regenerate_if_missing:
        df = generate_synthetic_data()
        save_dataset(df, path)
        return df
    if not path.exists():
        return pd.DataFrame(columns=["post_id", "user_id", "post_text", "url", "domain", "category", "likes", "comments", "shares", "timestamp", "engagement"])

    df = pd.read_csv(path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if "engagement" not in df.columns:
        df["engagement"] = df.get("likes", 0) + df.get("comments", 0) + df.get("shares", 0)
    return df

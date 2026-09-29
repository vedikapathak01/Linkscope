# LinkScope – Social Media Hyperlink Intelligence

## Executive Summary
LinkScope is a one-day capstone prototype designed to analyze how social-media-like posts distribute information through shared hyperlinks. The system uses a synthetic dataset to model user activity, website sharing patterns, and network relationships without requiring live scraping, authentication, or cloud infrastructure. The project demonstrates key concepts from social media analytics, including hyperlink analytics, network structure, weighted ties, and privacy-aware dashboard design.

The prototype delivers a polished local Streamlit dashboard that visualizes:
- total engagement and posting activity,
- dominant domains and categories,
- user-to-website relationships,
- website co-sharing networks,
- domain-specific source analysis, and
- privacy-aware methodology.

## Problem Statement
Modern social media platforms distribute content through hyperlinks that connect users to external information sources. These hyperlinks are not random; they often reflect specific communities, information ecosystems, and repeated patterns of trust or attention. However, without a structured analytical tool, it is difficult to understand which domains are shared repeatedly, which users contribute most to that spreading process, and how sources are connected through shared audiences.

LinkScope addresses this problem by providing a local analytics dashboard that reveals the structure of a synthetic hyperlink ecosystem. It supports exploration of source influence, network connectivity, and propagation patterns in a way that is visible, explainable, and academically meaningful.

## Motivation
The project was motivated by the need to produce a realistic but accessible social media analytics prototype within a short time frame. The goal was to simulate a real-world analytics workflow in a simplified, reproducible environment while emphasizing:
- modularity,
- visual clarity,
- academic relevance,
- ethical design,
- and immediate usability without external dependencies.

## Objectives
The primary objectives of the project were to:
1. Build a local social media hyperlink analytics dashboard in Python using Streamlit.
2. Generate a realistic synthetic dataset with repeated users, domains, and engagement patterns.
3. Identify the most highly shared domains and information-source categories.
4. Model user–website and website–website relationships via network analysis.
5. Create a transparent demo influence score for website ranking.
6. Demonstrate privacy-aware social media analytics in a prototype environment.
7. Provide a clear academic presentation suitable for a capstone demonstration.

## Project Scope and Constraints
The prototype was intentionally designed to remain within a one-day academic prototype scope. It does not include:
- live social-media scraping,
- user authentication,
- cloud deployment,
- complex ML models,
- LLM-based analysis,
- or invasive tracking.

Instead, the project prioritizes a polished MVP using synthetic data and a modular local analytics pipeline.

## System Architecture
The application follows a simple modular structure:

- app.py: main Streamlit entry point
- src/data_loader.py: synthetic dataset generation and loading
- src/analytics.py: KPIs, summary tables, and aggregation logic
- src/network_analysis.py: graph construction and Plotly visualizations
- src/utils.py: utility functions for safe numeric handling and normalization
- data/social_media_links.csv: generated synthetic dataset
- README.md: technical and academic documentation

This architecture keeps logic separated and makes the app easier to explain and extend.

## Dataset Design
The synthetic dataset contains realistic social-media-like records with fields such as:
- post_id
- user_id
- post_text
- url
- domain
- category
- likes
- comments
- shares
- timestamp

The generated dataset was designed to include:
- repeated users,
- repeated domains,
- multiple categories,
- realistic domain names,
- and time-based posting patterns.

The project uses a reproducible random seed so the dataset can be regenerated consistently. It is explicitly labeled in the interface as a Demo / Synthetic Dataset.

## Methodology
The prototype follows a practical social media analytics workflow:

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

This pipeline mirrors the conceptual sequence used in the analysis of digital information diffusion and social network behavior.

## Key Technical Components

### 1. Dashboard Overview
The landing page provides KPI cards for:
- Total Posts
- Total URLs
- Unique Users
- Unique Websites
- Total Shares
- Total Engagement

It also includes interactive visualizations for:
- top 10 most shared domains,
- domains by category,
- engagement by category,
- and posts over time.

### 2. Hyperlink Analytics
The hyperlink analytics module computes summary metrics by domain, including:
- posts,
- unique users,
- total shares,
- engagement,
- average engagement, and
- demo influence score.

These metrics are surfaced in a sortable table, making it easy to identify the leading information sources.

### 3. Demo Influence Score
A simple influence score is implemented to rank domains based on a weighted combination of normalized metrics:

Influence Score =
0.4 × normalized shares
+ 0.3 × normalized unique users
+ 0.2 × normalized engagement
+ 0.1 × normalized posts

This is clearly labeled as a Demo Influence Score and is not presented as a scientifically validated social influence metric.

### 4. User–Website Network
The project builds a bipartite user-to-website social graph using NetworkX. In this network:
- users are nodes,
- websites are nodes,
- and an edge indicates a sharing relationship.

The dashboard allows filtering by:
- minimum number of connections,
- category,
- and specific domain.

This supports the analysis of user connectivity, website centrality, and repeated source-sharing habits.

### 5. Website–Website Network
A second graph is created where websites are connected if the same users shared both domains. This network highlights information-source associations and helps identify related websites that co-occur in user behavior.

### 6. User Behavior Analysis
The system also analyzes which users:
- share the most links,
- spread content across multiple domains,
- generate the highest engagement,
- and connect different content communities.

This is presented as a Top Users table with network-aware connectivity metrics.

### 7. Information Source Analysis
Users can select a domain to examine:
- post volume,
- user count,
- total shares,
- average engagement,
- categories,
- top users,
- related websites,
- and posting activity over time.

### 8. Category Analysis
The dashboard reports category-based differences in:
- number of URLs,
- total shares,
- engagement,
- and unique users.

### 9. Search and Filter System
The sidebar allows filtering by:
- date range,
- category,
- domain,
- minimum shares,
- and minimum engagement.

This ensures that all dashboard outputs remain synchronized with the selected view.

### 10. Privacy and Ethics
A dedicated Privacy & Methodology section explains that:
- user IDs are synthetic and anonymized,
- no personally identifiable information is collected,
- precise user location is not used,
- and future real-world datasets should be handled under platform policies and privacy law.

The prototype is deliberately designed to be privacy-aware and non-invasive.

## Network Analysis Concepts Demonstrated
The project is aligned with social network analysis concepts, including:
- Nodes
- Edges
- Ties
- Degree centrality
- Betweenness centrality
- Bipartite networks
- Website co-sharing networks

These are not only visualized but also explained in the UI so that the project functions as both a dashboard and a teaching tool.

## Academic Alignment
The implementation aligns with the course learning outcomes listed in the project brief:

- CO2: Social network structure, nodes, edges, ties, visualization, and network measures
- CO3: Social media hyperlink analytics, hyperlink relationships, and hyperlink analysis
- CO4: Search and information-source analytics in the social media context
- CO5: Social information filtering, business KPIs, and privacy considerations

This makes the prototype academically meaningful, even within the constraints of a one-day capstone timeline.

## Results and Observed Prototype Findings
From the generated synthetic dataset, the prototype successfully produced a working demo environment with:
- 1600 posts,
- 240 synthetic users,
- 77 unique domains,
- and repeated sharing patterns across categories.

The dashboard is therefore capable of demonstrating real analytical behavior, even though the data are synthetic and intentionally non-real.

## Strengths
- Clean and professional UI
- Clear modular Python architecture
- Reproducible synthetic dataset
- Works fully locally with Streamlit
- Includes both network and engagement analysis
- Handles filters, missing values, and empty datasets gracefully
- Maintains privacy-aware design

## Limitations
- Synthetic data does not reflect actual platform behavior.
- No real follower metrics or influence data are available.
- The demo influence score is heuristic rather than validated.
- The project is intentionally limited to a local prototype and is not production-ready.

## Future Scope
Possible extensions include:
- integration with a real social media dataset under proper policy compliance,
- more advanced community detection,
- topic modeling for shared content,
- richer time-series forecasting,
- and improved influence scoring with weighted audience metrics.

## Conclusion
LinkScope successfully demonstrates how social media hyperlink analytics can be modeled in a lightweight, explainable, and academically relevant way. It combines data generation, dashboard design, hyperlink analysis, network modeling, and privacy-aware reporting into a single local prototype that can be run and demonstrated quickly.

The project fulfills the intended objective of producing a polished one-day college capstone demo that is both technically functional and pedagogically meaningful.

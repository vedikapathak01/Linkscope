# LinkScope – Social Media Hyperlink Intelligence

## 1. Project Title
LinkScope – Social Media Hyperlink Intelligence

## 2. Problem Statement
Social media users share many hyperlinks every day, but the underlying source ecosystems are often invisible. Without a structured view of what domains are being repeated, which users contribute to those repeated patterns, and how websites connect through user behavior, it is difficult to understand how information sources spread across social media.

## 3. Motivation
The goal of this project is to provide a quick, academically meaningful prototype for understanding hyperlink propagation and social-information dynamics. Instead of depending on external APIs or live scraping, the prototype uses a reproducible synthetic dataset to demonstrate social media analytics in a local, explainable, and privacy-aware way.

## 4. Objectives
- Identify the most shared website domains in a social media-like environment.
- Map user-to-website and website-to-website relationships.
- Analyze engagement and domain influence using a demo influence score.
- Support filtering by date, category, domain, and minimum activity thresholds.
- Demonstrate network concepts relevant to social media analytics.

## 5. Features
- Overview dashboard with KPI cards and interactive charts
- Hyperlink analytics table with influence scoring
- User–website bipartite network visualization
- Website co-sharing network visualization
- User behavior analysis and top-user rankings
- Information source drill-down for selected domains
- Category analysis and timeline views
- Privacy and methodology documentation

## 6. Architecture
The project follows a simple, modular structure:

- app.py: Streamlit dashboard entry point
- src/data_loader.py: synthetic dataset generation and loader
- src/analytics.py: dashboard metrics and aggregation logic
- src/network_analysis.py: NetworkX graph creation and Plotly visualizations
- src/utils.py: reusable helper functions
- data/social_media_links.csv: demo dataset

## 7. Technologies
- Python
- Streamlit
- Pandas
- NumPy
- NetworkX
- Plotly

## 8. Dataset Description
This project uses a synthetic dataset designed for one-day demonstration purposes. It contains approximately 1,600 social-media-like posts with fields including:

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

The dataset intentionally uses anonymized user IDs and realistic domains spanning categories such as:
- Technology
- News
- Education
- Research
- Entertainment
- Business
- Government
- Health

The application clearly labels this as a Demo / Synthetic Dataset.

## 9. Methodology
The prototype implements a simplified social-media analytics pipeline:

1. Social Media Posts
2. URL Extraction
3. Domain Identification
4. Data Cleaning
5. Hyperlink Analytics
6. Network Construction
7. Centrality & Influence Analysis
8. Visualization & Insights

This flow mirrors common social media analytics tasks while remaining comprehensible for a prototype demonstration.

## 10. Network Analysis Techniques
The system uses NetworkX to model social relationships in two ways:

- Bipartite network: users to websites
- Website co-sharing network: website-to-website links based on overlapping users

Key concepts showcased include:
- Nodes
- Edges
- Ties
- Degree centrality
- Betweenness centrality
- Bipartite networks
- Weighted relationships

## 11. Influence-Score Formula
The demo influence score is a transparent prototype metric defined as:

Influence Score =
0.4 × normalized shares
+ 0.3 × normalized unique users
+ 0.2 × normalized engagement
+ 0.1 × normalized posts

This is intentionally labeled as a Demo Influence Score and should not be interpreted as a scientifically validated ranking model.

## 12. Installation Instructions
1. Clone or download the project folder.
2. Open a terminal in the project directory.
3. Create a virtual environment (recommended):
   python -m venv .venv
4. Activate the environment:
   - macOS/Linux: source .venv/bin/activate
5. Install dependencies:
   pip install -r requirements.txt

## 13. How to Run
From the project root, run:

streamlit run app.py

Then open the local Streamlit URL shown in the terminal, typically:

http://localhost:8501

## 14. Screenshots Section Placeholder
Screenshots will be added in a later version once the dashboard is demonstrated in a presentation or report.

## 15. Limitations
- The dataset is synthetic and does not represent real social media activity.
- No live scraping or API integration is included.
- The influence score is a demonstration metric, not a validated academic measure.
- The network is bounded by the synthetic dataset and does not capture real-world follower dynamics.

## 16. Future Scope
- Real social-media API integration under policy-compliant conditions
- User clustering and community detection
- Topic modeling for shared hyperlink content
- More advanced engagement and influence metrics
- Deployment with a lightweight backend and database

## 17. Academic Alignment
This prototype aligns with course concepts in social media analytics, including:

- CO2: social network structure, nodes, edges, ties, visualization, and measures
- CO3: hyperlink analytics and hyperlink relationships
- CO4: search/information-source analytics and source discovery
- CO5: social information filtering, business KPIs, and privacy considerations

## 18. Privacy and Ethics
The demo emphasizes privacy-aware design by using synthetic and anonymized IDs and by avoiding real tracking or profiling. In future real-world work, all data handling should follow platform policies and applicable privacy laws.

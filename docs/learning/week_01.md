# DDIA Learning Log: Chapters 1-3

## Chapter 1: Reliability, Scalability, and Maintainability
* **Reliability:** Systems must remain functional even during hardware or software faults. In our project, we handle this by using `try-except` blocks and structured logging in `main.py`.
* **Scalability:** Handling increased load. We define load parameters (like transactions per second) to determine when to scale our Postgres or Airflow services.
* **Maintainability:** Making systems easy for teams to work on. We use **uv** for deterministic environments and **Docker** for environment parity.

## Chapter 2: Data Models and Query Languages
* **Relational vs. Document:** Why we chose **Postgres** (Relational) for banking data. Financial data requires strict schemas and ACID compliance, which fits the Relational model perfectly.
* **Query Languages:** Comparing imperative code (like our Python logic) to declarative SQL. SQL allows the database optimizer to decide the best way to retrieve data.

## Chapter 3: Storage and Retrieval
* **Log-Structured Storage (LSM-Trees):** Optimized for high-write throughput. This is the foundation of many modern NoSQL databases.
* **Page-Oriented Storage (B-Trees):** The foundation of **Postgres**. Understanding how indexes work here will help us optimize our "Silver" layer queries in Month 3.
* **OLTP vs. OLAP:** * **OLTP:** Our current Postgres setup for handling individual transactions.
    * **OLAP:** How we will eventually structure our "Gold" layer for big data analytics.

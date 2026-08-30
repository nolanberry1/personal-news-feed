# Personal News Feed — Development Handoff

Last updated: August 30, 2026

---

# 1. Project Overview

## What this project is

Personal News Feed is a local-first personal news aggregation system.

The long-term goal is to collect news from multiple sources, normalize and store the articles, identify which articles are reporting on the same underlying story, and eventually rank/filter/summarize those stories according to the user's interests.

The core idea is:

    News Sources
        ↓
    RSS ingestion
        ↓
    Normalize / deduplicate
        ↓
    SQLite article database
        ↓
    Text processing / embeddings
        ↓
    Story matching / clustering
        ↓
    Story-level news feed
        ↓
    Future ranking / personalization / presentation

The project is intentionally being developed incrementally. The current priority is getting the underlying news ingestion, storage, and story-identification architecture correct before building a sophisticated user-facing feed.

---

# 2. Development Philosophy

This is currently a local-first development project.

The developer runs the application and tests locally, then commits and pushes working changes to GitHub.

GitHub is the canonical backup/version-control repository.

Repository:

    nolanberry1/personal-news-feed

Current branch:

    main

Current HEAD:

    9adf663

Current HEAD message:

    Add news ingestion storage and story clustering

At the end of the current work session:

    local branch == origin/main
    working tree is clean

---

# 3. Current Git History

Recent commits:

    9adf663 Add news ingestion storage and story clustering
    9fa6b88 Add RSS ingestion and source registry
    7b4ced3 Remove accidental file
    26406f7 Initialize news feed project

The latest commit contains:

    12 files changed
    601 insertions

The latest commit added:

    app/ingestion/run.py
    app/storage/__init__.py
    app/storage/articles.py
    app/storage/database.py
    app/storage/report.py
    app/stories/clusters.py
    app/stories/matches.py
    app/stories/text.py
    tests/test_clusters.py
    tests/test_database.py
    tests/test_text.py

It also updated:

    .gitignore

---

# 4. Current Repository Structure

Current meaningful application structure:

    app/
    ├── evidence/
    │   └── __init__.py
    │
    ├── ingestion/
    │   ├── __init__.py
    │   ├── check_sources.py
    │   ├── rss.py
    │   └── run.py
    │
    ├── ranking/
    │   └── __init__.py
    │
    ├── storage/
    │   ├── __init__.py
    │   ├── articles.py
    │   ├── database.py
    │   └── report.py
    │
    ├── stories/
    │   ├── __init__.py
    │   ├── clusters.py
    │   ├── matches.py
    │   └── text.py
    │
    ├── triage/
    │   └── __init__.py
    │
    └── main.py

Tests:

    tests/
    ├── test_clusters.py
    ├── test_database.py
    ├── test_rss.py
    ├── test_sources.py
    └── test_text.py

---

# 5. Ingestion Architecture

## app/ingestion/rss.py

This module handles RSS/Atom ingestion.

It defines:

    RSSItem

with:

    title
    url
    published_at
    summary
    source_name
    external_id

It also handles:

- URL normalization
- publication timestamp parsing
- RSS/Atom fetching
- removal of duplicate URLs within a feed
- conversion of feed entries into normalized RSSItem objects

RSS feeds are fetched using HTTPX and parsed with feedparser.

URLs are normalized before storage/comparison.

---

## app/ingestion/run.py

This is the ingestion runner.

Flow:

    config.sources.SOURCES
        ↓
    fetch_feed()
        ↓
    save_article()
        ↓
    SQLite

For every configured source it:

1. Fetches the feed.
2. Normalizes the feed entries.
3. Attempts to save each article.
4. Counts fetched articles.
5. Counts newly inserted articles.
6. Prints source-level results.
7. Continues if an individual source fails.

Database initialization happens before ingestion.

The intended execution path is:

    python -m app.ingestion.run

---

# 6. Storage Architecture

SQLite is currently the persistence layer.

Database path:

    data/news.db

The database module creates the directory automatically if necessary.

## articles table

Current schema:

    id INTEGER PRIMARY KEY AUTOINCREMENT
    source_name TEXT NOT NULL
    external_id TEXT
    title TEXT NOT NULL
    url TEXT NOT NULL
    published_at TEXT
    summary TEXT
    discovered_at TEXT NOT NULL
    url_hash TEXT NOT NULL UNIQUE

Indexes currently exist for:

    published_at
    source_name

---

## Deduplication

Article URLs are hashed using SHA-256.

The hash is stored as:

    url_hash

The database enforces uniqueness on this field.

Article insertion uses:

    INSERT OR IGNORE

Therefore an article whose normalized URL has already been stored will not be inserted again.

This currently makes URL-based deduplication the primary storage-level duplicate protection mechanism.

---

# 7. Storage Utilities

## app/storage/articles.py

Responsible for article persistence.

Important functions:

    make_url_hash(url)
    save_article(item)

`save_article()` returns:

    True

when a new article was inserted, and:

    False

when the article was already present.

---

## app/storage/report.py

Provides a basic database report.

It currently reports:

- total stored articles
- articles by source
- 25 most recently stored articles

This is primarily a development/debugging utility at the moment.

---

# 8. Text / Semantic Similarity Architecture

## app/stories/text.py

This module provides text normalization and semantic similarity utilities.

The current embedding model is:

    all-MiniLM-L6-v2

from Sentence Transformers.

The model is cached with:

    @lru_cache(maxsize=1)

so the embedding model is loaded once per process.

Current utilities include:

    normalize_headline()
    tokenize_headline()
    headline_similarity()
    get_embedding_model()

`headline_similarity()`:

1. Encodes two headlines.
2. Normalizes the embeddings.
3. Calculates their dot product.
4. Uses that as cosine similarity.
5. Converts very low values to 0.
6. Bounds the result to approximately 0–1.

The current story-clustering work uses the same embedding model directly.

---

# 9. Story Matching

## app/stories/matches.py

This module was created as an exploratory tool for identifying strong cross-source headline matches.

It compares article headlines pairwise.

Important rule:

    Articles from the same source are never compared.

Exact duplicate headlines are also skipped.

The output is sorted by similarity score and displays the strongest 30 matches.

This was useful for exploring whether headline embeddings could identify stories reported by different sources.

This module is currently more of a diagnostic/exploration tool than part of the production feed pipeline.

---

# 10. Story Clustering

## app/stories/clusters.py

This is the main story-clustering implementation currently committed.

It defines:

    StoryCluster

with:

    articles
    embeddings

and properties:

    sources
    headline
    centroid

The clustering process is currently:

1. Generate embeddings for all article titles.
2. Process articles sequentially.
3. Compare each article against existing cluster centroids.
4. Never add an article to a cluster containing another article from the same source.
5. Select the existing cluster with the highest similarity.
6. Add the article if similarity exceeds the configured threshold.
7. Otherwise create a new cluster.
8. Sort the final clusters deterministically by cluster size and headline.

The current committed threshold is:

    SIMILARITY_THRESHOLD = 0.60

---

# 11. Important Clustering Design Rule

A story cluster may contain only one article from any given source.

Example:

    NPR article
    BBC article
    CBS article
    Guardian article

can belong to the same cluster.

But:

    NPR article A
    NPR article B

cannot belong to the same cluster.

The purpose is to prevent a source that publishes multiple related articles from dominating the representation of a story.

This rule should not be removed casually. It was deliberately introduced as part of the story-clustering design.

---

# 12. Clustering Experiments Performed Today

The database contained:

    340 articles

Using the committed clustering implementation with:

    threshold = 0.60

produced:

    280 clusters

Using an experimental threshold:

    threshold = 0.70

produced:

    303 clusters

The 0.70 experiment was NOT committed as the production threshold.

It was only used for evaluation.

---

# 13. Nepal/Tibet Experiment

A subset of articles containing "Nepal" or "Tibet" in their headlines was used to evaluate clustering.

At threshold 0.70, the system produced 19 clusters from the relevant articles.

Several groups looked reasonable.

For example, one cluster grouped:

    NPR — Nepal warns of possible fresh flooding...
    CBS — Nepal on high alert for fresh flooding...
    PBS — Nepal warns of possible fresh flooding...
    BBC — Satellite images reveal scale of flood devastation...
    Guardian — Nepal-Tibet floods...

Another grouped articles focused more specifically on missing people:

    NBC — Fears of more flooding in Nepal...
    CBS — Nearly 3,000 still missing...
    Guardian — Search continues...
    France 24 — Nepal: Hopes fade for thousands still missing

This revealed an important distinction:

The embedding system can identify semantically related coverage, but related coverage does not necessarily mean that every article belongs to exactly the same story/event cluster.

Some Nepal/Tibet articles were about:

- the initial disaster
- missing people
- rescue operations
- the threat of another flood
- individual survivor stories
- political/China information restrictions
- humanitarian impact

This distinction needs to be addressed in the future.

---

# 14. Major Discovery: Current Clustering Is Order-Dependent

We explicitly tested the same Nepal/Tibet article set twice:

1. Normal database order
2. Reverse database order

The resulting cluster membership changed.

For example, in normal order one cluster contained five articles:

    NPR
    CBS
    PBS
    BBC
    Guardian

In reverse order, that same group contained only four:

    BBC
    PBS
    CBS
    NPR

Other articles moved between clusters as well.

Therefore:

    cluster_articles(articles)

is currently dependent on the order in which `articles` is supplied.

This is a known flaw in the current algorithm.

The reason is that the algorithm is greedy and incremental:

    article → compare against current clusters → choose best → update centroid

Because the centroid changes as articles are added, processing an article earlier can affect the cluster that later articles see.

This needs to be fixed or deliberately replaced before story clustering should be considered reliable.

---

# 15. Current Clustering Problem

The biggest technical issue discovered today is NOT simply the threshold.

Changing:

    0.60 → 0.70

changes cluster count, but it does not solve the underlying problem.

The deeper issue is:

    greedy incremental centroid clustering is order-dependent.

Therefore future work should focus on the clustering algorithm itself before spending too much time tuning the threshold.

Potential future approaches to investigate include:

- pairwise similarity graph + connected components
- graph clustering with a similarity threshold
- agglomerative clustering
- constrained clustering
- representative/medoid-based clustering
- two-stage candidate matching followed by cluster formation

No replacement algorithm has been selected yet.

Do not assume one has been chosen.

---

# 16. Current Test Status

Latest test command:

    PYTHONPATH=. pytest -q

Result:

    14 passed in 5.19s

This is the current known-good baseline.

Do not consider clustering changes complete unless the test suite still passes.

---

# 17. Current .gitignore

The `.gitignore` now excludes:

    .venv/
    __pycache__/
    *.py[cod]
    .env
    .env.*
    !.env.example
    .pytest_cache/
    .DS_Store

The local SQLite database was also removed from tracking/status before the final commit.

The database itself should remain local development state rather than being committed to Git.

---

# 18. Things That Were Intentionally NOT Committed

During experimentation, temporary clustering files existed:

    app/stories/clusters.py.backup
    app/stories/clusters.py.before-centroid
    app/stories/clusters.py.experiment

These were removed before the final commit.

The production code is therefore only:

    app/stories/clusters.py

Do not recreate or rely on those temporary files unless intentionally running a new experiment.

---

# 19. Current Application Areas That Are Mostly Placeholders

These directories currently exist but have not yet received substantial implementation:

    app/evidence/
    app/ranking/
    app/triage/

These are likely future layers.

Their intended roles have not yet been fully designed.

Do not invent architecture for these areas prematurely.

---

# 20. Architecture We Should Preserve

The current separation of concerns is intentional:

    ingestion
        ↓
    storage
        ↓
    stories
        ↓
    future ranking / triage / evidence

The ingestion layer should not contain story-clustering logic.

The storage layer should not contain ranking logic.

Story identification should operate on stored article data rather than directly on RSS feeds.

This separation should make it possible to change the clustering algorithm without rewriting ingestion or database persistence.

---

# 21. Current State of the Project

At the end of this work session:

- RSS ingestion exists.
- RSS entries are normalized.
- URLs are normalized.
- Articles are persisted in SQLite.
- URL-based deduplication exists.
- Database reporting exists.
- Sentence-transformer embeddings exist.
- Headline semantic similarity exists.
- Pairwise cross-source matching exists as a diagnostic tool.
- Story clustering exists.
- Same-source articles are prohibited from sharing a cluster.
- 14 automated tests pass.
- 340 articles were available for clustering experiments.
- The current committed clustering threshold is 0.60.
- A 0.70 experiment was evaluated but not committed.
- Clustering has been proven to be order-dependent.
- The next major technical task is to improve/rethink story clustering.

---

# 22. What NOT to Do Next

Do NOT immediately:

- build a UI
- build sophisticated ranking
- tune dozens of arbitrary similarity thresholds
- assume every semantically similar headline is the same story
- assume the current clustering algorithm is good enough because it produces plausible groups
- delete the same-source constraint
- commit the local SQLite database
- reintroduce experimental backup files

The current priority should be making story identification technically sound.

---

# 23. Recommended Next Development Sequence

When development resumes:

### Step 1

Review the current clustering implementation and tests.

### Step 2

Write tests that explicitly capture the order-dependence problem.

The desired test should prove that clustering the same articles in different orders either:

- produces equivalent clusters, or
- documents why order-dependence is intentionally accepted.

The preferred outcome is order-independent clustering.

### Step 3

Evaluate alternative clustering strategies.

Use the Nepal/Tibet dataset as a concrete evaluation set.

### Step 4

Compare algorithms using real examples from the database.

Do not judge the algorithm only by total cluster count.

Evaluate:

- obvious duplicates
- same event / different angle
- related but distinct stories
- unrelated stories with similar vocabulary
- multiple articles from one source
- evolving stories over time

### Step 5

Once the clustering approach is selected, update the implementation and tests.

### Step 6

Only after clustering is reasonably reliable should we move into:

    story ranking
    story selection
    evidence
    triage
    user-facing feed

---

# 24. Useful Commands

Activate the environment:

    source .venv/bin/activate

Run tests:

    PYTHONPATH=. pytest -q

Inspect repository state:

    git status

Inspect recent commits:

    git log --oneline --decorate -5

Run ingestion:

    PYTHONPATH=. python -m app.ingestion.run

Inspect database:

    PYTHONPATH=. python -m app.storage.report

Run headline matching:

    PYTHONPATH=. python -m app.stories.matches

Run clustering against all articles:

    PYTHONPATH=. python - <<'PY'
    from app.storage.database import get_connection
    from app.stories.clusters import cluster_articles

    conn = get_connection()

    articles = list(conn.execute("""
        SELECT id, source_name, title
        FROM articles
        ORDER BY id
    """).fetchall())

    clusters = cluster_articles(articles)

    print(f"Articles: {len(articles)}")
    print(f"Clusters: {len(clusters)}")

    for i, cluster in enumerate(clusters, 1):
        if len(cluster.articles) < 2:
            continue

        print()
        print(f"Cluster {i} ({len(cluster.articles)} articles)")

        for article in cluster.articles:
            print(
                f"[{article['source_name']}] "
                f"{article['title']}"
            )
    PY

---

# 25. Resume Prompt — Short

Use this when returning to the project and you want to quickly get back into context:

"Open the personal-news-feed project and read SESSION_HANDOFF.md. Treat it as the canonical development handoff. First summarize the current architecture, current known-good state, and the clustering problem we discovered. Do not make changes yet. Then tell me the single best next development step."

---

# 26. Resume Prompt — Deep Technical

Use this when we want to continue technical development:

"We are continuing development of the personal-news-feed project.

First read SESSION_HANDOFF.md and inspect the current repository/code rather than relying on memory.

The current major problem is story clustering. The existing implementation in app/stories/clusters.py uses greedy incremental centroid clustering with a same-source exclusion rule. We tested the same Nepal/Tibet articles in normal and reverse order and demonstrated that cluster membership changes, proving that the algorithm is order-dependent.

Do not immediately change the code.

First:
1. Explain exactly why the current algorithm is order-dependent.
2. Review the existing clustering tests.
3. Identify what properties a better clustering algorithm should guarantee.
4. Propose 2–4 viable approaches.
5. Use the existing Nepal/Tibet examples to explain the tradeoffs.
6. Recommend one approach.

Then wait for me to approve the approach before implementing it."

---

# 27. Resume Prompt — Hands-On Pair Programming

Use this when we want to work through the next task slowly:

"We are continuing the personal-news-feed project from the state documented in SESSION_HANDOFF.md.

I want to work very slowly and have you give me extremely basic, explicit terminal steps.

Before doing anything:
- read SESSION_HANDOFF.md
- inspect the relevant current files
- explain what we are about to change and why

Then give me ONE terminal command at a time.

After each command, wait for me to paste the output.

Do not assume a command succeeded.
Do not give me a long sequence of commands.
Do not modify unrelated parts of the project.

Our current priority is fixing/rethinking the order-dependent story clustering algorithm."

---

# 28. Resume Prompt — New Developer Orientation

If a new developer joins the project, give them this instruction:

"You are joining development of the Personal News Feed project.

Start by reading SESSION_HANDOFF.md from the repository root.

The document describes:
- the product idea
- current architecture
- ingestion pipeline
- database
- text/embedding system
- story matching
- story clustering
- tests
- decisions already made
- experiments already performed
- known problems
- current development priorities

Do not begin coding immediately.

First explain the system back to me in your own words, including the data flow from RSS source to stored article to story cluster.

Then explain the most important unresolved technical issue and why it matters.

Finally, identify the next recommended development task."

---

# 29. End-of-Session Checkpoint

Before beginning another development session, the developer should run:

    git status

and confirm:

    working tree clean

Then:

    git pull

Then:

    PYTHONPATH=. pytest -q

The expected baseline is:

    14 passed

If the tests do not pass, investigate that before continuing with new functionality.

---

# 30. Current Stopping Point

STOP HERE.

The project is in a safe, reproducible state.

The latest committed version is:

    9adf663

The latest known test result is:

    14 passed

The major lesson from today's clustering experiments is:

    Semantic similarity can identify related coverage,
    but the current greedy centroid clustering algorithm
    does not produce stable clusters independent of input order.

That is the point at which development should resume.


## app/stories/text.py

This module provides the semantic text-processing layer used by story clustering.

It currently uses a SentenceTransformer embedding model.

Important behavior:

- The embedding model is loaded lazily.
- Article titles are converted into vector embeddings.
- Embeddings are normalized before being returned.
- Cosine similarity can therefore be calculated using the dot product.

The current clustering implementation uses article titles only.

This is an intentional early implementation rather than the final semantic representation.

Potential future improvements include incorporating:

- article summaries
- article descriptions
- extracted article text
- named entities
- dates/events
- other structured metadata

---

# 9. Story Matching Architecture

## app/stories/matches.py

This module contains the lower-level semantic matching logic.

The basic concept is:

    Article A
        ↓
    embedding
        ↓
    compare against Article B
        ↓
    similarity score

The purpose of this layer is to determine whether two articles are semantically related.

Story matching is distinct from the higher-level clustering problem.

Matching asks:

    "Are these two articles similar?"

Clustering asks:

    "Which collection of articles represents the same underlying story?"

This distinction should be preserved as the project develops.

---

# 10. Current Story Clustering Implementation

## app/stories/clusters.py

The current clustering implementation uses a greedy, centroid-based approach.

For each article:

1. Generate its normalized embedding.

2. Examine existing clusters.

3. Ignore clusters that already contain an article from the same source.

4. Calculate similarity between the article embedding and each eligible cluster centroid.

5. Select the highest-scoring eligible cluster.

6. If that score meets the similarity threshold, add the article to that cluster.

7. Otherwise create a new cluster.

The current threshold in the committed code is:

    SIMILARITY_THRESHOLD = 0.60

Each cluster maintains:

    articles
    embeddings

The cluster centroid is calculated as the normalized mean of its article embeddings.

Clusters expose:

    sources
    headline
    centroid

The current headline selection is simply the longest headline in the cluster.

The final clusters are sorted deterministically by:

    number of articles, descending
    headline, ascending

---

# 11. Important Clustering Decision / Known Limitation

During development we tested a threshold of 0.70.

That was an experiment only.

The committed implementation remains:

    SIMILARITY_THRESHOLD = 0.60

The 0.70 experiment produced useful diagnostic results.

With the current database:

    340 articles
    303 clusters

At 0.70, several obvious multi-source stories clustered successfully.

For example, multiple articles about the Iceland EU referendum formed a single cluster.

However, the Nepal/Tibet flood coverage exposed a more important architectural issue.

The same set of articles was clustered twice:

    normal input order
    reversed input order

The resulting clusters were different.

This demonstrates that the current greedy algorithm is order-dependent.

That is expected behavior for the current algorithm and is NOT currently treated as a test failure.

The issue should be addressed before relying on clustering as a mature story-identification system.

---

# 12. Nepal/Tibet Diagnostic

The Nepal/Tibet experiment was particularly useful because the coverage represented an evolving event with multiple related developments.

At 0.70, the system produced multiple clusters such as:

- fresh flooding / devastation
- missing people / rescue efforts
- deaths and casualties
- individual rescue stories
- subsequent developments

Some of these distinctions may actually be useful at a story-feed level, while others may represent fragmentation that should eventually be merged.

The important lesson is:

Semantic similarity alone does not necessarily define the correct story boundary.

Future clustering should consider both:

    semantic similarity

and potentially:

    event identity
    temporal proximity
    geographic context
    entities
    source diversity
    evolving-story relationships

Do not assume that increasing or decreasing the similarity threshold alone will solve this.

---

# 13. Same-Source Constraint

The clustering algorithm currently prevents two articles from the same source from being placed in the same cluster.

Rationale:

If five articles from one publisher all describe the same event, they should not artificially dominate a story cluster.

This constraint is useful for the eventual personal news feed because a story should ideally represent independent coverage from multiple sources.

However, the constraint also interacts with clustering order and can contribute to fragmentation.

This should be considered when redesigning the clustering algorithm.

---

# 14. Current Tests

The current test suite covers:

    RSS ingestion behavior
    source registry behavior
    database behavior
    text embedding behavior
    story clustering behavior

Current test command:

    PYTHONPATH=. pytest -q

At the end of this development session:

    14 passed

No tests were failing.

The tests currently establish the basic behavior of the implemented modules but do not yet fully validate whether clusters correspond to human judgments of "the same story."

That higher-level evaluation remains future work.

---

# 15. What Was Completed During This Development Session

This session established the first meaningful end-to-end backend architecture for the project.

Completed:

- RSS ingestion already established from the previous development stage.
- Article normalization and persistence.
- SQLite database initialization.
- URL-based article deduplication.
- Article reporting/debugging utilities.
- Lazy semantic embedding model.
- Article title embeddings.
- Pairwise semantic story matching.
- Initial story clustering.
- Same-source protection inside clusters.
- Cluster centroid calculation.
- Deterministic cluster sorting.
- Automated tests for the new storage/text/clustering functionality.
- `.gitignore` cleanup to prevent local databases and generated artifacts from being committed.
- Git commit and push to GitHub.
- Development handoff documentation.

---

# 16. Current Architecture — End to End

The current backend should be understood as:

    CONFIGURED SOURCES
            |
            v
    app/ingestion/rss.py
            |
            v
    NORMALIZED RSS ITEMS
            |
            v
    app/ingestion/run.py
            |
            v
    app/storage/articles.py
            |
            v
    SQLite: data/news.db
            |
            v
    app/stories/text.py
            |
            v
    TITLE EMBEDDINGS
            |
            v
    app/stories/matches.py
            |
            v
    SEMANTIC RELATIONSHIPS
            |
            v
    app/stories/clusters.py
            |
            v
    STORY CLUSTERS
            |
            v
    FUTURE STORY RANKING
            |
            v
    FUTURE PERSONAL NEWS FEED

There are currently placeholder package areas for:

    app/evidence/
    app/ranking/
    app/triage/

These represent future architectural areas rather than mature functionality.

---

# 17. What Does NOT Exist Yet

The following should NOT be assumed to be implemented:

- sophisticated story/event identity
- production-quality clustering
- article body extraction
- evidence aggregation
- story-level ranking
- personalization
- user preference modeling
- duplicate-story resolution across time
- story lifecycle management
- web UI
- API layer
- scheduled production ingestion
- cloud deployment
- production database
- authentication
- user accounts

The project is still primarily a local backend/data-processing prototype.

---

# 18. Known Problems / Earmarked Future Work

## High priority

### 1. Make clustering order-independent

The current greedy algorithm produces different results depending on article input order.

This is the most important known technical issue from this session.

Possible approaches to investigate:

- pairwise similarity graph + connected components
- hierarchical/agglomerative clustering
- community detection
- constrained clustering
- deterministic batch clustering
- improved centroid assignment
- explicit merge/split passes

Do not immediately choose one without first understanding the desired definition of "same story."

### 2. Establish what a "story" actually means

Before optimizing clustering too aggressively, define the desired story boundary.

Questions to answer:

- When are two articles about the same event?
- How should an evolving event behave over multiple days?
- Should separate developments within a disaster be one story or several?
- How much temporal separation is acceptable?
- Should follow-up stories remain attached to the original story?
- How should related-but-distinct events be separated?

### 3. Improve semantic representation

Currently only article titles are embedded.

Investigate whether story identification improves by incorporating:

- summaries
- descriptions
- article text
- named entities
- locations
- dates
- extracted event information

### 4. Evaluate clustering against human judgments

Create a small labeled evaluation set containing:

    article A
    article B
    same story? yes/no

and eventually:

    article set
    expected story grouping

Use this to compare clustering approaches rather than relying only on anecdotal examples.

---

# 19. Medium / Lower Priority Future Work

Potential future work includes:

- Better representative headline selection.
- Better source diversity handling.
- Story-level metadata.
- Story timestamps.
- Story lifecycle / merging over time.
- Handling articles that belong to multiple related developments.
- Evidence aggregation.
- Source credibility / quality considerations.
- Ranking stories by user interest.
- Personalization.
- Feed presentation.
- Web/API interface.
- Scheduled ingestion.
- Database retention policies.
- Monitoring and logging.
- Production deployment.

These should generally come after the story model and clustering behavior are better defined.

---

# 20. Important Files for a New Developer

Start here:

    app/ingestion/rss.py
        Understand how external news becomes normalized RSSItem objects.

    app/ingestion/run.py
        Understand the ingestion pipeline.

    app/storage/database.py
        Understand SQLite initialization and schema.

    app/storage/articles.py
        Understand article persistence and deduplication.

    app/storage/report.py
        Useful for inspecting database contents.

    app/stories/text.py
        Understand embeddings.

    app/stories/matches.py
        Understand semantic article matching.

    app/stories/clusters.py
        Understand the current story clustering algorithm.

Then review:

    tests/test_rss.py
    tests/test_sources.py
    tests/test_database.py
    tests/test_text.py
    tests/test_clusters.py

The tests are important because they document intended behavior better than assumptions in this handoff document.

---

# 21. How to Resume Development

Activate the environment:

    source .venv/bin/activate

Run the tests:

    PYTHONPATH=. pytest -q

Check repository state:

    git status

Review recent commits:

    git log --oneline --decorate -5

The expected baseline is:

    HEAD == origin/main
    working tree clean

Before changing clustering, read:

    app/stories/clusters.py
    app/stories/matches.py
    app/stories/text.py
    tests/test_clusters.py

Then reproduce the order-dependence experiment before modifying the algorithm.

The goal is to understand the failure mode first, then design a better clustering approach.

---

# 22. Recommended Next Development Session

The next session should focus on story clustering rather than the UI.

Suggested sequence:

1. Re-read this handoff.

2. Inspect the current clustering and matching code.

3. Re-run the Nepal/Tibet experiment.

4. Reproduce the normal-vs-reverse-order difference.

5. Explain precisely why the current greedy centroid algorithm produces that behavior.

6. Define the desired semantics of a "story."

7. Compare several candidate clustering architectures.

8. Choose an approach based on the project's actual requirements.

9. Add tests that capture the desired behavior.

10. Implement the improved algorithm.

11. Re-run the full test suite.

12. Re-run the real 340-article dataset.

13. Compare the resulting clusters with the previous implementation.

Do NOT move directly into UI development until the story model is sufficiently trustworthy.

---

# 23. Developer Prompt — Quick Resume

Use this prompt at the beginning of a future session:

"Resume development of my Personal News Feed project from SESSION_HANDOFF.md.

First read and understand the handoff document and current repository state. Do not assume anything beyond what is documented.

Our current Git baseline is commit 9adf663, 'Add news ingestion storage and story clustering'. The working tree was clean and origin/main matched HEAD.

The immediate unfinished problem is story clustering. The current implementation in app/stories/clusters.py is a greedy centroid-based algorithm with SIMILARITY_THRESHOLD = 0.60 and a same-source constraint.

We tested 0.70 experimentally. The important finding was that clustering the same Nepal/Tibet article set in normal order versus reverse order produced different cluster membership. Therefore the current algorithm is order-dependent.

Before changing code:
1. inspect the current clustering/matching/text implementation and tests;
2. reproduce the order-dependence experiment;
3. explain exactly why it happens;
4. discuss what definition of 'same story' the system should use;
5. propose candidate solutions;
6. only then implement the next change.

Do not start building the UI yet."


---

# 24. Developer Prompt — Deep Technical Resume

"Take over the Personal News Feed project as a new developer.

Read SESSION_HANDOFF.md first. Then inspect the repository's current implementation and tests.

Orient yourself to:
- the project's purpose
- the ingestion pipeline
- SQLite storage
- URL deduplication
- text embeddings
- semantic matching
- story clustering
- current tests
- architectural placeholders for evidence, ranking, and triage

Pay particular attention to app/stories/clusters.py.

The current implementation is greedy and centroid-based. It prevents articles from the same source from occupying the same cluster. The committed similarity threshold is 0.60.

A 0.70 experiment showed that the same 340-article dataset produced different clustering behavior when article order was reversed. A focused Nepal/Tibet experiment demonstrated the same issue.

Treat this as the primary known architectural limitation.

Do not modify code immediately. First provide:
1. your understanding of the existing implementation;
2. the exact source of order dependence;
3. the strengths and weaknesses of the current approach;
4. several viable replacement approaches;
5. the tradeoffs of each;
6. what additional tests should be written;
7. your proposed implementation plan.

Wait for agreement before making substantial architectural changes."


---

# 25. Developer Prompt — Continue Hands-On

"Continue working directly on my Personal News Feed repository from SESSION_HANDOFF.md.

Assume I am working locally from the project root with the virtual environment activated.

Start by checking:
    git status
    git log --oneline --decorate -5
    PYTHONPATH=. pytest -q

Then inspect the current clustering implementation and tests.

The immediate objective is to fix or redesign the order-dependent story clustering behavior discovered during the Nepal/Tibet experiment.

Do not touch unrelated parts of the application.

Work incrementally:
- reproduce the problem;
- add a regression test;
- make the smallest sensible architectural change;
- run the relevant tests;
- run the full suite;
- inspect real clustering output;
- explain what changed and why.

Do not assume that simply changing SIMILARITY_THRESHOLD is the correct solution."


---

# 26. Definition of the Current Stopping Point

This session is considered successfully complete when:

    Code is committed.
    Code is pushed to GitHub.
    Working tree is clean.
    Tests pass.
    SESSION_HANDOFF.md documents the architecture.
    SESSION_HANDOFF.md documents the known clustering limitation.
    SESSION_HANDOFF.md identifies the next development objective.
    A future session can resume without reconstructing today's work from memory.

Current known state:

    Git baseline:
    9adf663

    Branch:
    main

    Remote:
    origin/main

    Tests:
    14 passed

    Known clustering issue:
    Order-dependent greedy clustering

    Current threshold:
    0.60

    Experimental threshold:
    0.70

    Next major task:
    Redesign/evaluate story clustering.

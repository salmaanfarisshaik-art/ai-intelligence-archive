# AI Intelligence Archive: Autonomous & Self-Updating

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![Status](https://img.shields.io/badge/status-autonomous%20bot%20active-success)
![Architecture](https://img.shields.io/badge/architecture-deterministic-orange)
![Frontend](https://img.shields.io/badge/frontend-Next.js%20Static-black)
![License](https://img.shields.io/badge/license-MIT-green)

Welcome to the **AI Intelligence Archive**—a fully autonomous, self-updating, serverless ecosystem intelligence platform. This repository is not just a static collection of data; it is an active, deterministic machine that continuously scours, ingests, analyzes, and visualizes the rapidly evolving artificial intelligence landscape.

**Completely Serverless & Database-Free:** Powered entirely by Python, GitHub Actions, and Next.js Static Export.

---

## 🤖 The Autonomous Bot Engine

This repository runs itself. Using GitHub Actions, it operates on a continuous scheduled loop:

1. **Ingest & Expand:** Wakes up every 6 hours and pulls massive datasets of new AI models, datasets, tools, and research papers from HuggingFace, arXiv, and GitHub APIs.
2. **Deterministic Processing (Phase 9):** Runs a Python pipeline to map relationships, build semantic search indices, and compile a massive knowledge graph.
3. **Automated Version Control:** Automatically commits new findings directly to the `main` branch under the maintainer's GitHub profile.
4. **Static Frontend Compilation (Phase 10):** Instantly triggers a Next.js build to statically export over 1,000+ interactive analytical pages.
5. **Zero-Touch Deployment:** Pushes the compiled frontend directly to GitHub Pages.

---

## 📊 Archive Scale & Statistics

The pipeline currently processes and organizes massive amounts of intelligence:

- **🤖 Models:** 2,000+
- **📚 Datasets:** 2,080+
- **🧰 AI Tools:** 4,248+
- **🔌 APIs & AI Services:** 3,200+
- **📝 Prompt Templates & Workflows:** 80,000+
- **🧠 Knowledge Graph Relationships:** 50,000+
- **⚡ Static Pages Generated:** 1,022 individual Next.js routes generated natively in ~11 seconds.

---

## 🏗️ Step-by-Step Construction & Architecture

This repository was architected through 10 progressive phases, guaranteeing byte-for-byte reproducible outputs and total modularity.

### Phases 1-8.5: The Data Foundation
A completely modular, object-oriented Python backend that fetches data from multiple external sources, validates the data against JSON schemas, and normalizes them into canonical entity records in the `data/processed/*` folder. This layer uses massive deduplication and cross-reference matching to guarantee canonical data integrity.

### Phase 9: Intelligence & Discovery Layer
A strict read-only analytical pipeline that transforms the canonical data into optimized, frontend-ready artifacts in the `site/` directory:
- `semantic_index_builder.py` creates chunked search indices.
- `knowledge_graph_builder.py` bridges relationships across disparate datasets.
- `timeline_generator.py` plots chronological ingestion events.
- `dashboard_data_generator.py` computes macro repository statistics.
- `artifact_manifest_generator.py` signs and hashes every single artifact using SHA-256 to ensure absolute determinism.

### Phase 10: Interactive Explorer (Frontend)
A beautifully designed Next.js application sitting in the `frontend/` directory.
- Relies on a `copy-data.js` pre-build script to synchronize artifacts from the backend's `site/` directory directly into `frontend/public/site/`.
- Leverages `output: "export"` to build completely static HTML/JSON files.
- Uses `generateStaticParams` to natively compile individual entity pages (e.g. `/entity/models/gpt-4`).

---

## 📁 Complete Repository Structure

```text
ai-intelligence-archive/
│
├── .github/
│   └── workflows/
│       └── sync.yml               # 🤖 The Autonomous Bot Pipeline
│
├── data/
│   ├── metadata/                  # Central registries and schema indexing
│   └── processed/                 # Canonical Entity JSONs (Models, Datasets, Tools, etc.)
│
├── docs/                          # Architectural Decision Records (ADRs) & Docs
│
├── frontend/                      # 🌐 Next.js Interactive Explorer
│   ├── public/
│   │   └── site/                  # Automatically synchronized Phase 9 artifacts
│   ├── src/
│   │   ├── app/                   # Dynamic and Static Next.js routes
│   │   ├── components/            # UI Components (Search Modal, Graph viewers)
│   │   └── lib/                   # Shared data access layer for artifacts
│   ├── package.json               # Frontend dependencies & copy-data.js pre-build hook
│   └── next.config.ts             # Strict static export configuration
│
├── reports/                       # Deterministic build logs, integrity checks, & run manifests
│
├── schemas/                       # Authoritative JSON schemas to validate all data
│
├── scripts/                       # 🐍 Python Pipeline Source Code
│   ├── lib/                       # Generators, Validators, Indexers, & Linkers
│   ├── main.py                    # Master Orchestrator Script
│   └── massive_seed_fetcher.py    # Raw data ingestion engine
│
├── site/                          # 📦 Phase 9 Generated Artifacts (Hashed & Validated)
│   ├── search/                    # Deterministically chunked search index JSONs
│   ├── artifact_manifest.json     # Cryptographic signatures for reproducibility
│   ├── dashboard_metrics.json     # Global stats for the UI
│   ├── entity_graph.json          # Node and edge mapping
│   ├── index_manifest.json        # Frontend schema compatibility manifest
│   └── timeline.json              # Chronological event tracking
│
├── requirements.txt               # Production Python dependencies
├── requirements-dev.txt           # Testing Python dependencies
└── README.md                      # You are here!
```

---

## ⚙️ Pin-to-Pin Local Setup Guide

If you want to run the pipeline, verify determinism, or contribute to the frontend, follow this exact setup.

### 1. Clone the Repository
```bash
git clone https://github.com/salmaanfarisshaik-art/ai-intelligence-archive.git
cd ai-intelligence-archive
```

### 2. Backend Setup (Python)
The backend pipeline requires Python 3.11+.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
DRY_RUN=false
GEMINI_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_token
# Note: Do NOT commit this file to git!
```

### 4. Run the Pipeline
Execute the main orchestrator to ingest data and build the `site/` artifacts.
```bash
python scripts/main.py
```

### 5. Frontend Setup (Next.js)
Once the Python pipeline has generated the artifacts, build the Next.js visualizer.

```bash
cd frontend

# Install Node dependencies
npm install

# Run the local development server
npm run dev

# OR build the production static export
npm run build
```

---

## 🔒 Determinism & Safety Contracts

The system operates under several unbreakable architectural contracts:
- **Frontend Consumption Boundary:** The frontend is strictly forbidden from reading raw data. It may only read the hashed, validated payloads inside `site/`.
- **Atomic File Operations:** All artifacts are built in temporary paths and swapped atomically to prevent partial writes.
- **DRY_RUN Safety:** If `DRY_RUN=true` is enabled, the pipeline executes fully in memory and guarantees 0 bytes are altered on disk.
- **CI/CD Lockfile Parity:** The frontend relies on `npm install` within the `.github/workflows/sync.yml` file to handle cross-OS SWC binary dependencies seamlessly.
- **Canonical Ordering Contract:** All generated JSON arrays and objects are strictly sorted by Canonical ID, ensuring that identical inputs always generate byte-for-byte identical artifacts.

---

## 🤝 Contributing

Contributions are heavily encouraged! Whether you are adding a new data ingestion script in Python or polishing a TailwindCSS component in Next.js, the deterministic boundary ensures you can't easily break the system.

Please ensure you run `python scripts/main.py` locally and verify that the `reports/build_manifest.json` correctly hashes your outputs before submitting a Pull Request.

---
*Maintained autonomously by GitHub Actions under the @salmaanfarisshaik-art profile.*

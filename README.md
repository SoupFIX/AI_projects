<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Qdrant-Vector_DB-DC143C?style=for-the-badge&logo=qdrant&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenAI-CLIP-412991?style=for-the-badge&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>

<br/><br/>

```
██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗         ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
██║   ██║██║██╔════╝██║   ██║██╔══██╗██║         ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
██║   ██║██║███████╗██║   ██║███████║██║         ███████╗█████╗  ███████║██████╔╝██║     ███████║
╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║         ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗    ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
  ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

                         ███████╗███╗   ██╗ ██████╗ ██╗███╗   ██╗███████╗
                         ██╔════╝████╗  ██║██╔════╝ ██║████╗  ██║██╔════╝
                         █████╗  ██╔██╗ ██║██║  ███╗██║██╔██╗ ██║█████╗
                         ██╔══╝  ██║╚██╗██║██║   ██║██║██║╚██╗██║██╔══╝
                         ███████╗██║ ╚████║╚██████╔╝██║██║ ╚████║███████╗
                         ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝
```

### *Google Lens — but for your own product catalog.*

**Upload any clothing image. Find 10 visually similar products in under 20ms. No keywords. No guessing. Pure AI.**

</div>

---

## ⚡ Live Pipeline Animation

> *Every time a user uploads an image, this entire pipeline fires in under 20ms.*

<div align="center">

![Visual Search Engine Pipeline](./search_animation.svg)

</div>

The animation above shows the real-time flow: your image travels through **FastAPI → CLIP Encoder → Qdrant Vector DB**, where it's compared against 500 stored vectors using cosine similarity — and the 10 closest results shoot back to your screen almost instantly.

---

## 🧠 What Is This Project?

Imagine **Google Lens** — but self-hosted, and tuned specifically for your own product catalog.

This is a **Visual Product Search Engine** that lets users upload any clothing image and instantly surface the **10 most visually similar products** from a database — **without typing a single keyword**.

The magic lies in a deceptively simple idea:

> *Every image can be converted into a list of 512 numbers — a mathematical fingerprint called a **vector** — that captures its color, shape, style, and texture. Images that look alike have similar numbers. Finding similar products means finding similar numbers.*

Upload a red sneaker → the engine finds every other sneaker in the catalog that shares its color, silhouette, and style. Upload a tote bag → it finds tote bags. Upload a striped sweater → it finds striped sweaters. **No rules written. No tags required. The AI figures it out.**

---

## 🔬 Core Concepts — Made Simple

Before diving into the architecture, here's a concise explanation of the three technologies at the heart of this engine:

### 🔢 What Is a Vector?

A vector is simply an ordered list of numbers that encodes the **meaning** of an image:

```
Photo of a red sneaker  →  [0.21, -0.84, 0.67, 0.44, 0.98, ... 507 more numbers]
Photo of a blue jacket  →  [0.11,  0.92, 0.12, 0.77, 0.03, ... 507 more numbers]
```

Two images that *look* similar will produce *numerically similar* vectors. That is the entire foundation of this system.

---

### 🧩 What Is CLIP?

**CLIP** (Contrastive Language–Image Pretraining) is an AI model from OpenAI that was trained on 400 million image–text pairs from the internet. It learned to embed both images **and** text into the same 512-dimensional mathematical space — which means:

```
"red running shoes"  ──►  [0.21, -0.84, 0.67 ...]  ◄── 📸 Photo of red running shoes
                                     ↑
                           Nearly identical vectors
```

This is why this engine supports **both image search and text search** — CLIP converts both to vectors, and the same similarity search finds matches either way.

---

### 📐 What Is Cosine Similarity?

Cosine similarity measures the **angle** between two vectors. A smaller angle means more visual similarity:

| Score | Meaning | Angle |
|-------|---------|-------|
| `1.00` | Identical images | 0° |
| `0.95` | Highly similar | ≈ 18° |
| `0.80` | Related style | ≈ 37° |
| `0.50` | Loosely related | ≈ 60° |
| `0.00` | Completely different | 90° |

---

### 🗄️ What Is Qdrant?

Qdrant is a **vector database** — think of it as PostgreSQL, but instead of matching exact values, it matches *mathematical similarity*:

```sql
-- Normal database (exact match only):
SELECT * FROM products WHERE category = 'sneaker'

-- Qdrant (similarity match):
FIND vectors NEAREST TO [0.21, -0.84, 0.67 ...] LIMIT 10
```

Internally, Qdrant uses **HNSW** (Hierarchical Navigable Small World) graphs — a data structure that finds the nearest vectors in milliseconds even across millions of entries, without scanning every single one.

---

## 🗺️ Architecture — The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DOCKER NETWORK                             │
│                                                                     │
│   ┌──────────────┐     ┌──────────────────┐     ┌───────────────┐   │
│   │  qdrant_db   │◄────│  visual_search   │◄────│ streamlit_ui  │   │
│   │              │     │    (FastAPI)      │     │  (Frontend)   │   │
│   │ Vector Store │     │    Port 8000      │     │   Port 8501   │   │
│   │  Port 6333   │     └──────────────────┘     └───────────────┘   │
│   └──────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────┘
        ▲                         ▲                       ▲
   localhost:6333            localhost:8000          localhost:8501
        │                         │                       │
        └─────────────────────────┴───────────────────────┘
                               Your Browser
```

Three Docker containers work in harmony:

| Container | Role | Port |
|-----------|------|------|
| `qdrant_db` | Vector database — stores and searches 512-dim vectors | 6333 |
| `visual_search` | FastAPI backend — receives uploads, calls CLIP, queries Qdrant | 8000 |
| `streamlit_ui` | Streamlit frontend — the user-facing interface | 8501 |

All three are orchestrated by a single `docker-compose.yml` and share an internal Docker network, so they communicate with each other by container name — no manual networking needed.

---

## 📁 Project Structure

```
Visual_Product_Search_Engine_Project/
│
├── 🐳 docker-compose.yml           ← Orchestrates all 3 containers
├── 🐳 Dockerfile                   ← Builds the FastAPI container
├── 🐳 Dockerfile.streamlit         ← Builds the Streamlit container
├── 📋 requirements.txt             ← Python dependencies
│
├── backend/                        ← FastAPI application
│   ├── app.py                      ← Main API server — /search, /search-by-text
│   ├── clip_encoder.py             ← Loads CLIP, encodes a single image
│   ├── embedder.py                 ← CLIPEmbedder class (reusable module)
│   ├── vector_store.py             ← Qdrant client + collection setup
│   └── config.py                   ← Settings (model name, vector size, etc.)
│
├── frontend/
│   └── front_end.py                ← Space-themed Streamlit search interface
│
├── data/
│   ├── images/                     ← 500 Fashion-MNIST product images
│   └── qdrant_data/                ← Persistent Qdrant vector storage
│       └── collections/
│           └── Products/           ← 500 stored vectors live here
│
└── scripts/
    └── prepare_data.py             ← One-time script: encode images → store in Qdrant
```

Every file has a single, clear responsibility. The backend is split into focused modules so that swapping out CLIP for a different model, or Qdrant for another vector DB, requires touching only one file.

---

## 🔄 How It Works — Phase by Phase

### Phase 1 — One-Time Setup (Building the Vector Database)

This runs once via `prepare_data.py` and never needs to run again:

```
500 Fashion-MNIST images
         │
         ▼
┌─────────────────────┐
│    CLIP Encoder      │  ← openai/clip-vit-base-patch32
│  clip_encoder.py     │    Downloads from Hugging Face (~340MB)
└─────────────────────┘
         │  Converts each image to 512 floats
         ▼
┌─────────────────────┐
│   Qdrant Database   │  ← Stores: ID + vector + image path
│   vector_store.py   │
└─────────────────────┘

What gets stored in Qdrant:
┌──────┬──────────────────────────────────────────────┬────────────────────┐
│  ID  │ Vector (512 numbers)                         │ Payload (metadata) │
├──────┼──────────────────────────────────────────────┼────────────────────┤
│ 0001 │ [0.21, -0.84, 0.67, 0.44, 0.98, ...]        │ 0001_sneaker.png   │
│ 0002 │ [0.67,  0.03, 0.19, 0.81, 0.33, ...]        │ 0002_bag.png       │
│ 0003 │ [0.19, -0.81, 0.44, 0.55, 0.71, ...]        │ 0003_sneaker.png   │
│ ...  │ ...                                           │ ...                │
│ 0500 │ [0.88,  0.12, 0.91, 0.24, 0.66, ...]        │ 0500_jacket.png    │
└──────┴──────────────────────────────────────────────┴────────────────────┘
```

---

### Phase 2 — Live Search (Every User Query)

```
User uploads image (e.g. a bag photo)
         │
         ▼ POST /search
┌─────────────────────┐
│      FastAPI         │  ← app.py receives the multipart upload
│       app.py         │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│    CLIP Encoder      │  ← Same model, same 512-number space
│  clip_encoder.py     │    Converts query image → query vector
└─────────────────────┘
         │  query_vector = [0.44, -0.12, 0.88, 0.31, ...]
         ▼
┌─────────────────────┐
│  Qdrant ANN Search  │  ← "Find the 10 closest vectors
│   vector_store.py   │     using cosine similarity"
└─────────────────────┘
         │
         ▼
Top 10 results with scores
→ FastAPI returns JSON
→ Streamlit displays as a product grid
```

The entire pipeline — from upload to displayed results — completes in **under 20ms**.

---

## 🚀 Quick Start — Run in 3 Commands

### Prerequisites

- ✅ [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- ✅ ~10 GB free disk space (CLIP model weights are ~600 MB; Docker images are ~10 GB total)
- ✅ Any modern browser

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SoupFIX/AI_projects.git
```

### Step 2 — Navigate to the Project Folder

```bash
cd AI_projects/Visual_Product_Search_Engine_project
```

### Step 3 — Launch Everything

```bash
docker-compose up
```

> ⏳ **First run takes 5–6 minutes.** Docker pulls all images, and the CLIP model (~600MB) needs to download and load. Subsequent starts take ~30 seconds.

### ✅ Access the Application

Once all containers are running, open your browser:

| Service | URL | Purpose |
|---------|-----|---------|
| 🎨 **Streamlit UI** | http://localhost:8501 | Main search interface — upload images here |
| ⚡ **FastAPI Backend** | http://localhost:8000 | REST API + auto-generated interactive docs |
| 🗄️ **Qdrant Dashboard** | http://localhost:6333/dashboard | Explore the vector database directly |

### 🛑 Stopping the Application

```bash
# Clean stop — properly releases all ports
docker-compose down

# Or press Ctrl+C (2–3 times) in the terminal where compose is running
```

> 💡 Always prefer `docker-compose down` over killing the terminal. It cleanly releases ports so you don't hit `port already allocated` errors on the next start.

---

## 🔌 API Reference

### `POST /search` — Search by Image

Upload any image file and receive the 10 most visually similar products with their similarity scores.

```bash
curl -X POST "http://localhost:8000/search" \
     -F "file=@your_image.png"
```

**Response:**

```json
{
  "query_file": "your_image.png",
  "total_results": 10,
  "results": [
    { "rank": 1, "score": 0.9823, "image_path": "/images/0044_sneaker.png", "id": 44 },
    { "rank": 2, "score": 0.9712, "image_path": "/images/0118_sneaker.png", "id": 118 },
    { "rank": 3, "score": 0.9501, "image_path": "/images/0302_sneaker.png", "id": 302 }
  ]
}
```

---

### `POST /search-by-text` — Search by Text Description

Type a natural language description and find matching product images. Powered by CLIP's shared image-text vector space.

```bash
curl -X POST "http://localhost:8000/search-by-text?query=red%20running%20shoes"
```

---

### `GET /` — Health Check

```bash
curl http://localhost:8000/
# → {"message": "✅ Visual Search Engine is running!"}
```

---

## 🐳 Docker Images

Both pre-built images are publicly available on Docker Hub:

| Image | Tag | Size | Purpose |
|-------|-----|------|---------|
| `soup28/visual-product-search-engine` | `api-1.0.0` | 8.93 GB | FastAPI + CLIP + PyTorch |
| `soup28/visual-product-search-engine` | `ui-1.0.0` | 1.02 GB | Streamlit frontend |

> The API image is large because it bundles PyTorch and all CLIP neural network weights. This is a one-time download.

---

## 🛠️ Tech Stack

| Technology | Role | Why This Choice |
|------------|------|-----------------|
| **OpenAI CLIP** | Image & text → vector encoder | Understands both modalities in a unified 512-dim space |
| **Qdrant** | Vector database | Best-in-class ANN search, excellent Python client, local storage |
| **FastAPI** | REST API server | Async I/O, auto-generated Swagger docs, minimal boilerplate |
| **Streamlit** | Frontend UI | Python-native rapid development, perfect for ML demos |
| **PyTorch** | ML framework | Required by Transformers / CLIP model |
| **Docker Compose** | Container orchestration | Reproducible, portable deployment — 3 services, 1 command |
| **Fashion-MNIST** | Dataset | 70,000 labeled clothing images, ideal for product search demos |

---

## 📊 Performance Characteristics

```
Dataset:          500 Fashion-MNIST images
Vector dimensions: 512 (float32)
Index type:       HNSW (Hierarchical Navigable Small World)
Distance metric:  Cosine similarity
Search latency:   < 20ms per query
Model load time:  ~30s (CLIP, on first cold start)
Storage per image: ~2KB (vector only, excluding image files)
```

---

## 🔭 How to Extend This Project

This architecture is intentionally modular. Here are natural extensions:

- **Swap the dataset** — Replace Fashion-MNIST with your own product catalog. Update `prepare_data.py` to point at your images.
- **Scale to millions** — Qdrant handles millions of vectors natively. No code changes required — just run `prepare_data.py` on a larger dataset.
- **Add filtering** — Qdrant supports payload filters. Store product category, price, or brand in the payload and filter search results server-side.
- **Swap the encoder** — Replace CLIP with a domain-specific model (e.g. a fine-tuned ViT for furniture or electronics). Change one line in `config.py`.
- **Add text + image hybrid search** — Combine a text query vector with an image query vector by averaging them, then search. CLIP's shared space makes this trivial.

---

## 📜 License

```
PERSONAL USE & LEARNING LICENSE
────────────────────────────────────────────────────────────────────────

Copyright (c) 2024 SoupFIX

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software to:

  ✅  Run and experiment with it on their own local machine
  ✅  Read, study, and learn from the source code
  ✅  Modify it privately for personal educational purposes
  ✅  Reference specific techniques or patterns with attribution

The following are explicitly NOT permitted:

  ❌  Copying this project in whole or substantial part and publishing
      it as your own work — whether on GitHub, npm, PyPI, or elsewhere
  ❌  Submitting this project (or a close derivative) as your own for
      academic, professional, or commercial purposes
  ❌  Redistributing this project under a different name without clear,
      prominent attribution to the original author

Attribution requirement:
  Any permitted derivative or reference work must include a visible
  link to the original repository and credit to the original author.

The intent of this license is simple:
  → Learn from this freely. Build on the ideas. But do not plagiarize.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
THE AUTHOR IS NOT LIABLE FOR ANY CLAIM OR DAMAGES ARISING FROM USE.
```

---

## 🙏 Acknowledgements

- [OpenAI CLIP](https://openai.com/research/clip) — The vision-language model powering image and text encoding
- [Qdrant](https://qdrant.tech/) — The vector database making sub-20ms similarity search possible
- [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist) — The open-source clothing image dataset by Zalando Research
- [Hugging Face Transformers](https://huggingface.co/openai/clip-vit-base-patch32) — CLIP model hosting and Python interface

---

<div align="center">

**Built with 🧠 + ⚡ + 🐳**

*If this project helped you understand vector search or AI-powered retrieval,*
*a ⭐ on the repository is always appreciated.*

</div>

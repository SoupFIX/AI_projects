<div align="center">

<!-- ANIMATED HEADER BANNER — deep purple/cyber gradient with matrix code rain feel -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d0221,30:1a0533,60:0a1628,100:00ffe1&height=220&section=header&fontSize=1&animation=fadeIn" width="100%"/>

<!-- ANIMATED TITLE — Orbitron gaming font, neon cyan, typewriter loop -->
<a href="https://github.com/SoupFIX/AI_projects">
  <img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=38&duration=2500&pause=1200&color=00FFE1&background=00000000&center=true&vCenter=true&width=900&height=90&lines=Visual+Product+Search+Engine;CLIP+%2B+Qdrant+%2B+FastAPI+%2B+Docker;Neural+Vision+%7C+Real-Time+Search;Upload+Image+%E2%86%92+Find+Similar+Products" alt="Animated Title" />
</a>

<!-- CODE RAIN ANIMATION — scrolling terminal-style code blocks -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0d0221,100:0a1628&height=120&section=header&text=import%20clip%20%7C%20qdrant_client%20%7C%20fastapi%20%7C%20torch%20%7C%20streamlit%0Avector%20%3D%20model.encode(image)%20%23%20512-dim%20embedding%0Aresults%20%3D%20db.search(vector%2C%20top_k%3D10)%20%23%20%3C20ms&fontSize=13&fontColor=00ffe1&fontAlignY=35&animation=blinking&desc=⚡%20Encoding%20image...%20✅%20Vectors%20stored...%20🔍%20Searching%20512-dim%20space...%20🎯%20Results%20found%20in%2018ms&descAlignY=78&descSize=12&descColor=7be0ff" width="100%"/>

<br/><br/>

<!-- BADGES WITH LINKS -->
<a href="https://www.python.org/downloads/release/python-3110/" target="_blank">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
</a>
<a href="https://fastapi.tiangolo.com/" target="_blank">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
</a>
<a href="https://streamlit.io/" target="_blank">
  <img src="https://img.shields.io/badge/Streamlit-1.37+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
</a>
<a href="https://www.docker.com/" target="_blank">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
</a>
<a href="https://qdrant.tech/" target="_blank">
  <img src="https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=for-the-badge&logo=qdrant&logoColor=white"/>
</a>
<a href="https://openai.com/research/clip" target="_blank">
  <img src="https://img.shields.io/badge/OpenAI-CLIP_ViT%2FB32-412991?style=for-the-badge&logo=openai&logoColor=white"/>
</a>

<br/><br/>

<img src="https://img.shields.io/badge/License-Reference%20Only-red?style=flat-square"/>
<img src="https://img.shields.io/badge/Status-Production_Ready-00ffe1?style=flat-square"/>
<img src="https://img.shields.io/docker/pulls/soup28/visual_product_search_engine_project?style=flat-square&color=7be0ff"/>

<br/>

<!-- BOTTOM WAVE of header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ffe1,50:0a1628,100:0d0221&height=80&section=footer&animation=fadeIn" width="100%"/>

</div>

---

## 🌌 What is This Project?

> **Imagine Google Lens — but for your own product catalog.**

This is a **Visual Product Search Engine** that lets users upload any clothing image and instantly find the 10 most visually similar products from a database — **without using any keywords or text**.

It works by converting every image into a list of **512 numbers** (called a vector) that captures its visual meaning — color, shape, style, texture. When you upload a query image, the engine finds the database images whose numbers are closest to yours.

```
You upload a photo of a red sneaker
        ↓
CLIP model reads it → [0.21, -0.84, 0.67, ... 512 numbers total]
        ↓
Qdrant scans all 500 stored vectors
        ↓
Returns the 10 most similar ones in < 20ms
        ↓
You see 10 visually similar products 🎯
```

---

## 🗺️ Project Architecture — The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK                           │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  qdrant_db   │◄───│ visual_search│◄───│ streamlit_ui │  │
│  │              │    │   (FastAPI)  │    │  (Frontend)  │  │
│  │ Vector store │    │   Port 8000  │    │  Port 8501   │  │
│  │ Port 6333    │    └──────────────┘    └──────────────┘  │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
    localhost:6333       localhost:8000       localhost:8501
         │                    │                    │
         └────────────────────┴────────────────────┘
                         Your Browser
```

**Containers talk to each other using service names** (`qdrant`, `app`) not `localhost`. Your browser uses `localhost` with port numbers.

---

## 🧠 How It Works — Phase by Phase

### Phase 1 — One-Time Setup (Building the Database)

```
500 Fashion-MNIST Images
          │
          ▼
  ┌───────────────┐
  │  CLIP Model   │  ← openai/clip-vit-base-patch32
  │ clip_encoder  │    Downloads from Hugging Face
  └───────┬───────┘
          │ Converts each image to
          │ 512 floating point numbers
          ▼
  ┌───────────────┐
  │    Qdrant     │  ← Vector Database
  │  vector_store │    Stores vectors + image paths
  └───────────────┘

Result stored in Qdrant:
  ID: 0001  │  Vector: [0.21, -0.84, 0.67 ... 509 more]  │  Path: 0001_sneaker.png
  ID: 0002  │  Vector: [0.67,  0.03, 0.19 ... 509 more]  │  Path: 0002_bag.png
  ID: 0003  │  Vector: [0.19, -0.81, 0.44 ... 509 more]  │  Path: 0003_sneaker.png
  ... 497 more rows
```

### Phase 2 — Live Search (Every Time a User Searches)

```
User uploads image (e.g. a bag photo)
          │
          ▼
  ┌───────────────┐
  │    FastAPI    │  ← app.py receives the upload
  │    app.py     │
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │  CLIP Model   │  ← Same model, same 512-number space
  │               │    Converts query image → vector
  └───────┬───────┘
          │  query_vector = [0.44, -0.12, 0.88 ...]
          ▼
  ┌───────────────┐
  │    Qdrant     │  ← "Find me the 10 closest vectors
  │  ANN Search   │     using cosine similarity"
  └───────┬───────┘
          │
          ▼
  Top 10 results with similarity scores
  → Streamlit displays them as images
```

---

## 🔬 Core Concepts Explained Simply

### 🔢 What is a Vector?

A vector is just **a list of 512 numbers** that represents an image's visual meaning.

```
Image of a red sneaker → [0.21, -0.84, 0.67, 0.44, 0.98, ... 507 more numbers]
Image of a blue jacket → [0.11,  0.92, 0.12, 0.77, 0.03, ... 507 more numbers]
```

Two images that look similar will have **similar numbers**. That's the entire magic.

### 📐 What is Cosine Similarity?

It measures the **angle between two vectors**. The smaller the angle, the more similar the images.

```
Score = 1.00  →  Identical images (angle = 0°)
Score = 0.95  →  Very similar     (angle ≈ 18°)
Score = 0.50  →  Somewhat related (angle ≈ 60°)
Score = 0.00  →  Completely different
```

### 🧩 What is CLIP?

CLIP (Contrastive Language-Image Pretraining) is an AI model from OpenAI that understands **both images and text in the same mathematical space**.

```
"red running shoes"  ──► [0.21, -0.84, 0.67 ...]  ◄── Photo of red running shoes
                                    ↑
                          Nearly identical vectors!
```

This is why text search also works — type "blue jacket" and CLIP converts that text to a vector, then Qdrant finds images with similar vectors.

### 🗄️ What is Qdrant?

Qdrant is a **vector database** — like a normal database (PostgreSQL, MySQL) but instead of searching by exact match, it searches by **mathematical similarity**.

```
Normal DB query:  SELECT * WHERE name = 'sneaker'   ← exact match only
Qdrant query:     Find vectors closest to [0.21, -0.84, ...]  ← similarity match
```

It uses **HNSW** (Hierarchical Navigable Small World) graphs to find the nearest vectors in milliseconds even with millions of entries.

---

## 📁 Project Structure

```
Visual_Product_Search_Engine_Project/
│
├── 🐳 docker-compose.yml          ← Orchestrates all 3 containers
├── 🐳 dockerfile                  ← Builds FastAPI container
├── 🐳 Dockerfile.streamlit        ← Builds Streamlit container
├── 📋 requirements.txt            ← Python dependencies
│
├── backend/                       ← FastAPI application
│   ├── app.py                     ← Main API server (search endpoints)
│   ├── clip_encoder.py            ← Loads CLIP model, encodes images
│   ├── embedder.py                ← CLIPEmbedder class (reusable)
│   ├── vector_store.py            ← Qdrant client, collection setup
│   └── config.py                  ← Settings (model name, vector size, etc.)
│
├── frontend/                      ← Streamlit UI
│   └── front_end.py               ← Beautiful space-themed search interface
│
├── data/
│   ├── images/                    ← 500 Fashion-MNIST product images
│   └── qdrant_data/               ← Qdrant vector database files
│       └── collections/
│           └── Products/          ← Your 500 stored vectors live here
│
└── scripts/                       ← Helper scripts
    └── prepare_data.py            ← One-time: encodes images → stores in Qdrant
```

---

## 🚀 Quick Start — Run in 3 Steps

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- 10GB free disk space (CLIP model is large)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/SoupFIX/AI_projects.git
```

### Step 2 — Navigate to the Project Folder
```bash
cd AI_projects/Visual_Product_Search_Engine_project
```

### Step 3 — Start All Services
```bash
docker-compose up
```

> ⏳ **Wait 5–6 minutes** on the first run. Docker will pull all images and the CLIP model (~600MB) needs time to load. Subsequent starts are much faster (~30 seconds).

---

### ✅ Access the App

Once all containers are running, open your browser and visit:

| Service | URL | What it is |
|---------|-----|-----------|
| 🎨 Streamlit UI | http://localhost:8501 | Main search interface — upload images here |
| ⚡ FastAPI Backend | http://localhost:8000 | REST API & auto-generated docs |
| 🗄️ Qdrant Dashboard | http://localhost:6333/dashboard | Vector database explorer |

---

### 🛑 Stopping the App

To stop all running services, press **`Ctrl+C`** (2–3 times) in the terminal where `docker-compose up` is running.

Or run this from the project folder in a separate terminal:
```bash
docker-compose down
```

> 💡 Always use `docker-compose down` for a clean stop — it properly releases ports so you don't run into "port already allocated" errors next time.

---

## 🔌 API Endpoints

### `POST /search` — Search by Image
Upload any image file and get back the 10 most visually similar products.

```bash
curl -X POST "http://localhost:8000/search" \
     -F "file=@your_image.png"
```

Response:
```json
{
  "query_file": "your_image.png",
  "total_results": 10,
  "results": [
    {
      "rank": 1,
      "score": 0.9823,
      "image_path": "/images/0044_sneaker.png",
      "id": 44
    }
  ]
}
```

### `POST /search-by-text` — Search by Text
Type a description and find matching product images.

```bash
curl -X POST "http://localhost:8000/search-by-text?query=red%20running%20shoes"
```

### `GET /` — Health Check
```bash
curl http://localhost:8000/
# → {"message": "✅ Visual Search Engine is running!"}
```

---

## 🐳 Docker Images

Both images are publicly available on **[Docker Hub →](https://hub.docker.com/repository/docker/soup28/visual-product-search-engine/general)**

| Image | Tag | Size | Purpose |
|-------|-----|------|---------|
| `soup28/visual-product-search-engine` | `api-1.0.0` | 8.93GB | FastAPI + CLIP + PyTorch |
| `soup28/visual-product-search-engine` | `ui-1.0.0` | 1.02GB | Streamlit frontend |

> The API image is large because it includes PyTorch and the CLIP neural network weights.

---

## 🛠️ Tech Stack

| Technology | Role | Why This Choice |
|-----------|------|----------------|
| **OpenAI CLIP** | Image/Text → Vector encoder | Understands both images and text in same space |
| **Qdrant** | Vector database | Fast ANN search, great Python client, local storage |
| **FastAPI** | REST API server | Async, auto-docs, fast |
| **Streamlit** | Frontend UI | Rapid development, Python-native |
| **PyTorch** | ML framework | Required by CLIP/Transformers |
| **Docker** | Containerization | Reproducible, portable deployment |
| **Fashion-MNIST** | Dataset | 70K clothing images, perfect for demo |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Vector dimensions | 512 |
| Index type | HNSW (Approximate Nearest Neighbour) |
| Distance metric | Cosine Similarity |
| Query time | < 20ms |
| Dataset size | 500 images (expandable to millions) |
| Modalities | Image + Text search |

---

## 🔧 Configuration

All settings are in `backend/config.py`:

```python
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"  # Model from Hugging Face
vector_size = 512                                   # Output dimensions
TOP_K_RESULTS = 10                                  # Results per search
Collection_name = "Products"                        # Qdrant collection name
```

---

## 🤔 FAQ

**Q: Why is the API image 8.93GB?**
> PyTorch alone is ~2GB and the CLIP model weights add another ~600MB. The rest is Python, CUDA libraries, and dependencies.

**Q: Can I add my own images?**
> Yes! Add images to `data/images/`, run `prepare_data.py` to encode and store them, then restart the app.

**Q: Why do containers use service names instead of localhost?**
> Each Docker container is its own isolated machine. `localhost` inside a container means "this container itself". Service names (`app`, `qdrant`) are like hostnames on Docker's internal network.

**Q: What is HNSW?**
> Hierarchical Navigable Small World — a graph algorithm that finds approximate nearest neighbours in O(log n) time instead of scanning every vector linearly. This is what makes Qdrant fast at scale.

**Q: I get a "port already allocated" error when starting.**
> A previous container is still holding the port. Run `docker-compose down` first, then `docker-compose up` again.

---

## 📄 License

**All Rights Reserved.**

Feel free to clone this project, run it locally, and explore how everything works together — that's exactly what it's here for! 🙌
Use it as a real-world reference to learn how CLIP, Qdrant, FastAPI, and Docker come together in a production-style project.

However, please **do not** copy it wholesale and publish or submit it as your own work. Give credit where it's due, and build your own awesome things inspired by it. ✨

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d0221,40:1a0533,100:00ffe1&height=140&section=footer&animation=fadeIn" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=700&size=14&duration=3000&pause=1000&color=00FFE1&center=true&vCenter=true&width=600&height=35&lines=Built+with+🧠+neural+embeddings+%26+❤️+by+soup28;If+this+helped+you%2C+please+⭐+star+the+repo!" alt="Footer" />

</div>

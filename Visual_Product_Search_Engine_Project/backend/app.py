import io
import numpy as np
from pathlib import Path
from fastapi import FastAPI,File,UploadFile,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import sys
import os
sys.path.append(str(Path(__file__).parent))
from clip_encoder import model,preprocessor
from vector_store import get_client,Collection_name
from config import TOP_K_RESULTS
import torch
from fastapi.staticfiles import StaticFiles

# CREATING THE SERVER. Server object is app
server = FastAPI(title = "Visual Product Search Engine",description = "Upload an image and get visually similar products back",version = '1.0.0')
server.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"], # ALLOW GET,POST,PUT,DELETE
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.getenv("IMAGES_DIR", os.path.join(BASE_DIR, "..", "data", "images"))
server.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Connection to Database
client = get_client()

#Image -> vector 
def encode_image_to_vector(image : Image.Image) -> list:
    inputs = preprocessor(images = image,return_tensors = "pt")
    with torch.no_grad():
        # Main Generation of 512 Numbers from the Image
        output = model.get_image_features(**inputs)
        # Tensor of shape (1,512) and normalize it
    if hasattr(output,'pooler_output'):
        image_features = output.pooler_output
    elif hasattr(output,'image_embeds'):
        image_features = output.image_embeds
    else:
        image_features = output        
    image_features = image_features/image_features.norm(dim=-1,keepdim = True)
    # convert it to a plain python list of numbers of shape(512) Ready for Qdrant
    return image_features.squeeze().tolist()

def encode_text_to_vector(text: str) -> list:
    """
    Takes a text string like "red running shoes".
    Uses YOUR preprocessor and model from clip_encoder.py
    Returns a plain Python list of 512 floats (the vector).
    """
    # Tokenize the text (convert words → numbers the model understands)
    inputs = preprocessor(text=[text], return_tensors="pt", padding=True)

    with torch.no_grad():
        output = model.get_text_features(**inputs)
    if hasattr(output,'pooler_output'):
        text_features = output.pooler_output
    elif hasattr(output,'text_embeds'):
        text_features = output.text_embeds
    else:
        text_features = output        
    # Normalize
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return text_features.squeeze().tolist()

# -------------------------------------------------------
# ENDPOINT 1: Health Check
# -------------------------------------------------------
@server.get("/")
def root():
    """Visit http://localhost:8000/ to confirm the server is running"""
    return {"message": "✅ Visual Search Engine is running! Visit /docs to test it."}

@server.on_event("startup")
async def startup():
    collections = [c.name for c in client.get_collections().collections]
    
    if "Products" not in collections:
        print("⚙️ First run! Building database... (~10 mins)")
        import sys
        sys.path.append("/app/scripts")          # 👈 path inside Docker container
        from prepare_data import run_pipeline
        run_pipeline()
        print("✅ Database ready!")
# -------------------------------------------------------
# ENDPOINT 2: Search by Image (MAIN FEATURE)
# -------------------------------------------------------
@server.post("/search")
async def search_by_image(file: UploadFile = File(...)):
    """
    Upload an image → get back the most visually similar images from your database.

    How it works:
    1. Receive uploaded image from user
    2. Convert it to a 512-number vector using CLIP
    3. Ask Qdrant: "find me vectors most similar to this one"
    4. Return the matching image paths + similarity scores
    """

    # --- Validate: must be an image file ---
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Expected an image file, got: {file.content_type}"
        )
    # --- Read the raw bytes and open as PIL Image ---
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # --- Convert image → vector using CLIP ---
    query_vector = encode_image_to_vector(image)

    # --- Search Qdrant for similar vectors ---
    # This calls client.search() internally in your vector_store.py style
    result_response = client.query_points(
        collection_name=Collection_name,   # "Products" — from your vector_store.py
        query=query_vector,
        limit=TOP_K_RESULTS                # how many results to return
    )
    hits = result_response.points
    results = []
    for hit in hits:
        raw_path = hit.payload.get('image_path', '')
        filename = Path(raw_path).name   # safely extracts just "0000_dress.png" regardless of OS
        results.append(
            {
                "rank": len(results) + 1,
                "score": round(hit.score, 4),
                "image_path": f"/images/{filename}",
                "id": hit.id,
            }
        )
    return {
        "query_file": file.filename,
        "total_results": len(results),
        "results": results
    }
# -------------------------------------------------------
# ENDPOINT 3: Search by Text (BONUS FEATURE)
# -------------------------------------------------------
@server.post("/search-by-text")
async def search_by_text(query: str = Query(..., description="e.g. red running shoes")):
    """
    Type a description → get back visually matching images.
    Works because CLIP understands BOTH images and text in the same vector space.

    Example: "blue denim jacket" → finds images of blue denim jackets
    """

    # Convert text → vector using CLIP
    query_vector = encode_text_to_vector(query)

    # Search Qdrant
    result_response = client.query_points(
        collection_name=Collection_name,
        query=query_vector,
        limit=TOP_K_RESULTS
    )
    hits = result_response.points

    # Format results
    results = []
    # safely extracts just "0000_dress.png" regardless of OS

    for hit in hits:
        raw_path = hit.payload.get('image_path', '')
        filename = Path(raw_path).name
        results.append({
            "rank": len(results) + 1,
            "score": round(hit.score, 4),
            "image_path": f"/images/{filename}",
            "id": hit.id
        })

    return {
        "query_text": query,
        "total_results": len(results),
        "results": results
    }
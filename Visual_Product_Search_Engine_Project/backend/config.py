from pathlib import Path
db_path = str(Path(__file__).parent.parent/"data"/"qdrant_db")
Collection_name = "Products"
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
#  ViT-Base/32 always outputs 512 numbers — matches vector_size in vector_store.py
vector_size = 512
# How many similar images to return per search
TOP_K_RESULTS = 10
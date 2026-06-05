"""
prepare_data.py
───────────────
One-time pipeline:
1. Download 500 Fashion-MNIST images from HuggingFace
2. Save them to disk (path controlled by IMAGES_DIR env var)
3. Encode each image with CLIP → 512-dim vector
4. Store vectors + filenames in Qdrant
"""

import sys
from pathlib import Path
from datasets import load_dataset
from PIL import Image

sys.path.append(str(Path(__file__).parent.parent / "backend"))
from vector_store import get_client,create_collection,store_vectors
from clip_encoder import encode_image

_default_image_dir = Path(__file__).parent.parent / "data" / "images"
IMAGE_DIR = Path(os.getenv("IMAGES_DIR", str(_default_image_dir)))

num_image = 500
Seed = 42
Label_name = [
    "tshirt",
    "trouser",
    "pullover",
    "dress",
    "coat",
    "sandal",
    "shirt",
    "sneaker",
    "bag",
    "ankle_boot",
    ]

def run_pipeline():
        image_dir.mkdir(parents = True,exist_ok = True)
        print("  Downloading Fashion MNIST from HuggingFace...")
        dataset = load_dataset("zalando-datasets/fashion_mnist",split = "train")
        dataset = dataset.shuffle(seed = Seed).select(range(num_image))

        saved_paths = []   # keep track of saved image paths
        for i,item in enumerate(dataset):
            label_name = Label_name[item["label"]]
            filename = f"{i:04d}_{label_name}.png"
            filepath = image_dir/filename
            img : Image.Image = item['image']
            img = img.resize((224,224),Image.LANCZOS)
            img.convert("RGB").save(filepath)
            saved_paths.append(filepath) 
        # Step 2: Connect to Qdrant and create Collection
        
        print("Connecting to Qdrant...")
        client = get_client()
        create_collection(client)
        
        # Step 3 : Convert each image to vector and store
        print("Indexing images into Qdrant")
        vectors = []
        image_paths = []

        for i,filepath in enumerate(saved_paths):
            img = Image.open(filepath).convert("RGB")
            v = encode_image(img)
            vectors.append(v)
            image_paths.append(filepath.name)

            if(i+1)%50 ==0:
                print(f"Processed {i+1}/{len(saved_paths)}")
        store_vectors(client,vectors,image_paths)
        print(f"✅ All Done ! {len(vectors)} images indexed and ready to search!")
if __name__ == "__main__":
            run_pipeline()

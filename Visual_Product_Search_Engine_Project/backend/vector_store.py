from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance,VectorParams,PointStruct
DB_path = str(Path(__file__).parent.parent/"data"/"qdrant_data")
Collection_name = "Products"
vector_size = 512
import os

def get_client():
    host = os.getenv("QDRANT_HOST", "localhost")  # reads env variable
    port = int(os.getenv("QDRANT_PORT", 6333))
    return QdrantClient(host=host, port=port)

def create_collection(client : QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if Collection_name not in existing :
        client.create_collection(
        collection_name = Collection_name,
        vectors_config = VectorParams(
            size = vector_size,
            distance = Distance.COSINE
        )
        )
        print(f"Collection : {Collection_name} Created ✅")
    else:
        print(f"Collection : {Collection_name} Already exist ✅")

def store_vectors(client : QdrantClient,vectors : list,image_paths : list) -> None:
    """
    Store image vectors into Qdrant.
    Each vector is stored with its image path as metadata.
    """
    points = [
        PointStruct(
        id = i,
        vector = vector,
        payload = {"image_path": Path(image_paths[i]).name}
        )
        for i,vector in enumerate(vectors)
    ]
    client.upsert(
        collection_name = Collection_name,
        points = points
    )
    print(f"Stored {len(points)} vectors into Qdrant ✅")

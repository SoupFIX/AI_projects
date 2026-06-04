from __future__ import annotations
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from transformers import CLIPModel,CLIPProcessor

Model_id = "openai/clip-vit-base-patch32"


class CLIPembedder:
    """
    Loads CLIP ones and expose embed_images and embed_text methods.
    """
    def __init__(self) ->None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP on : {self.device}")
        self.processor = CLIPProcessor.from_pretrained(Model_id)
        self.model = CLIPModel.from_pretrained(Model_id).to(self.device)
        self.model.eval()
        print(" CLIP Model Ready.")

    def embed_image(self,image_path : str | Path) ->np.ndarray:
        """
        Encode one image file into 512 -Dimensional Vector
        Args : image_path : Path to any PNG or JPEG file.
        Returns : numpy array of shape(512,),normalized to unit length
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images = image,return_tensors = "pt")
        inputs = {
            k:v.to(self.device) for k,v in inputs.items()
        }
        with torch.no_grad():
            raw = self.model.get_image_features(**inputs)
        if hasattr(raw,"pooler_output"):
            features = raw.pooler_output
        elif hasattr(raw,"image_embeds"):
            features = raw.image_embeds
        else:
            features = raw
        


        features = features/features.norm(dim=-1,keepdim = True)
        return features.squeeze().cpu().numpy()

    def embed_text(self,query : str) -> np.ndarray:
        """
        Encode a text strings to a 512-dimensional Vector
        Args : 
            query : Any plain-English Description,e.g = "red sneaker with white sole"
        Returns :
            numpy array of shape (512,), normalize to unit length
            Lives in the same space as image vectors, so we can compare them directly.    
        """

        inputs = self.processor(text = [query],return_tensors = "pt",padding = True)
        inputs = {
            k:v.to(self.device )for k,v in inputs.items()
        }
        with torch.no_grad():
            raw = self.model.get_text_features(**inputs)
        if hasattr(raw,"pooler_output"):
            features = raw.pooler_output
        elif hasattr(raw,"text_embeds"):
            features = raw.text_embeds
        else:
            features = raw

        features = features/features.norm(dim=-1,keepdim = True)
        return features.squeeze().cpu().numpy()
            
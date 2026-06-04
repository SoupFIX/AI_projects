# Importing the required necessary libraries
from transformers import CLIPProcessor,CLIPModel
from PIL import Image
import torch
# Address of Hugging Face
MODEL_NAME = "openai/clip-vit-base-patch32"
# Downloads and loads the actual clip Neural Network
model = CLIPModel.from_pretrained(MODEL_NAME)
# Downloads the image preparation tool 
preprocessor = CLIPProcessor.from_pretrained(MODEL_NAME)
# Makes model ready from learning to predicting only
model.eval()

def encode_image(image : Image.Image) ->list:
    # Prepares the image into a format PyTorch ("pt") can feed into the model
    inputs = preprocessor(images = image,return_tensors = "pt")
    # Just predict don't learn
    with torch.no_grad():
        output = model.get_image_features(**inputs)  # returns complex object
    if hasattr(output,'pooler_output'):
        features  = output.pooler_output
    elif hasattr(output,'image_embeds'):
        features = output.image_embeds
    else:
        features = output 
    # NOrmalize each vectors  
    features = features/features.norm(dim=-1,keepdim=True)
    # return the simple list of numbers for each image
    return features.squeeze().tolist()
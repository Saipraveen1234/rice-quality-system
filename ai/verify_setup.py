from ultralytics import YOLO
import sys
import torch

def check_setup():
    print(f"Python version: {sys.version}")
    
    try:
        model = YOLO('yolov8n.pt')  # load a pretrained model
        print("YOLOv8 installed and model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLO: {e}")
        return

    if torch.backends.mps.is_available():
        print("MPS (Metal Performance Shaders) is available for Mac GPU acceleration.")
    elif torch.cuda.is_available():
        print("CUDA is available.")
    else:
        print("Running on CPU.")

if __name__ == "__main__":
    check_setup()

from ultralytics import YOLO

def train():
    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (nano for speed)

    # Train the model
    results = model.train(data="config/data.yaml", epochs=10, imgsz=640, device="mps")

if __name__ == "__main__":
    train()

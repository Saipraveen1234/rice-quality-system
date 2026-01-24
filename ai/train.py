from ultralytics import YOLO
import os

def train():
    # Use absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_yaml = os.path.join(base_dir, 'config', 'data.yaml')
    
    # Load a pretrained model (recommended for training)
    model = YOLO('yolov8n.pt') 

    # Train the model
    # epochs=100: long enough to converge
    # imgsz=640: standard resolution
    # patience=50: wait 50 epochs before early stopping if no improvement
    # batch=16: standard batch size
    # augment=True: use default augmentation to help with small dataset
    results = model.train(
        data=data_yaml,
        epochs=100,
        imgsz=640,
        batch=16,
        patience=50,
        name='rice_quality_improved',
        project=os.path.join(os.path.dirname(base_dir), 'runs/detect'),
        exist_ok=True,
        pretrained=True,
        optimizer='Adam',   # Adam usually works better for smaller datasets
        lr0=1e-3,           # Initial learning rate
        plots=True          # Save training plots
    )

if __name__ == '__main__':
    train()

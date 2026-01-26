from ultralytics import YOLO
import os

def train():
    """
    Enhanced training script for rice cluster detection.
    Uses YOLOv8-Small with high-resolution input and advanced augmentation.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_yaml = os.path.join(base_dir, 'config', 'data_dense.yaml')
    
    print("=" * 60)
    print("RICE CLUSTER DETECTION TRAINING - PHASE 4A")
    print("=" * 60)
    print(f"Data config: {data_yaml}")
    print(f"Model: YOLOv8-Small (upgraded from Nano)")
    print(f"Resolution: 1280x1280 (2x higher for cluster detection)")
    print(f"Expected duration: 3-4 hours")
    print("=" * 60)
    
    # Use SMALL model instead of NANO for better accuracy
    model = YOLO('yolov8s.pt')  # Upgraded from yolov8n.pt

    results = model.train(
        data=data_yaml,
        epochs=150,           # Increased from 100
        imgsz=1280,          # Higher resolution for clusters (was 640)
        batch=4,             # Smaller batch for higher res (was 16)
        patience=75,         # Early stopping patience
        name='rice_cluster_v2',
        project=os.path.join(base_dir, 'runs/detect'),
        exist_ok=True,
        pretrained=True,
        optimizer='AdamW',   # Better optimizer than Adam
        lr0=1e-3,
        
        # Advanced augmentation for cluster detection
        mosaic=1.0,          # Mix 4 images together (simulates dense piles)
        mixup=0.15,          # Blend images (simulates overlapping grains)
        copy_paste=0.1,      # Copy grains between images
        degrees=180,         # Full rotation augmentation
        scale=0.5,           # Scale variation (0.5-1.5x)
        flipud=0.5,          # Vertical flip
        fliplr=0.5,          # Horizontal flip
        
        # Output
        plots=True,          # Generate training plots
        save=True,
        save_period=10       # Save checkpoint every 10 epochs
    )
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Best model saved to: {base_dir}/runs/detect/rice_cluster_v2/weights/best.pt")
    print(f"Results: {base_dir}/runs/detect/rice_cluster_v2/")
    print("=" * 60)

if __name__ == '__main__':
    train()

from ultralytics import YOLO
import os

def fix_data_yaml(base_dir):
    """Rewrite data.yaml with the correct absolute path for the current machine."""
    dataset_dir = os.path.join(base_dir, 'datasets', 'merged_dataset')
    data_yaml = os.path.join(dataset_dir, 'data.yaml')
    content = f"""path: {dataset_dir}
train: train/images
val: valid/images

nc: 2
names:
  0: Full
  1: Broken
"""
    with open(data_yaml, 'w') as f:
        f.write(content)
    return data_yaml

def train():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_yaml = fix_data_yaml(base_dir)

    print("=" * 60)
    print("RICE QUALITY TRAINING - V3 (Merged Dataset)")
    print("=" * 60)
    print(f"Data config: {data_yaml}")
    print(f"Model: YOLOv8-Small")
    print(f"Dataset: 904 images (723 train / 181 val)")
    print(f"Classes: Full, Broken")
    print(f"Expected duration: 4-6 hours on CPU")
    print("=" * 60)

    model = YOLO('yolov8s.pt')

    results = model.train(
        data=data_yaml,
        epochs=100,
        imgsz=640,           # 640 is optimal — dataset images are smaller resolution
        batch=8,
        patience=30,         # Stop early if no improvement for 30 epochs
        name='rice_quality_v3',
        project=os.path.join(base_dir, 'runs/detect'),
        exist_ok=False,
        pretrained=True,
        optimizer='AdamW',
        lr0=1e-3,
        lrf=0.01,            # Final LR = lr0 * lrf

        # Augmentation
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
        degrees=180,
        scale=0.5,
        flipud=0.5,
        fliplr=0.5,

        plots=True,
        save=True,
        save_period=10,
        val=True,
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    best = os.path.join(base_dir, 'runs/detect/rice_quality_v3/weights/best.pt')
    print(f"Best model: {best}")
    print("Update inference.py MODEL_PATH to use this model.")
    print("=" * 60)

if __name__ == '__main__':
    train()

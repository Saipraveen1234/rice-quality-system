from ultralytics import YOLO
import os

def resume_train():
    """
    Resume training from Epoch 13 to Epoch 50.
    Uses the last checkpoint to continue where we left off.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    last_checkpoint = os.path.join(base_dir, 'runs/detect/rice_cluster_v2/weights/last.pt')
    
    print("=" * 60)
    print("RESUMING RICE CLUSTER TRAINING - EPOCH 13 → 50")
    print("=" * 60)
    print(f"Checkpoint: {last_checkpoint}")
    print(f"Target: 50 epochs total")
    print(f"Remaining: ~37 epochs (~8 hours)")
    print("=" * 60)
    
    # Load the last checkpoint
    model = YOLO(last_checkpoint)
    
    # Resume training - YOLO will continue from where it stopped
    results = model.train(
        resume=True,      # Resume from checkpoint
        epochs=50,        # Target total epochs (will train 13→50)
    )
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Best model: {base_dir}/runs/detect/rice_cluster_v2/weights/best.pt")
    print(f"Final epoch: 50")
    print("=" * 60)

if __name__ == '__main__':
    resume_train()

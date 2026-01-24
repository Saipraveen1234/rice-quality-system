import sys
import json
import os
import contextlib
from ultralytics import YOLO

# Path to the trained model
# Support both local development and Docker environments
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from ai/ to project root
MODEL_PATH = os.path.join(project_root, 'runs/detect/rice_quality_improved/weights/best.pt')

def analyze_image(image_path):
    try:
        # Load the model
        # Redirect stdout/stderr to suppress "Results saved to..." messages
        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            model = YOLO(MODEL_PATH)
            
            # Run inference
            # Using standard confidence threshold (0.25) now that model is better trained
            results = model.predict(image_path, conf=0.25, save=True, project='/Users/malleshasaipraveen/Desktop/rice-quality-system/runs/detect', name='inference', exist_ok=True, verbose=False)
        
        result = results[0]
        
        # Count classes
        # Class 0: Full, Class 1: Broken
        boxes = result.boxes
        classes = boxes.cls.tolist()
        
        full_grains = classes.count(0.0)
        broken_grains = classes.count(1.0)
        total_grains = full_grains + broken_grains
        
        # Calculate quality (percentage of full grains)
        if total_grains > 0:
            quality_score = round((full_grains / total_grains) * 100, 2)
        else:
            quality_score = 0.0
            
        # Get path to saved annotated image (optional, for debugging)
        # It usually saves to runs/detect/inference/<filename>
        
        output = {
            "status": "success",
            "image": image_path,
            "total_grains": total_grains,
            "good_grains": full_grains,
            "broken_grains": broken_grains,
            "quality_score": quality_score,
            "details": "Real YOLOv8 Inference"
        }
        
    except Exception as e:
        output = {
            "status": "error",
            "error": str(e)
        }
    
    # Print JSON to stdout
    print(json.dumps(output))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)
        
    image_path = sys.argv[1]
    analyze_image(image_path)

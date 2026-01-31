import sys
import json
import os
import contextlib
import cv2
import numpy as np
from ultralytics import YOLO

# Path to the trained model
# Support both local development and Docker environments
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from ai/ to project root
MODEL_PATH = os.path.join(script_dir, 'runs/detect/rice_cluster_v2/weights/best.pt')

def preprocess_image(image_path):
    """
    Preprocess image to handle transparent backgrounds.
    Converts them to black to match training data.
    """
    try:
        # Read image with alpha channel support
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            return image_path
        
        # Handle different image formats
        if len(img.shape) == 2:
            # Grayscale image, convert to BGR
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            # Image has alpha channel (transparency)
            # Simple approach: replace transparent areas with black
            rgb = img[:, :, :3]
            alpha = img[:, :, 3]
            
            # Create black background
            black_bg = np.zeros_like(rgb)
            
            # Blend: where alpha is 255 (opaque), use original; where 0 (transparent), use black
            alpha_3ch = np.stack([alpha, alpha, alpha], axis=2) / 255.0
            img = (rgb * alpha_3ch + black_bg * (1 - alpha_3ch)).astype(np.uint8)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            # Standard RGB/BGR image - use as is
            pass
        else:
            return image_path
        
        # Save preprocessed image
        preprocessed_path = image_path.rsplit('.', 1)[0] + '_preprocessed.jpg'
        cv2.imwrite(preprocessed_path, img)
        
        return preprocessed_path
        
    except Exception as e:
        print(f"Preprocessing error: {e}", file=sys.stderr)
        return image_path



def validate_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image file"

        # Check average brightness
        # Rice grains on black background should result in low average brightness
        # Random screenshots usually have high brightness (white/light background)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Threshold: 100 out of 255. 
        # Screenshots are typically > 150-200. Dark background images are < 50.
        if mean_brightness > 100:
            return False, "Invalid image: Image is too bright. Please use an image with a dark background."
            
        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def analyze_image(image_path):
    try:
        # Validate image first
        is_valid, validation_error = validate_image(image_path)
        if not is_valid:
            print(json.dumps({
                "status": "error",
                "error": validation_error
            }))
            return

        # Preprocess image to handle transparent/white backgrounds
        processed_image_path = preprocess_image(image_path)
        
        # Load the model
        # Redirect stdout/stderr to suppress "Results saved to..." messages
        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            model = YOLO(MODEL_PATH)
            
            # Run inference on preprocessed image
            # Using standard confidence threshold (0.25) now that model is better trained
            # Save to project_root/runs/detect inside the container
            save_dir = os.path.join(project_root, 'runs/detect')
            results = model.predict(processed_image_path, conf=0.25, save=True, project=save_dir, name='inference', exist_ok=True, verbose=False)
        
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

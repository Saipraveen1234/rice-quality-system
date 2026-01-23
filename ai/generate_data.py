import os
import random
import cv2
import numpy as np
from glob import glob
from tqdm import tqdm

# Configuration
SOURCE_DIR = "datasets/source_grains"
OUTPUT_DIR = "datasets/generated_train"
IMG_SIZE = 640
NUM_IMAGES = 200  # Generate 200 synthetic images
GRAINS_PER_IMAGE = 15

# Classes
CLASS_FULL = 0
CLASS_BROKEN = 1

def setup_dirs():
    os.makedirs(f"{OUTPUT_DIR}/images", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/labels", exist_ok=True)

def load_source_images():
    # Load all images from all subdirectories
    images = glob(f"{SOURCE_DIR}/*/*.jpg") + glob(f"{SOURCE_DIR}/*/*.png")
    print(f"Found {len(images)} source grains.")
    return images

def create_broken_grain(img):
    """
    Simulate a broken grain by cropping the original randomly.
    """
    h, w = img.shape[:2]
    # Keep 30% to 70% of the grain to simulate breakage
    crop_factor = random.uniform(0.3, 0.7)
    
    if random.choice([True, False]):
        # Horizontal crop (keep top or bottom)
        new_h = int(h * crop_factor)
        start_y = 0 if random.choice([True, False]) else h - new_h
        return img[start_y:start_y+new_h, :]
    else:
        # Vertical crop (keep left or right)
        new_w = int(w * crop_factor)
        start_x = 0 if random.choice([True, False]) else w - new_w
        return img[:, start_x:start_x+new_w]

def generate_scene(image_id, source_grains):
    # Create black canvas
    canvas = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    labels = []

    for _ in range(GRAINS_PER_IMAGE):
        # Pick a random source grain
        src_path = random.choice(source_grains)
        src_img = cv2.imread(src_path)
        
        if src_img is None:
            continue

        # Decide if Full or Broken
        is_broken = random.random() < 0.5 # 50% chance of being broken
        class_id = CLASS_BROKEN if is_broken else CLASS_FULL

        if is_broken:
            grain_img = create_broken_grain(src_img)
        else:
            grain_img = src_img

        # Random rotation
        angle = random.randint(0, 360)
        M = cv2.getRotationMatrix2D((grain_img.shape[1]//2, grain_img.shape[0]//2), angle, 1.0)
        grain_img = cv2.warpAffine(grain_img, M, (grain_img.shape[1], grain_img.shape[0]))

        # Check for transparency/black background in the rotated image? 
        # Actually simplest is just to copy it over. 
        # Using a simple mask for non-black pixels to overlay.
        
        # Random position
        h, w = grain_img.shape[:2]
        
        # Ensure it fits
        if h >= IMG_SIZE or w >= IMG_SIZE: continue

        x_pos = random.randint(0, IMG_SIZE - w - 1)
        y_pos = random.randint(0, IMG_SIZE - h - 1)

        # Region of Interest
        roi = canvas[y_pos:y_pos+h, x_pos:x_pos+w]

        # Create mask (assuming grain is on black/dark background in source or simply non-black pixels)
        # The Kaggle dataset usually has black background.
        gray = cv2.cvtColor(grain_img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Black-out area of grain in ROI
        img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        # Take only region of grain from grain_img
        img_fg = cv2.bitwise_and(grain_img, grain_img, mask=mask)

        # Put grain in ROI
        dst = cv2.add(img_bg, img_fg)
        canvas[y_pos:y_pos+h, x_pos:x_pos+w] = dst

        # Add label (YOLO format: class x_center y_center width height)
        # Normalized to 0-1
        x_center = (x_pos + w/2) / IMG_SIZE
        y_center = (y_pos + h/2) / IMG_SIZE
        norm_w = w / IMG_SIZE
        norm_h = h / IMG_SIZE
        
        labels.append(f"{class_id} {x_center} {y_center} {norm_w} {norm_h}")

    # Save Image
    params = [cv2.IMWRITE_JPEG_QUALITY, 95] # Save as JPG to save space if needed
    cv2.imwrite(f"{OUTPUT_DIR}/images/{image_id}.jpg", canvas, params)

    # Save Label
    with open(f"{OUTPUT_DIR}/labels/{image_id}.txt", "w") as f:
        f.write("\n".join(labels))

if __name__ == "__main__":
    setup_dirs()
    source_grains = load_source_images()
    if not source_grains:
        print("No source images found!")
    else:
        print("Generating synthetic data...")
        for i in tqdm(range(NUM_IMAGES)):
            generate_scene(f"train_{i}", source_grains)
        print("Done!")

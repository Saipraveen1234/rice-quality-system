import os
import random
import cv2
import numpy as np
from glob import glob
from tqdm import tqdm

# Configuration
SOURCE_DIR = "datasets/source_grains"
OUTPUT_DIR = "datasets/generated_train" # Overwrite the existing dataset folder for next training
IMG_SIZE = 640
NUM_IMAGES = 200  # Generate 200 synthetic images
GRAINS_PER_IMAGE = 50 # Increased density (was 15)

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

def add_shadow(canvas, mask, x, y, w, h):
    """
    Adds a simple drop shadow to the canvas based on the grain mask.
    """
    shadow_offset_x = random.randint(2, 5)
    shadow_offset_y = random.randint(2, 5)
    
    # Create shadow mask (dilated slightly to look softer)
    shadow_mask = mask.copy()
    shadow_mask = cv2.GaussianBlur(shadow_mask, (5, 5), 0)
    
    # Shadow intensity (0.4 opacity)
    shadow_opacity = 0.4
    
    # Calculate shadow coordinates
    sy1 = min(canvas.shape[0], max(0, y + shadow_offset_y))
    sy2 = min(canvas.shape[0], max(0, y + h + shadow_offset_y))
    sx1 = min(canvas.shape[1], max(0, x + shadow_offset_x))
    sx2 = min(canvas.shape[1], max(0, x + w + shadow_offset_x))
    
    # Calculate source mask coordinates (handling boundary clipping)
    my1 = sy1 - (y + shadow_offset_y)
    my2 = my1 + (sy2 - sy1)
    mx1 = sx1 - (x + shadow_offset_x)
    mx2 = mx1 + (sx2 - sx1)
    
    if (sy2 <= sy1) or (sx2 <= sx1): return canvas
    
    # Apply shadow
    roi_shadow = canvas[sy1:sy2, sx1:sx2]
    shadow_area = shadow_mask[my1:my2, mx1:mx2]
    
    # Darken the shadow area
    # Convert shadow_area to float 0-1
    shadow_factor = (shadow_area.astype(float) / 255.0) * shadow_opacity
    
    # Broadcast to 3 channels
    shadow_factor = np.stack([shadow_factor, shadow_factor, shadow_factor], axis=2)
    
    # Darken: result = original * (1 - shadow_factor)
    roi_shadow = roi_shadow * (1.0 - shadow_factor)
    canvas[sy1:sy2, sx1:sx2] = roi_shadow.astype(np.uint8)
    
    return canvas

def generate_scene(image_id, source_grains):
    # Create black canvas
    canvas = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    labels = []

    # Cluster centers (create 3-5 piles of rice)
    num_clusters = random.randint(3, 5)
    clusters = []
    for _ in range(num_clusters):
        cx = random.randint(100, IMG_SIZE-100)
        cy = random.randint(100, IMG_SIZE-100)
        clusters.append((cx, cy))

    for _ in range(GRAINS_PER_IMAGE):
        # Pick a random source grain
        src_path = random.choice(source_grains)
        src_img = cv2.imread(src_path)
        
        if src_img is None:
            continue

        # Decide if Full or Broken
        is_broken = random.random() < 0.5 
        class_id = CLASS_BROKEN if is_broken else CLASS_FULL

        if is_broken:
            grain_img = create_broken_grain(src_img)
        else:
            grain_img = src_img

        # Random rotation
        angle = random.randint(0, 360)
        M = cv2.getRotationMatrix2D((grain_img.shape[1]//2, grain_img.shape[0]//2), angle, 1.0)
        grain_img = cv2.warpAffine(grain_img, M, (grain_img.shape[1], grain_img.shape[0]))
        
        # Slight blur to blend edges
        grain_img = cv2.GaussianBlur(grain_img, (3, 3), 0)

        h, w = grain_img.shape[:2]
        if h >= IMG_SIZE or w >= IMG_SIZE: continue

        # Position logic: 80% chance to be near a cluster center, 20% random
        if random.random() < 0.8:
            # Pick a random cluster
            cx, cy = random.choice(clusters)
            # Offset from center (Gaussian dispersion) - make tightly packed
            offset_x = int(random.gauss(0, 40))
            offset_y = int(random.gauss(0, 40))
            x_pos = max(0, min(IMG_SIZE - w, cx + offset_x - w//2))
            y_pos = max(0, min(IMG_SIZE - h, cy + offset_y - h//2))
        else:
            # Random position (scattered grains)
            x_pos = random.randint(0, IMG_SIZE - w - 1)
            y_pos = random.randint(0, IMG_SIZE - h - 1)

        # Create mask
        gray = cv2.cvtColor(grain_img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        
        # Add shadow first
        canvas = add_shadow(canvas, mask, x_pos, y_pos, w, h)

        # Region of Interest
        roi = canvas[y_pos:y_pos+h, x_pos:x_pos+w]
        mask_inv = cv2.bitwise_not(mask)

        # Black-out area of grain in ROI
        img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        # Take only region of grain from grain_img
        img_fg = cv2.bitwise_and(grain_img, grain_img, mask=mask)

        # Put grain in ROI
        dst = cv2.add(img_bg, img_fg)
        canvas[y_pos:y_pos+h, x_pos:x_pos+w] = dst

        # Add label
        x_center = (x_pos + w/2) / IMG_SIZE
        y_center = (y_pos + h/2) / IMG_SIZE
        norm_w = w / IMG_SIZE
        norm_h = h / IMG_SIZE
        
        labels.append(f"{class_id} {x_center} {y_center} {norm_w} {norm_h}")

    # Save Image
    params = [cv2.IMWRITE_JPEG_QUALITY, 95]
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
        print("Generating DENSE CLUSTERED synthetic data WITH SHADOWS...")
        for i in tqdm(range(NUM_IMAGES)):
            generate_scene(f"train_dense_{i}", source_grains)
        print("Done!")

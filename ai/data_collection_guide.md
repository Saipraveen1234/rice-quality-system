# Rice Image Collection Guidelines

To train a high-accuracy AI model, we need good data. Please follow these rules when taking photos of the rice samples.

## 1. Setup the Scene
*   **Background**: Use a **solid, contrasting background**. A black or dark blue matte paper/cloth is best for white rice. Avoid white backgrounds if possible (harder to see edges).
*   **Lighting**: Use **even, bright lighting**. Avoid strong shadows. Natural daylight near a window is great, or overhead lights with no direct glare.
*   **Camera**: A standard smartphone camera is fine. Ensure the lens is clean.

## 2. Arrangement
*   **Spread Out**: Spread the grains so they **do not touch**. The AI needs to see individual grains to count them accurately.
    *   *Bad*: A pile of rice.
    *   *Good*: Grains separated by at least 1-2mm.
*   **Diversity**: Include different types in one image if possible (some broken, some full, some discolored).

## 3. Capture Strategy
*   **Angle**: Take photos directly from **top-down** (bird's eye view).
*   **Quantity**:
    *   Start with **20-30 photos**.
    *   Each photo should have 20-50 grains.
*   **Resolution**: Standard photo resolution is sufficient.

## 4. Folder Structure
Save your images in the `ai/datasets` folder (create it if missing):

```
ai/datasets/
  └── raw_images/
       ├── sample_01.jpg
       ├── sample_02.jpg
       ...
```

## Next Steps
Once you have ~20 photos:
1.  We will use an annotation tool (like **LabelImg**) to draw boxes around "Full", "Broken", and "Bad" grains.
2.  We will convert these to YOLO format.

import numpy as np
import onnxruntime as ort
from PIL import Image
from utils.resource_path import resource_path
import sys
import os
import logging

# Logger setup
logger = logging.getLogger("getpositions")
logger.setLevel(logging.DEBUG)

# Use the helper function to get the correct model path
model_path = resource_path("chess_detection.onnx")
if not os.path.exists(model_path):
    logger.error(
        "Missing chess_detection.onnx – please download and place it in the project root. "
        "See README for instructions: https://github.com/OTAKUWeBer/ChessPilot/blob/main/README.md"
    )
    sys.exit(1)

# Load the ONNX model from the correct path
session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

conf = 0.7

def letterbox_resize(image, target_size):
    """
    Resizes the image to fit within the target_size, maintaining the aspect ratio.
    Adds padding only to one dimension (either top/bottom or left/right) to make the image square.
    """
    orig_w, orig_h = image.size
    scale = min(target_size / orig_w, target_size / orig_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2

    padded = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    padded.paste(resized, (x_offset, y_offset))

    return padded, x_offset, y_offset, scale

def preprocess_image(image):
    """
    Prepares the image for model inference by resizing, normalizing, and formatting.
    """
    image, x_offset, y_offset, scale = letterbox_resize(image, 640)
    image = np.array(image).astype(np.float32) / 255.0  # Normalize
    image = image.transpose(2, 0, 1)  # HWC to CHW
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image, x_offset, y_offset, scale

def scale_bbox(detection, x_offset, y_offset, scale):
    """
    Scales bounding box coordinates from padded/resized image to original image dimensions.
    """
    x, y, w, h = detection[:4]
    new_x = int((x - x_offset) / scale)
    new_y = int((y - y_offset) / scale)
    new_w = int((w - x) / scale)  # Width in original dimensions
    new_h = int((h - y) / scale)  # Height in original dimensions
    
    scaled = detection.copy()
    scaled[:4] = [new_x, new_y, new_w, new_h]
    return scaled

def predict(image):
    """
    Runs model inference and returns processed detections.
    """
    img_array, x_offset, y_offset, scale = preprocess_image(image)
    output = session.run([output_name], {input_name: img_array})[0]
    output = np.squeeze(output)
    
    detections = []
    for r in output:
        if r[4] > conf:
            scaled = scale_bbox(r, x_offset, y_offset, scale)
            detections.append(scaled.tolist())  # Convert to list for compatibility
    
    return detections

def get_positions(image_input):
    """
    Handles image loading, executes prediction, and returns detections, midpoints, and offset.
    """
    try:
        if isinstance(image_input, str):
            image = Image.open(image_input)
        else:
            image = image_input
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None, None

    predictions = predict(image)
    if not predictions:
        return None, None, None

    midpoints, drag_offset = calculate_midpoints_and_offset(predictions)

    return predictions, midpoints, drag_offset

def calculate_midpoints_and_offset(detections):
    """
    Calculates the midpoints of each square and a drag offset.
    """
    if not detections:
        return {}, 0

    # Assuming the detections include piece bounding boxes, we can estimate square size
    # A simple approach is to find the min/max coordinates to define the board area
    all_x = [d[0] for d in detections]
    all_y = [d[1] for d in detections]

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    board_width = max_x - min_x
    board_height = max_y - min_y

    square_w = board_width / 8
    square_h = board_height / 8

    drag_offset = min(square_h // 4, square_w // 4)

    midpoints = {}
    for i in range(8):
        for j in range(8):
            mid_x = min_x + (j * square_w) + (square_w / 2)
            mid_y = min_y + (i * square_h) + (square_h / 2)

            # Convert to standard chess notation (a1, h8)
            file = chr(ord('a') + j)
            rank = str(8 - i)
            square_name = f"{file}{rank}"
            midpoints[square_name] = (mid_x, mid_y)

    return midpoints, drag_offset

if __name__ == "__main__":
    image_path = "screenshot.png"
    preds, mids, offset = get_positions(image_path)
    print("Predictions:", preds)
    print("Midpoints:", mids)
    print("Drag Offset:", offset)
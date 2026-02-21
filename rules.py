"""
EAS 510 - Expert System Rules
"""
import os
import cv2


from PIL import Image


def _get_image_dims(path):
    """Return (w, h) or (None, None) if PIL can't read the file."""
    try:
        with Image.open(path) as im:
            return im.size  # (width, height)
    except Exception:
        return None, None


def rule1_metadata(target_info, input_path):
    """
    Rule 1: Metadata (file size + dimensions + aspect ratio)
    Total score: 30 points

    target_info must contain:
      - 'path': path to the original image
      - 'size': file size in bytes (already stored in your register_targets)
    """
    target_path = target_info["path"]

    # ---- File size ratio ----
    try:
        input_size = os.path.getsize(input_path)
    except OSError:
        return 0, False, "Could not stat input file"

    target_size = target_info.get("size", 0)

    if target_size > 0 and input_size > 0:
        size_ratio = min(input_size, target_size) / max(input_size, target_size)  # 0..1
    else:
        size_ratio = 0.0

    # ---- Dimensions + aspect ratio ----
    iw, ih = _get_image_dims(input_path)
    tw, th = _get_image_dims(target_path)

    # If we can't read dimensions, fall back to size-only scoring
    if iw is None or tw is None or ih == 0 or th == 0:
        score = int(size_ratio * 30)
        fired = size_ratio >= 0.40
        evidence = f"Size ratio {size_ratio:.2f} (dims unavailable)"
        return score, fired, evidence

    # Width/height similarity (0..1)
    w_ratio = min(iw, tw) / max(iw, tw)
    h_ratio = min(ih, th) / max(ih, th)
    dim_sim = (w_ratio + h_ratio) / 2.0

    # Aspect ratio similarity (0..1)
    in_ar = iw / ih
    tgt_ar = tw / th
    ar_ratio = min(in_ar, tgt_ar) / max(in_ar, tgt_ar)

    # ---- Scoring breakdown (total 30) ----
    # Feel free to tune weights, but keep total 30.
    size_points = int(size_ratio * 10)     # 0..14
    dim_points = int(dim_sim * 16)         # 0..12
    ar_points = int(ar_ratio * 4)          # 0..4
    score = size_points + dim_points + ar_points

    # Clamp just in case
    score = max(0, min(30, score))

    # ---- Fire decision ----
    # Fires when metadata strongly suggests same original.
    fired = (size_ratio >= 0.45) or (dim_sim >= 0.80 and ar_ratio >= 0.90)

    evidence = (
        f"Size ratio {size_ratio:.2f}, "
        f"Dims {iw}x{ih} vs {tw}x{th} (sim {dim_sim:.2f}), "
        f"AR sim {ar_ratio:.2f}"
    )

    return score, fired, evidence



def rule2_histogram(target_info, input_path):
    """Rule 2: Compare color histograms."""
    # Load both images
    target_img = cv2.imread(target_info['path'])
    input_img = cv2.imread(input_path)

    # Check if images loaded successfully
    if target_img is None or input_img is None:
        return 0, False, "Could not load images"

    # Calculate histograms for each color channel (B, G, R)
    # Parameters: [image], [channel], mask, [bins], [range]
    target_hist = cv2.calcHist([target_img], [0, 1, 2], None,
                                [8, 8, 8], [0, 256, 0, 256, 0, 256])
    input_hist = cv2.calcHist([input_img], [0, 1, 2], None,
                               [8, 8, 8], [0, 256, 0, 256, 0, 256])

    # Normalize histograms (scale to 0-1)
    cv2.normalize(target_hist, target_hist)
    cv2.normalize(input_hist, input_hist)

    # Compare histograms using correlation method
    # Returns value between -1 (opposite) and 1 (identical)
    similarity = cv2.compareHist(target_hist, input_hist, cv2.HISTCMP_CORREL)

    # Convert to score (0-35 points)
    # similarity ranges from -1 to 1, we map 0-1 to 0-35
    score = int(max(0, similarity) * 30)
    fired = similarity > 0.5
    evidence = f"Histogram correlation {similarity:.3f}"

    return score, fired, evidence

def rule3_template(target_info, input_path):
    """
    Rule 3: Template matching (cv2.matchTemplate) to detect if one image is contained in another.
    Output matches required format:
      evidence like: "Match score 0.76"
      score out of 40

    Returns:
      score (int): 0..40
      fired (bool)
      evidence (str)
    """
    target_path = target_info["path"]

    # Safety checks
    if not os.path.exists(target_path):
        return 0, False, "Target missing"
    if not os.path.exists(input_path):
        return 0, False, "Input missing"

    # Load images (grayscale for template matching)
    target_img = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
    input_img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    if target_img is None or input_img is None:
        return 0, False, "Could not load image(s)"

    th, tw = target_img.shape[:2]
    ih, iw = input_img.shape[:2]

    # Decide which is template and which is search image
    # Template MUST be smaller than (or equal to) the search image in both dims.
    if th <= ih and tw <= iw:
        template = target_img
        search = input_img
    elif ih <= th and iw <= tw:
        template = input_img
        search = target_img
    else:
        # Fallback: take a centered patch from the larger image as the template
        # so template always fits. This keeps the rule from crashing.
        if th * tw >= ih * iw:
            big = target_img
            small_h, small_w = ih, iw
        else:
            big = input_img
            small_h, small_w = th, tw

        # Patch is 80% of the smaller image size
        patch_h = max(20, int(0.8 * small_h))
        patch_w = max(20, int(0.8 * small_w))

        bh, bw = big.shape[:2]
        y0 = max(0, (bh - patch_h) // 2)
        x0 = max(0, (bw - patch_w) // 2)

        template = big[y0:y0 + patch_h, x0:x0 + patch_w]

        # Search is the other image (or the larger one if needed)
        search = input_img if big is target_img else target_img

        # Ensure template fits; if still not, resize template down
        sh, sw = search.shape[:2]
        if template.shape[0] > sh or template.shape[1] > sw:
            new_w = min(template.shape[1], sw)
            new_h = min(template.shape[0], sh)
            template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Final guard
    sh, sw = search.shape[:2]
    th2, tw2 = template.shape[:2]
    if th2 > sh or tw2 > sw:
        return 0, False, "Template larger than target"

    # Template matching
    try:
        res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
    except cv2.error:
        return 0, False, "matchTemplate failed"

    # Convert to [0,1] similarity for scoring safety
    sim = float(max_val)
    sim = max(0.0, min(1.0, sim))

    # Score out of 40
    score = int(sim * 40)

    # Fire threshold (tune if needed)
    fired = sim >= 0.45

    evidence = f"Match score {sim:.2f}"
    return score, fired, evidence
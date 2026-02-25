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
    target_path = target_info["path"]

    if not os.path.exists(target_path) or not os.path.exists(input_path):
        return 0, False, "Missing file"

    A = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)  # original
    B = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)   # modified
    if A is None or B is None:
        return 0, False, "Could not load image(s)"

    hA, wA = A.shape[:2]
    hB, wB = B.shape[:2]

    # Template must be smaller than search in both dims
    if hB <= hA and wB <= wA:
        template, search = B, A
    elif hA <= hB and wA <= wB:
        template, search = A, B
    else:
        return 0, False, "No valid containment"

    res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    sim = max(0.0, min(1.0, float(max_val)))
    score = int(sim * 40)
    fired = sim >= 0.55  # slightly stricter than before
    evidence = f"Match score {sim:.2f}"
    return score, fired, evidence

def rule4_orb(target_info, input_path):
    """
    Rule 4 (ORB keypoints): robust to resize + compression.
    Score: 0..30 points
    Evidence: "ORB good matches X/Y"
    """
    target_path = target_info["path"]

    if not os.path.exists(target_path) or not os.path.exists(input_path):
        return 0, False, "Missing file"

    img_t = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
    img_i = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img_t is None or img_i is None:
        return 0, False, "Could not load image(s)"

    # ORB detector (interpretable feature matching)
    orb = cv2.ORB_create(nfeatures=800)

    kp1, des1 = orb.detectAndCompute(img_t, None)
    kp2, des2 = orb.detectAndCompute(img_i, None)

    if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
        return 0, False, "ORB insufficient keypoints"

    # Brute-force matcher for ORB (Hamming distance)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    try:
        matches = bf.knnMatch(des1, des2, k=2)
    except cv2.error:
        return 0, False, "ORB match failed"

    # Lowe-style ratio test (keeps matches reliable)
    good = []
    for m_n in matches:
        if len(m_n) != 2:
            continue
        m, n = m_n
        if m.distance < 0.75 * n.distance:
            good.append(m)

    good_count = len(good)

    # Convert to score out of 30.
    # Cap at 60 good matches => full points (tune later).
    score = int(min(1.0, good_count / 500.0) * 30)

    # Fire if enough good matches
    fired = good_count >= 90

    evidence = f"ORB good matches {good_count}"
    return score, fired, evidence
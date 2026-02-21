"""
EAS 510 - Expert System Rules
"""
import os

def rule1_metadata(target_info, input_path):
    """Rule 1: Compare file sizes."""
    input_size = os.path.getsize(input_path)
    target_size = target_info['size']

    # Calculate ratio (0.0 to 1.0)
    if target_size > 0 and input_size > 0:
        ratio = min(input_size, target_size) / max(input_size, target_size)
    else:
        ratio = 0

    # Convert to score (0-30 points)
    score = int(ratio * 30)
    fired = ratio > 0.3
    evidence = f"Size ratio {ratio:.2f}"

    return score, fired, evidence
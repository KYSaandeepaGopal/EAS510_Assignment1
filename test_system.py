import os
import re
from forensics_detective import SimpleDetective

IMG_EXTS = (".jpg", ".jpeg", ".png")


def list_images(folder):
    return sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(IMG_EXTS)
    ])


def expected_original_from_modified(filename):
    """
    modified_03_compressed.jpg -> original_03.jpg
    """
    m = re.search(r"modified_(\d{2})_", filename)
    if not m:
        return None
    idx = m.group(1)
    return f"original_{idx}.jpg"


def expected_original_from_hard(filename):
    """
    original_03__resize_scale75__compress__q45__v3.jpg -> original_03.jpg
    """
    m = re.search(r"^original_(\d{2})", filename)
    if not m:
        return None
    idx = m.group(1)
    return f"original_{idx}.jpg"


def main():
    detective = SimpleDetective()
    detective.register_targets("originals")

    # ------------------------
    # MODIFIED (accuracy)
    # ------------------------
    print("\n" + "=" * 60)
    print("EVALUATING MODIFIED IMAGES (V2)")
    print("=" * 60)

    modified_files = list_images("modified_images")
    correct_mod = 0

    for path in modified_files:
        result = detective.find_best_match(path)
        predicted = result["best_match"]
        expected = expected_original_from_modified(os.path.basename(path))
        if predicted == expected:
            correct_mod += 1

    total_mod = len(modified_files)
    acc_mod = (correct_mod / total_mod) * 100 if total_mod else 0.0

    # ------------------------
    # RANDOM (false positives)
    # ------------------------
    print("\n" + "=" * 60)
    print("EVALUATING RANDOM IMAGES (V2)")
    print("=" * 60)

    random_files = list_images("random")
    false_pos = 0

    for path in random_files:
        result = detective.find_best_match(path)
        if result["best_match"] is not None:
            false_pos += 1

    total_rand = len(random_files)
    fpr = (false_pos / total_rand) * 100 if total_rand else 0.0

    # ------------------------
    # HARD (accuracy)
    # ------------------------
    print("\n" + "=" * 60)
    print("EVALUATING HARD IMAGES (V2)")
    print("=" * 60)

    hard_files = list_images("hard")
    correct_hard = 0
    skipped_hard = 0

    for path in hard_files:
        fname = os.path.basename(path)
        expected = expected_original_from_hard(fname)

        if expected is None:
            skipped_hard += 1
            # Still run it (so your output file includes everything),
            # but we won't count it in accuracy if we can't infer truth.
            detective.find_best_match(path)
            continue

        result = detective.find_best_match(path)
        predicted = result["best_match"]

        if predicted == expected:
            correct_hard += 1

    total_hard = len(hard_files) - skipped_hard
    acc_hard = (correct_hard / total_hard) * 100 if total_hard else 0.0

    # ------------------------
    # SUMMARY
    # ------------------------
    print("\n" + "=" * 60)
    print("SUMMARY (V2)")
    print("=" * 60)
    print(f"Modified Accuracy: {correct_mod}/{len(modified_files)} = {acc_mod:.1f}%")
    print(f"Random False Positive Rate: {false_pos}/{len(random_files)} = {fpr:.1f}%")
    print(f"Hard Accuracy: {correct_hard}/{total_hard} = {acc_hard:.1f}% (skipped {skipped_hard})")
    print("=" * 60)


if __name__ == "__main__":
    main()
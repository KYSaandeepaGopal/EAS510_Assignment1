# EAS 510 Assignment 1: Digital Forensics Apprentice

Dataset for building a rule-based expert system that matches modified images back to their originals.

## Dataset Structure

```
EAS510_Assignment1/
├── originals/        # 10 original JPEG images
├── modified_images/  # 60 "easy" cases (single transformations)
├── hard/             # 60 "hard" cases (combined transformations)
└── random/           # 15 unrelated images (should be rejected)
```

## Transformations

### Easy Cases (modified_images/)
Each original has 6 modifications:
- Brightness enhancement
- JPEG compression
- 25% crop (center)
- 50% crop (center)
- 75% crop (center)
- PNG format conversion

### Hard Cases (hard/)
Each original has 6 challenging modifications:
- **v1**: Off-center crop + compression
- **v2**: Crop + brightness + compression
- **v3**: Resize + compression
- **v4**: Rotation + compression
- **v5**: Contrast + compression
- **v6**: Crop + resize + compression

## Ground Truth

The filename prefix indicates which original each image was derived from:
- `modified_03_brightness.jpg` → `original_03.jpg`
- `original_03__rotate6deg__compress__q50__v4.jpg` → `original_03.jpg`

Images in `random/` are not derived from any original and should be rejected.

## Setup

```bash
pip install pillow opencv-python numpy
```

## Usage

Clone this repository and use the images to build and test your forensic matching system:

```bash
git clone https://github.com/delveccj/EAS510_Assignment1.git
cd EAS510_Assignment1
```

Your system should:
1. Register the 10 original images
2. For each test image, determine which original it came from (or reject it)
3. Display transparent reasoning showing how each rule contributed to the decision



▶ Running the System

The evaluation script is:

test_system.py

Run:

python test_system.py

To save results:

python test_system.py > results.txt

The script evaluates:

modified_images/

hard/

random/

🟢 Phase 1 – Version 1 (V1)
Rules Used
Rule	Description	Points
Rule 1	Metadata (file size, dimensions, aspect ratio)	30
Rule 2	Color histogram similarity	30
Rule 3	Template matching (cv2.matchTemplate)	40
Total		100
V1 Threshold Adjustment

Initially:

threshold = 25

This caused some random images to match incorrectly.

The threshold was increased to:

threshold = 40

This made the system more conservative and reduced false positives.

🔴 V1 Failure Analysis (Hard Cases)

Using the output from the hard/ folder, a systematic weakness was identified.

Observed Failure Pattern

V1 struggled with:

Resize transformations

Rotation

Crop + resize combinations

Resize + compression combinations

Why?

Rule 3 (Template Matching) is:

Not scale invariant

Not rotation invariant

Dependent on pixel alignment

When geometry changed, template correlation dropped significantly.

Example

Resize case:

original_00__resize_scale114__compress__q45__v3.jpg
Rule 3: 0.38 → 15/40
Final: 67/100

Rotation case:

original_00__rotate6deg__compress__q35__v4.jpg
Rule 3: 0.39 → 15/40
Final: 67/100

In these cases, histogram similarity remained high, which sometimes caused incorrect or fragile matches.

This revealed a structural weakness in V1.

🔵 Phase 2 – Version 2 (V2)

To address the geometric weakness, Rule 4 was introduced.

🟢 Rule 4 – ORB Feature Matching

ORB (Oriented FAST + Rotated BRIEF) was selected because:

Robust to rotation

More robust to scale changes

Handles compression reasonably well

Remains interpretable (counts good keypoint matches)

V2 Scoring
Rule	Points
Rule 1 – Metadata	20
Rule 2 – Histogram	20
Rule 3 – Template	30
Rule 4 – ORB	30
Total	100
ORB Tuning

Final tuning:

score = int(min(1.0, good_count / 500.0) * 30)
fired = good_count >= 90
Why divide by 500?

Earlier scaling caused early saturation (almost all matches got full points).
Dividing by 500:

Prevents early saturation

Gives proportional scoring

Improves discrimination between moderate and strong matches

Why minimum 90 to fire?

Prevents weak structural coincidences

Reduces false positives

Ensures meaningful feature agreement

📈 Effect of V2

Easy cases remained strong.

Hard cases improved significantly under:

Resize

Rotation

Crop + resize

ORB provided structural evidence when template matching weakened.

⚖ Trade-offs Introduced by Rule 4

Increased computational cost (feature extraction is heavier)

Requires careful threshold tuning

Sensitive to low-texture images

Introduces additional parameter calibration

🧠 Key Takeaways

Template matching is powerful but fragile under geometric transformations.

Histogram similarity alone cannot guarantee structural correctness.

Rule-based systems require careful threshold tuning.

Targeted rule addition (ORB) improved robustness without machine learning.

Interpretability was maintained in both versions.

Accuracy depends heavily on threshold selection in both V1 and V2.

In V1, increasing threshold from 25 → 40 reduced false positives.

In V2, threshold set to 60 makes the system more conservative.

Lowering V2 threshold may increase measured accuracy but reduce reliability.

Therefore:

Accuracy alone is not the only measure of system quality.

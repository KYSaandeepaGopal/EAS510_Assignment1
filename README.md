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



📂 Project Structure

project/
│
├── originals/          # Original reference images
├── modified_images/    # Easy cases
├── random/             # Unrelated images
├── hard/               # Combined transformations
│
├── forensics_detective.py
├── rules.py
├── test_system.py
│
├── results_v1.txt, results_v1_hard.txt
├── results_v2.txt
└── README.md

▶ Running the System (V1 and V2)

test_system.py is the unified evaluation script.

Each run evaluates:

modified_images/

random/

hard/

🟢 Phase 1 – Version 1 (V1)
V1 Rules:

Rule 1 – Metadata (30 pts)

Rule 2 – Histogram (30 pts)

Rule 3 – Template Matching (40 pts)

Total = 100 points

Rule 4 (ORB) does not exist in V1.

V1 Threshold

Initially:

threshold = 25

This caused some random images to match incorrectly.

To improve robustness and reduce false positives, the threshold was increased to:

threshold = 40

This required stronger agreement across rules before declaring a match.

Running V1

Ensure:

rule4_orb() is removed from rules.py

No Rule 4 import or scoring exists in forensics_detective.py

Scoring is 30/30/40

max_possible = 100

Then run:

python test_system.py > results_v1.txt

This evaluates modified, random, and hard folders in one execution.

Hard-case failures are identified by inspecting the hard/ section of results_v1.txt.

🔴 V1 Hard-Case Analysis (Systematic Failure Pattern)
1️⃣ Observed Weakness in V1: What failed and why?

V1 struggles most on hard cases involving:

Resize / scale changes

Rotation

Crop + resize combinations

Resize + compression

The primary failure occurs in Rule 3 (Template Matching).

Template matching is:

Not scale-invariant

Not rotation-invariant

So when geometry changes, correlation drops significantly.

Evidence from results_v1.txt:

Resize case

original_00__resize_scale114__compress__q45__v3.jpg
Rule 3: 0.38 → 15/40
Final: 67/100

Rotation case

original_00__rotate6deg__compress__q35__v4.jpg
Rule 3: 0.39 → 15/40
Final: 67/100

Crop + Resize case

original_00__crop_keep60__resized__q45__v6.jpg
Rule 3: 0.12 → 4/40
Final: 52/100

When Rule 3 weakens, the system relies more heavily on:

Rule 1 (Metadata)

Rule 2 (Histogram)

However, histogram similarity can remain high even for visually similar but incorrect images.

Example incorrect match:

original_02__resize_scale85__compress__q30__v3.jpg
Rule 2: 0.906 → 27/30
Rule 3: 0.08 → 3/40
Final: MATCH to original_01.jpg (Incorrect)

This shows a systematic failure pattern:

Resize/rotation → Template score collapses → Histogram dominates → Wrong candidate can win.

🔵 Phase 2 – Version 2 (V2)

To address V1’s structural weakness, Rule 4 was added.

🟢 Rule 4 – ORB Feature Matching (30 pts)

ORB (Oriented FAST + Rotated BRIEF) was selected because it:

Is more robust to scale changes

Is more robust to rotation

Handles compression reasonably well

Remains fully interpretable (counts good keypoint matches)

ORB Tuning (Final Version)

Based on empirical observation of match counts:

Strong matches: 400–800 good matches

Moderate matches: 200–350

Weak/noise: <50

Final scoring:

score = int(min(1.0, good_count / 500.0) * 30)
fired = good_count >= 90
Why divide by 500?

Previously dividing by 60 caused early saturation (almost every real match got 30/30).
Dividing by 500:

Prevents early saturation

Gives partial credit to moderate matches

Makes ORB more discriminative

Prevents bias toward structural overconfidence

Why minimum 90 to fire?

Prevents weak structural coincidences

Reduces risk of random false positives

Ensures meaningful feature agreement

V2 Scoring Structure
Rule	Points
Rule 1	20
Rule 2	20
Rule 3	30
Rule 4 (ORB)	30
Total	100
Running V2

Ensure:

Rule 4 exists in rules.py

It is imported and applied in forensics_detective.py

Scoring is rebalanced to 20/20/30/30

Then run:

python test_system.py > results_v2.txt
📈 Effect of the Change
Easy Cases (modified_images/)

V1 already performed strongly on simple edits:

Brightness

Compression

Format change

Moderate cropping

V2 preserves this strong performance.

Hard Cases (hard/)

V2 improves robustness on:

Resize cases

Rotation cases

Crop + resize combinations

Where V1 template matching weakened, ORB now provides structural evidence.

Example improvement:

original_00__rotate6deg__compress__q35__v4.jpg
Rule 3 weak (0.39)
Rule 4 strong (hundreds of matches)
Final: Correct match retained

V2 maintains accuracy on easy cases while improving reliability on geometric transformations.

⚖ Trade-Offs Introduced by Rule 4

Adding ORB introduced new considerations:

1️⃣ Increased Runtime

Feature detection and matching increases computational cost compared to metadata and histogram rules.

2️⃣ Sensitivity to Extreme Crops / Low Texture

If an image has very few detectable features, ORB may contribute little evidence.

3️⃣ Need for Careful Threshold Tuning

Poor scaling (e.g., dividing by 60) caused early saturation and biased scoring.
Proper tuning (500 cap, 90 fire threshold) was necessary to maintain balance.

4️⃣ Additional Parameter Sensitivity

ORB introduces hyperparameters (match thresholds, ratio test), requiring empirical adjustment.

🧠 Key Takeaways:

Template matching is powerful but fragile under geometric transformations.
Resize and rotation significantly weaken correlation-based matching.

Histogram similarity alone is insufficient for structural verification.
Images with similar global color distributions can produce high similarity scores even when structurally different.

Rule-based systems require careful threshold tuning.
Small changes in scoring thresholds can significantly alter system behavior.

Targeted rule addition (ORB) can systematically address diagnosed weaknesses.
Instead of replacing the system with machine learning, we added a geometric-robust rule while maintaining interpretability.

Maintaining interpretability while improving robustness is possible without machine learning.
Each rule contributes explainable evidence to the final decision.

Accuracy depends heavily on threshold selection in both V1 and V2.

In V1, increasing the threshold from 25 to 40 reduced false positives and improved robustness.

In V2, using a threshold of 60 makes the system more conservative.

Lowering the threshold in V2 would increase measured accuracy but could reduce reliability and increase false positives.

Therefore, accuracy alone is not the sole measure of system quality.

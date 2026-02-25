"""
EAS 510 - Digital Forensics Detective
"""
import os
from rules import rule1_metadata, rule2_histogram, rule3_template, rule4_orb

class SimpleDetective:
    """An expert system that matches modified images to originals."""

    def __init__(self):
        self.targets = {}  # filename -> signature

    def register_targets(self, folder):
        """Load original images and compute signatures."""
        print(f"Loading targets from: {folder}")

        for filename in os.listdir(folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(folder, filename)
                file_size = os.path.getsize(filepath)

                self.targets[filename] = {
                    'path': filepath,
                    'size': file_size
                }
                print(f"  Registered: {filename} ({file_size} bytes)")

        print(f"Total targets: {len(self.targets)}")
    

    def find_best_match(self, input_image_path):
        print(f"\nProcessing: {os.path.basename(input_image_path)}")
        results = []

        # simple helper for rebalancing
        def _scale(score, old_max, new_max):
            if old_max <= 0:
                return 0
            scaled = int(round(score * new_max / old_max))
            return max(0, min(new_max, scaled))

        for target_name, target_info in self.targets.items():
            # Apply Rule 1: Metadata (raw /30)
            score1, fired1, evidence1 = rule1_metadata(target_info, input_image_path)

            # Apply Rule 2: Histogram (raw /30)
            score2, fired2, evidence2 = rule2_histogram(target_info, input_image_path)

            # Apply Rule 3: Template (raw /40)
            score3, fired3, evidence3 = rule3_template(target_info, input_image_path)

            # Apply Rule 4: ORB (raw /30)
            score4, fired4, evidence4 = rule4_orb(target_info, input_image_path)

            # Rebalance to V2 weights: 20/20/30/30 => total 100
            score1_v2 = _scale(score1, 30, 20)
            score2_v2 = _scale(score2, 30, 20)
            score3_v2 = _scale(score3, 40, 30)
            score4_v2 = _scale(score4, 30, 30)  # unchanged

            # Combine scores (now /100)
            total_score = score1_v2 + score2_v2 + score3_v2 + score4_v2
            max_possible = 100

            results.append({
                'target': target_name,
                'score': total_score,
                'max_score': max_possible,
                'rules': [
                    (fired1, evidence1, score1_v2, 20),
                    (fired2, evidence2, score2_v2, 20),
                    (fired3, evidence3, score3_v2, 30),
                    (fired4, evidence4, score4_v2, 30)
                ]
            })

        # Sort by score, highest first
        results.sort(key=lambda x: x['score'], reverse=True)
        best = results[0]

        # Print rule details for best match (format consistent)
        print(f"  Rule 1 (Metadata):  {'FIRED' if best['rules'][0][0] else 'NO MATCH'} - {best['rules'][0][1]} -> {best['rules'][0][2]}/{best['rules'][0][3]} points")
        print(f"  Rule 2 (Histogram): {'FIRED' if best['rules'][1][0] else 'NO MATCH'} - {best['rules'][1][1]} -> {best['rules'][1][2]}/{best['rules'][1][3]} points")
        print(f"  Rule 3 (Template):  {'FIRED' if best['rules'][2][0] else 'NO MATCH'} - {best['rules'][2][1]} -> {best['rules'][2][2]}/{best['rules'][2][3]} points")
        print(f"  Rule 4 (ORB):       {'FIRED' if best['rules'][3][0] else 'NO MATCH'} - {best['rules'][3][1]} -> {best['rules'][3][2]}/{best['rules'][3][3]} points")

        # Decision threshold: 60/100 is a good starting point
        threshold = 60
        if best['score'] >= threshold:
            print(f"Final Score: {best['score']}/{best['max_score']} -> MATCH to {best['target']}")
            return {'best_match': best['target'], 'confidence': best['score']}
        else:
            print(f"Final Score: {best['score']}/{best['max_score']} -> REJECTED")
            return {'best_match': None, 'confidence': best['score']}

if __name__ == "__main__":
    print("=" * 50)
    print("SimpleDetective - Prototype v0.1")
    print("=" * 50)

    detective = SimpleDetective()
    detective.register_targets("originals")

    print("\n" + "=" * 50)
    print("TESTING")
    print("=" * 50)

    test_images = [
        "modified_images/modified_00_bright_enhanced.jpg",
        "modified_images/modified_03_compressed.jpg",
        "modified_images/modified_00_crop_75pct.jpg",
        "modified_images/modified_08_crop_75pct.jpg",
        "modified_images/modified_07_format_png.png",
        "random/random_noise_01.jpg",
    ]

    for img in test_images:
        if os.path.exists(img):
            detective.find_best_match(img)

    print("\n" + "=" * 50)
    print("PROTOTYPE COMPLETE!")
    print("=" * 50)
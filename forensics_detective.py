"""
EAS 510 - Digital Forensics Detective
"""
import os
from rules import rule1_metadata, rule2_histogram

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

        for target_name, target_info in self.targets.items():
            # Apply Rule 1: Metadata
            score1, fired1, evidence1 = rule1_metadata(target_info, input_image_path)

            # Apply Rule 2: Histogram
            score2, fired2, evidence2 = rule2_histogram(target_info, input_image_path)

            # Combine scores
            total_score = score1 + score2
            max_possible = 30 + 35  # Rule 1 max + Rule 2 max

            results.append({
                'target': target_name,
                'score': total_score,
                'max_score': max_possible,
                'rules': [(fired1, evidence1, score1), (fired2, evidence2, score2)]
            })

        # Sort by score, highest first
        results.sort(key=lambda x: x['score'], reverse=True)
        best = results[0]

        # Print rule details for best match
        print(f"  Rule 1 (Metadata):  {best['rules'][0][1]} -> {best['rules'][0][2]}/30")
        print(f"  Rule 2 (Histogram): {best['rules'][1][1]} -> {best['rules'][1][2]}/35")

        # Decision threshold: need at least 25% of max score
        threshold = best['max_score'] * 0.25
        if best['score'] >= threshold:
            print(f"Final: {best['score']}/{best['max_score']} -> MATCH to {best['target']}")
            return {'best_match': best['target'], 'confidence': best['score']}
        else:
            print(f"Final: {best['score']}/{best['max_score']} -> REJECTED")
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
    ]

    for img in test_images:
        if os.path.exists(img):
            detective.find_best_match(img)

    print("\n" + "=" * 50)
    print("PROTOTYPE COMPLETE!")
    print("=" * 50)
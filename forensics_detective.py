"""
EAS 510 - Digital Forensics Detective
"""
import os
from rules import rule1_metadata

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
            score, fired, evidence = rule1_metadata(target_info, input_image_path)
            results.append({'target': target_name, 'score': score,
                            'fired': fired, 'evidence': evidence})

        results.sort(key=lambda x: x['score'], reverse=True)
        best = results[0]

        status = "FIRED" if best['fired'] else "NO MATCH"
        print(f"  Rule 1 (Metadata): {status} - {best['evidence']} -> {best['score']}/30")

        if best['score'] >= 10:
            print(f"Final: {best['score']}/30 -> MATCH to {best['target']}")
            return {'best_match': best['target'], 'confidence': best['score']}
        else:
            print(f"Final: {best['score']}/30 -> REJECTED")
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
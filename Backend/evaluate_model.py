#!/usr/bin/env python3
"""
Comprehensive model evaluation to identify prediction issues
"""

import os
import sys
from collections import defaultdict

# Add AI path
ai_path = os.path.join(os.path.dirname(__file__), "..", "Ai", "efficientNet")
sys.path.append(ai_path)


def evaluate_model():
    """Evaluate model accuracy across all test classes"""
    try:
        from test_api_integration import PriceClassifierAPI

        api = PriceClassifierAPI()

        test_dir = os.path.join("..", "Ai", "data", "price", "test")
        if not os.path.exists(test_dir):
            print("❌ Test directory not found")
            return

        results = defaultdict(list)
        confusion_matrix = defaultdict(lambda: defaultdict(int))

        print("🔍 Evaluating model on test set...")
        print("=" * 60)

        total_correct = 0
        total_samples = 0

        for true_class in sorted(os.listdir(test_dir)):
            class_path = os.path.join(test_dir, true_class)
            if not os.path.isdir(class_path):
                continue

            images = [
                f
                for f in os.listdir(class_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]

            class_correct = 0
            print(f"\n📂 Testing {true_class} ({len(images)} images):")

            for img_file in images[:5]:  # Test first 5 images per class
                img_path = os.path.join(class_path, img_file)
                result = api.predict_from_file(img_path)

                if result["success"]:
                    predicted = result["product_type"]
                    confidence = result["confidence"]

                    is_correct = predicted == true_class
                    if is_correct:
                        class_correct += 1
                        total_correct += 1

                    total_samples += 1
                    confusion_matrix[true_class][predicted] += 1

                    status = "✅" if is_correct else "❌"
                    print(f"  {status} {img_file}: {predicted} ({confidence:.3f})")

                    results[true_class].append(
                        {
                            "image": img_file,
                            "predicted": predicted,
                            "confidence": confidence,
                            "correct": is_correct,
                        }
                    )
                else:
                    print(f"  ❌ {img_file}: Error - {result.get('error', 'Unknown')}")

            accuracy = class_correct / min(len(images), 5) * 100
            print(
                f"  📊 Class accuracy: {accuracy:.1f}% ({class_correct}/{min(len(images), 5)})"
            )

        # Overall results
        overall_accuracy = (
            total_correct / total_samples * 100 if total_samples > 0 else 0
        )
        print("\n" + "=" * 60)
        print(
            f"📈 Overall Accuracy: {overall_accuracy:.1f}% ({total_correct}/{total_samples})"
        )

        # Confusion matrix summary
        print("\n🔄 Confusion Matrix (True → Predicted):")
        for true_class in sorted(confusion_matrix.keys()):
            predictions = confusion_matrix[true_class]
            most_predicted = max(predictions.items(), key=lambda x: x[1])
            print(f"  {true_class} → {most_predicted[0]} ({most_predicted[1]} times)")

        # Recommendations
        print("\n💡 Recommendations:")
        if overall_accuracy < 50:
            print("  ⚠️  Model accuracy is very low - needs retraining")
            print("  🔄 Consider:")
            print("     - More training epochs")
            print("     - Better data augmentation")
            print("     - Data quality review")
        elif overall_accuracy < 80:
            print("  📈 Model needs improvement - try fine-tuning")
        else:
            print("  ✅ Model performance is acceptable")

        return overall_accuracy

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return 0


if __name__ == "__main__":
    print("Model Evaluation")
    print("=" * 60)
    evaluate_model()

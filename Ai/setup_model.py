from pathlib import Path
from ultralytics import YOLO

def setup_custom_model():
    """Setup a custom YOLO model for ceramic detection"""
    
    model_save_path = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\custom_yolo_model.pt"
    dataset_yaml = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\custom_dataset\dataset.yaml"
    
    print("Setting up custom YOLO model...")
    
    # Create models directory
    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Download and save a pre-trained YOLOv8 nano model
    model = YOLO('yolov8n.pt')
    
    # Save the model to our custom path
    model.save(model_save_path)
    
    print(f"✅ Model saved to: {model_save_path}")
    
    # Create a class mapping file for your ceramic classes
    classes = [
        'Ceramic Vase',
        'Ceramic Cups', 
        'Handcrafted Tamegroute Ceramic Cake Stand with Sca',
        'White Ceramic Divided Plate with Silver Accents  5',
        'Tamegroute Ceramic Pitcher  Handmade Moroccan Wate'
    ]
    
    class_mapping = {
        'model_path': model_save_path,
        'classes': classes,
        'dataset': dataset_yaml,
        'note': 'This is a base YOLOv8n model. For better performance on ceramics, train with your dataset.'
    }
    
    import json
    with open(Path(model_save_path).parent / 'model_info.json', 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    return model_save_path, classes

def test_model(model_path, test_image_path):
    """Test the model on an image"""
    
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    if not Path(test_image_path).exists():
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    try:
        # Load model
        model = YOLO(model_path)
        
        # Run inference
        results = model(test_image_path)
        
        # Save results
        output_dir = Path("inference_results")
        output_dir.mkdir(exist_ok=True)
        
        for i, result in enumerate(results):
            result.save(output_dir / f"result_{i}.jpg")
        
        print(f"✅ Inference completed! Results saved to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        return False

def main():
    print("🏺 Custom YOLO Model Setup for Ceramic Detection")
    print("=" * 50)
    
    # Setup model
    model_path, classes = setup_custom_model()
    
    print(f"\nClasses detected: {len(classes)}")
    for i, cls in enumerate(classes):
        print(f"  {i}: {cls}")
    
    # Test with a sample image
    test_image = r"c:\Users\boume\Briefs\Filrouge2A\images\product_1_Ceramic Vase\image_1.jpg"
    
    print(f"\n🧪 Testing model with: {test_image}")
    success = test_model(model_path, test_image)
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print(f"📁 Model location: {model_path}")
        print("📊 Dataset config: c:\\Users\\boume\\Briefs\\Filrouge2A\\Ai\\data\\custom_dataset\\dataset.yaml")
        print("\n💡 To train the model on your data:")
        print("   1. Fix the MLflow issue in your environment")
        print("   2. Or use a different machine/environment for training")
        print("   3. The dataset is already prepared and ready for training")
    else:
        print("\n⚠️  Setup completed but testing failed")

if __name__ == "__main__":
    main()
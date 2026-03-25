# 🤖 Morocco Chatbot Setup Guide

## Quick Start

### 1. Install Ollama
```bash
# Windows/Mac/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai
```

### 2. Pull a Model
```bash
# Recommended: Fast and good quality
ollama pull llama3.2

# Alternatives:
ollama pull llama3.1      # Better quality, slower
ollama pull mistral       # Good alternative
ollama pull qwen2.5       # Multilingual support
```

### 3. Start Ollama Server
```bash
ollama serve
```

### 4. Test Setup
Run the test script:
```bash
# Windows
test_ollama.bat

# Linux/Mac
chmod +x test_ollama.sh
./test_ollama.sh
```

## 🎯 Usage

### Test Questions:
- "Tell me about Jemaa el-Fna"
- "What are the entrance fees for Bahia Palace?"
- "Where can I buy traditional Moroccan lanterns?"
- "How much do babouches cost?"
- "What's the best time to visit Majorelle Garden?"

### Features:
✅ **Local AI** - No internet required  
✅ **Privacy** - All data stays on your machine  
✅ **Fast** - Instant responses  
✅ **Smart** - Uses comprehensive Morocco knowledge base  
✅ **Navigation hints** - Mentions nearest souks/landmarks  

## 🔧 Troubleshooting

### "Connection error" message:
1. Make sure Ollama is installed: `ollama --version`
2. Start the server: `ollama serve`
3. Check if running: `curl http://localhost:11434/api/tags`

### Model not found:
1. List installed models: `ollama list`
2. Pull the model: `ollama pull llama3.2`
3. Update model name in LocationHelper.jsx if using different model

### Slow responses:
- Try a smaller model: `ollama pull llama3.2:1b`
- Or use quantized version: `ollama pull llama3.2:q4_0`

## 🚀 Advanced

### Custom Model:
```bash
# Use a specialized model
ollama pull codellama      # For technical questions
ollama pull dolphin-llama3 # Uncensored responses
```

### Model Configuration:
In LocationHelper.jsx, adjust these parameters:
```javascript
options: {
  temperature: 0.7,    // Creativity (0.1-1.0)
  top_p: 0.9,         // Response diversity
  max_tokens: 300     // Response length
}
```

## 🔄 Future: RAG Integration

When your RAG server is ready, replace the knowledge base:
```javascript
// Instead of MOROCCO_KB, use:
const ragResponse = await fetch('http://localhost:8002/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: userMsg.content, k: 4 })
});
const ragData = await ragResponse.json();
const knowledgeBase = ragData.answer || MOROCCO_KB;
```

## 📊 Performance Tips

- **RAM**: 8GB+ recommended for llama3.2
- **CPU**: More cores = faster responses
- **Storage**: Models are 2-7GB each
- **GPU**: Optional but speeds up responses significantly

---

🎉 **Your Morocco chatbot is now ready!** Ask about any Marrakech destination and get intelligent, contextual responses powered by your local AI model.
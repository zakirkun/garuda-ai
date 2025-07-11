# 🦅 Garuda AI Assistant - Quick Setup Guide

## Option 1: Automatic Setup (Recommended)

### 1. Run the quick setup script:
```bash
python quick_setup.py
```

This will automatically:
- ✅ Check Python version
- ✅ Create necessary directories
- ✅ Install dependencies
- ✅ Setup environment file
- ✅ Optionally configure API keys
- ✅ Verify installation

### 2. Start the application:
```bash
python run.py
```

### 3. Open your browser:
Go to `http://localhost:8501`

---

## Option 2: Manual Setup

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Setup environment:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run the application:
```bash
streamlit run gui/app.py
```

---

## 🔑 Getting API Keys

### OpenAI (Recommended)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env` file: `OPENAI_API_KEY=your_key_here`

### Anthropic (Optional)
1. Go to https://console.anthropic.com/
2. Get API key from settings
3. Add to `.env` file: `ANTHROPIC_API_KEY=your_key_here`

### Ollama (Free, Local)
1. Install Ollama: https://ollama.ai/
2. Run: `ollama pull llama3:8b`
3. Make sure Ollama is running on `http://localhost:11434`

---

## 🎯 First Steps

1. **Start with basic chat** - Test without RAG first
2. **Upload a document** - Try the sample_document.txt file
3. **Enable RAG** - Toggle "Use RAG" and ask questions about your document
4. **Explore settings** - Try different models and providers

---

## 🐛 Troubleshooting

### "Failed to initialize agent"
- Check your API keys in `.env` file
- Verify internet connection
- Try different provider in config

### "No models available"
- Check API key for selected provider
- Verify provider configuration in `config.yaml`

### ChromaDB errors
- Delete `data/vector_store/` folder
- Restart the application

### Import errors
- Run: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

---

## 💡 Pro Tips

- **Start with OpenAI** - Most reliable for testing
- **Use local Ollama** - Free option for privacy
- **Upload small documents first** - Test RAG functionality
- **Check logs** - Look in `logs/app.log` for errors
- **Enable debug mode** - In Settings tab for troubleshooting

---

**Need help? Check the full README.md for detailed documentation!** 
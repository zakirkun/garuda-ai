# 🇮🇩 Garuda AI Assistant - Indonesia Edition

**Asisten AI Cerdas untuk Bangsa Indonesia**

A sophisticated AI Assistant application designed with Indonesian national pride, featuring multi-provider LLM support, RAG (Retrieval-Augmented Generation) capabilities, and a modern interface inspired by Indonesian government colors.

## 🌟 Features / Fitur

### 🤖 Multi-Provider AI Support
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude-3 (Haiku, Sonnet, Opus), Claude-3.5 Sonnet
- **Ollama**: Local models (Llama, Mistral, CodeLlama)
- Automatic fallback system with rate limiting
- Smart provider selection based on availability

### 📚 RAG (Retrieval-Augmented Generation)
- ChromaDB vector database integration
- Document upload support (PDF, TXT, DOCX)
- Intelligent text chunking and embedding
- Semantic search with relevance scoring
- Source citation and reference tracking

### 💬 Advanced Conversation Management
- Multi-session conversation handling
- Persistent conversation memory
- Context-aware responses
- Token usage tracking and optimization
- Indonesian language support

### 🇮🇩 Indonesian Government Theme
- Official Indonesian colors (Red #FF0000, White #FFFFFF)
- Indonesian flag elements and national symbols
- Bilingual interface (Bahasa Indonesia & English)
- Cultural pride integrated throughout the application
- "Bhinneka Tunggal Ika" - Unity in Diversity theme

### 🎨 Modern User Interface
- Beautiful gradient designs with Indonesian colors
- Responsive design for all screen sizes
- Interactive charts and metrics
- Real-time provider status indicators
- Enhanced typography with Google Fonts
- Smooth animations and transitions

## 🚀 Quick Start / Memulai

### Prerequisites / Prasyarat
- Python 3.8 or higher
- Internet connection for API providers
- At least 4GB RAM recommended

### Installation / Instalasi

1. **Clone the repository / Kloning repositori**:
```bash
git clone <repository-url>
cd garuda-ai
```

2. **Run quick setup / Jalankan setup cepat**:
```bash
python quick_setup.py
```

3. **Set up your API keys / Atur API key Anda**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
```

4. **Run the application / Jalankan aplikasi**:
```bash
python run.py
```

The application will open in your browser at `http://localhost:8501` 🎉

## 📁 Project Structure / Struktur Proyek

```
garuda-ai/
├── 🇮🇩 core/                    # Core AI functionality
│   ├── agent.py                 # Main Garuda AI agent
│   ├── llm_integration.py       # Multi-provider LLM manager
│   └── vector_manager.py        # RAG and vector database
├── 🎨 gui/                      # Indonesian-themed interface
│   ├── app.py                   # Main Streamlit app with Indonesian colors
│   └── interface.py             # UI components with bilingual support
├── 📄 documents/                # Sample documents
├── 📋 config.yaml              # Application configuration
├── 🔧 requirements.txt         # Python dependencies
├── ⚙️ quick_setup.py           # Automated setup script
├── 🚀 run.py                   # Application launcher
└── 📖 README.md                # This file
```

## 🔧 Configuration / Konfigurasi

### API Providers / Provider API
Configure your preferred AI providers in the GUI settings panel or edit `config.yaml`:

```yaml
llm_providers:
  openai:
    models: ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    rate_limit: 60
  anthropic:
    models: ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
    rate_limit: 50
  ollama:
    models: ["llama2", "mistral", "codellama"]
    base_url: "http://localhost:11434"
```

### Vector Database Settings
- **Embedding Model**: `all-MiniLM-L6-v2` (lightweight, multilingual)
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Similarity Threshold**: 0.7

## 🎯 Usage Guide / Panduan Penggunaan

### 1. 💬 Chat Interface / Antarmuka Chat
- Start conversations in the main chat tab
- Enable RAG mode for document-enhanced responses
- Switch between AI providers seamlessly
- View conversation history and metadata

### 2. 📚 Document Management / Manajemen Dokumen
- Upload PDF, TXT, or DOCX files
- Documents are automatically processed and indexed
- View document statistics and manage uploads
- RAG automatically uses uploaded documents for context

### 3. ⚙️ Settings / Pengaturan
- Configure API keys for different providers
- Adjust model parameters (temperature, max tokens)
- Enable/disable RAG functionality
- Export/import conversation backups

### 4. 📊 Performance Monitoring / Pemantauan Kinerja
- Real-time provider status indicators
- Conversation and message statistics
- Token usage tracking
- Error monitoring and fallback status

## 🇮🇩 Indonesian Features / Fitur Indonesia

### Bahasa Indonesia Support
- Full bilingual interface (Indonesian & English)
- Indonesian language model responses
- Cultural context understanding
- Local terminology and expressions

### National Pride Elements
- Indonesian flag colors throughout the design
- National motto: "Bhinneka Tunggal Ika"
- Indonesian symbols and iconography
- Cultural sensitivity in responses

### Indonesian Government Color Scheme
- **Primary Red**: #FF0000 (Indonesian flag red)
- **Pure White**: #FFFFFF (Indonesian flag white)
- **Supporting Colors**: Various shades of red and neutral tones
- **Typography**: Professional, modern fonts
- **Gradients**: Smooth transitions maintaining national identity

## 🛠️ Advanced Features / Fitur Lanjutan

### Smart Fallback System
- Automatic provider switching on failures
- Rate limit detection and queue management
- Health monitoring for all providers
- Graceful degradation of service

### RAG Intelligence
- Semantic similarity search
- Multi-document context synthesis
- Source attribution and citations
- Relevance scoring and filtering

### Memory Management
- Conversation context preservation
- Token-aware history truncation
- Session-based memory isolation
- Efficient context window utilization

## 🔍 Troubleshooting / Pemecahan Masalah

### Common Issues / Masalah Umum

**1. API Key Issues / Masalah API Key**
```bash
# Check if API keys are properly set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**2. ChromaDB Issues / Masalah ChromaDB**
```bash
# Clear vector database if corrupted
rm -rf chroma_db/
```

**3. Dependencies Issues / Masalah Dependensi**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**4. Port Already in Use / Port Sudah Digunakan**
```bash
# Run on different port
streamlit run gui/app.py --server.port 8502
```

### Performance Tips / Tips Kinerja
- Use smaller models for faster responses
- Limit document size for RAG efficiency
- Monitor token usage to control costs
- Enable caching for repeated queries

## 🤝 Contributing / Berkontribusi

We welcome contributions to make Garuda AI even better for Indonesia! 🇮🇩

### Development Setup / Setup Pengembangan
1. Fork the repository
2. Create a feature branch
3. Make your changes with Indonesian pride
4. Test thoroughly
5. Submit a pull request

### Contribution Guidelines / Panduan Kontribusi
- Maintain Indonesian cultural sensitivity
- Follow the government color scheme
- Include both Indonesian and English documentation
- Test with multiple AI providers
- Ensure accessibility compliance

## 📜 License / Lisensi

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments / Penghargaan

- Indonesian Government for inspiration in design
- OpenAI, Anthropic, and Ollama for AI providers
- ChromaDB for vector database capabilities
- Streamlit for the beautiful web interface
- The Indonesian AI community for support

## 📞 Support / Dukungan

For support, feature requests, or questions:
- Create an issue on GitHub
- Email: support@garuda-ai.id (hypothetical)
- Join our Indonesian AI community

---

**🇮🇩 Membanggakan Indonesia melalui Teknologi AI**

*Proudly serving Indonesia through AI Technology*

---

## 🏆 Version History / Riwayat Versi

### v1.0.0 - Indonesia Edition (Current)
- 🇮🇩 Indonesian government color scheme implementation
- 🎨 Complete UI overhaul with national pride theme
- 🌐 Bilingual interface (Indonesian & English)
- 🤖 Multi-provider AI integration
- 📚 Advanced RAG functionality
- 💾 Conversation management system
- 🔧 Comprehensive settings panel

### Planned Features / Fitur yang Direncanakan
- 🗣️ Indonesian voice interaction
- 📱 Mobile application
- 🌍 Regional Indonesian language variants
- 🏛️ Government document integration
- 📊 Advanced analytics dashboard
- 🔒 Enhanced security features

---

**Garuda AI Assistant** - Where Indonesian innovation meets artificial intelligence! 🦅🇮🇩 
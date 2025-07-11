import streamlit as st
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from typing import Dict, List, Any

def render_welcome_message():
    """Render welcome message with Indonesian theme"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #FFE6E6 0%, #FFFFFF 100%); border-radius: 15px; margin: 2rem 0; border: 2px solid rgba(255, 0, 0, 0.2);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🇮🇩</div>
        <h2 style="color: #FF0000; margin-bottom: 1rem; font-weight: 700;">Selamat Datang di Garuda AI!</h2>
        <p style="color: #6C757D; font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.6;">
            Asisten AI yang dirancang khusus untuk melayani kebutuhan teknologi Indonesia.<br>
            Mulai percakapan baru untuk merasakan kekuatan AI yang membanggakan bangsa!
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
            <div style="text-align: center; color: #FF0000;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                <div style="font-weight: 600;">Multi-Provider AI</div>
                <div style="font-size: 0.9rem; color: #6C757D;">OpenAI, Anthropic, Ollama</div>
            </div>
            <div style="text-align: center; color: #FF0000;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                <div style="font-weight: 600;">RAG Technology</div>
                <div style="font-size: 0.9rem; color: #6C757D;">Document Intelligence</div>
            </div>
            <div style="text-align: center; color: #FF0000;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                <div style="font-weight: 600;">Memory System</div>
                <div style="font-size: 0.9rem; color: #6C757D;">Context Awareness</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(agent, config):
    """Render enhanced sidebar with Indonesian government theme"""
    with st.sidebar:
        # Indonesian flag header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem; background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%); border-radius: 10px; color: white;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🇮🇩</div>
            <div style="font-weight: 700; font-size: 1.2rem;">GARUDA AI</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Asisten AI Indonesia</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Session Management
        st.markdown("### 💬 Manajemen Sesi")
        
        # Initialize current session if not set
        if not hasattr(st.session_state, 'current_session_id'):
            st.session_state.current_session_id = "default"
        
        # Current session info
        current_session_id = st.session_state.current_session_id
        if current_session_id in agent.sessions:
            session = agent.sessions[current_session_id]
            session_count = len(session.get_messages())
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Sesi Aktif</div>
                <div style="color: #FF0000; font-weight: 600; margin-bottom: 0.5rem;">{current_session_id}</div>
                <div style="color: #6C757D; font-size: 0.9rem;">{session_count} pesan</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Session selector
        available_sessions = list(agent.sessions.keys()) if agent.sessions else []
        if available_sessions:
            selected_session = st.selectbox(
                "Pilih Sesi:",
                options=available_sessions,
                index=available_sessions.index(current_session_id) if current_session_id in available_sessions else 0,
                key="session_selector"
            )
            
            if selected_session != current_session_id:
                st.session_state.current_session_id = selected_session
                st.rerun()
        
        # New session button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 Sesi Baru", use_container_width=True):
                new_session = f"Session_{datetime.now().strftime('%H%M%S')}"
                st.session_state.current_session_id = new_session
                agent.create_session(new_session)
                st.rerun()
        
        with col2:
            if st.button("🗑️ Hapus Sesi", use_container_width=True):
                if current_session_id and current_session_id in agent.sessions:
                    del agent.sessions[current_session_id]
                    remaining_sessions = list(agent.sessions.keys())
                    st.session_state.current_session_id = remaining_sessions[0] if remaining_sessions else "default"
                    if not remaining_sessions:
                        agent.create_session("default")
                    st.rerun()
        
        st.divider()
        
        # Provider Status with Indonesian styling
        st.markdown("### 🔧 Status Provider")
        
        provider_status = get_provider_status(agent, config)
        for provider, status in provider_status.items():
            status_icon = "🟢" if status["connected"] else "🔴"
            status_text = "Terhubung" if status["connected"] else "Terputus"
            status_class = "status-connected" if status["connected"] else "status-error"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: rgba(255, 255, 255, 0.1); border-radius: 8px; margin-bottom: 0.5rem;">
                <span style="color: white; font-weight: 500;">{status_icon} {provider.title()}</span>
                <span class="{status_class}" style="font-size: 0.8rem;">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Model Selection
        st.markdown("### 🎯 Pemilihan Model")
        render_model_selector(agent, config)
        
        st.divider()
        
        # Performance Metrics
        st.markdown("### 📊 Metrik Kinerja")
        render_performance_metrics(agent)
        
        st.divider()
        
        # Indonesian Pride Footer
        st.markdown("""
        <div style="text-align: center; padding: 1rem; margin-top: 2rem; background: rgba(255, 255, 255, 0.1); border-radius: 8px;">
            <div style="color: white; font-size: 0.9rem; font-style: italic;">
                "Bhinneka Tunggal Ika"
            </div>
            <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.8rem; margin-top: 0.5rem;">
                Unity in Diversity through Technology
            </div>
        </div>
        """, unsafe_allow_html=True)

def get_provider_status(agent, config) -> Dict[str, Dict[str, Any]]:
    """Get status of all providers"""
    status = {}
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    status["openai"] = {
        "connected": bool(openai_key and len(openai_key) > 10),
        "models": config.get("llm_providers", {}).get("openai", {}).get("models", [])
    }
    
    # Check Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    status["anthropic"] = {
        "connected": bool(anthropic_key and len(anthropic_key) > 10),
        "models": config.get("llm_providers", {}).get("anthropic", {}).get("models", [])
    }
    
    # Check Ollama
    status["ollama"] = {
        "connected": True,  # Assume available locally
        "models": config.get("llm_providers", {}).get("ollama", {}).get("models", [])
    }
    
    return status

def render_model_selector(agent, config):
    """Render model selector with Indonesian styling"""
    available_models = get_available_models(config)
    
    if not available_models:
        st.warning("⚠️ Tidak ada model yang tersedia. Periksa konfigurasi API key.")
        return
    
    # Model selector
    model_options = []
    for provider, models in available_models.items():
        if isinstance(models, list):
            for model in models:
                model_options.append(f"{provider}:{model}")
        elif isinstance(models, str):
            model_options.append(f"{provider}:{models}")
    
    if model_options:
        current_model = getattr(agent.llm_manager, 'current_provider', 'openai') + ":" + getattr(agent.llm_manager, 'current_model', 'gpt-3.5-turbo')
        
        if current_model not in model_options:
            current_model = model_options[0]
        
        selected_model = st.selectbox(
            "Model AI:",
            options=model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            format_func=lambda x: f"🤖 {x.split(':')[1]} ({x.split(':')[0].title()})",
            key="model_selector"
        )
        
        if selected_model != current_model:
            provider, model = selected_model.split(":", 1)
            agent.llm_manager.set_provider(provider, model)
            st.success(f"✅ Model berubah ke {model} ({provider.title()})")
        
        # Model info
        provider, model = selected_model.split(":", 1)
        context_window = get_model_context_window(model)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <div style="color: white; font-size: 0.9rem;">
                <strong>📋 Info Model:</strong><br>
                Provider: {provider.title()}<br>
                Context: {context_window:,} token<br>
                Status: <span style="color: #90EE90;">Aktif</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def get_available_models(config) -> Dict[str, List[str]]:
    """Get available models from config"""
    models = {}
    llm_providers = config.get("llm_providers", {})
    
    for provider, provider_config in llm_providers.items():
        provider_models = provider_config.get("models", [])
        if provider_models:
            models[provider] = provider_models
    
    return models

def get_model_context_window(model_name: str) -> int:
    """Get context window size for model"""
    context_windows = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
        "claude-3-haiku": 200000,
        "claude-3-sonnet": 200000,
        "claude-3-opus": 200000,
        "claude-3-5-sonnet": 200000,
        "llama2": 4096,
        "mistral": 32000,
        "codellama": 16384
    }
    
    return context_windows.get(model_name, 4096)

def render_performance_metrics(agent):
    """Render performance metrics with Indonesian styling"""
    total_sessions = len(agent.sessions) if agent.sessions else 0
    current_session_id = getattr(st.session_state, 'current_session_id', 'default')
    current_session_messages = 0
    if current_session_id in agent.sessions:
        current_session_messages = len(agent.sessions[current_session_id].get_messages())
    
    total_messages = sum(len(session.get_messages()) for session in agent.sessions.values()) if agent.sessions else 0
    
    # Indonesian-styled metrics
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Sesi</div>
        <div class="metric-value">{total_sessions}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Pesan Sesi Ini</div>
        <div class="metric-value">{current_session_messages}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Pesan</div>
        <div class="metric-value">{total_messages}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_interface(agent):
    """Render chat interface with Indonesian enhancements"""
    st.markdown("### 💬 Percakapan AI")
    
    # Initialize current session if not set
    if not hasattr(st.session_state, 'current_session_id'):
        st.session_state.current_session_id = "default"
    
    current_session_id = st.session_state.current_session_id
    
    # Ensure session exists
    if current_session_id not in agent.sessions:
        agent.create_session(current_session_id)
    
    # Display conversation history
    session = agent.sessions[current_session_id]
    messages = session.get_messages()
    
    for i, message in enumerate(messages):
        # Skip system messages in display
        if message.role == "system":
            continue
            
        role = message.role
        content = message.content
        timestamp = message.timestamp.strftime("%H:%M:%S")
        metadata = message.metadata or {}
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-header">👤 Anda</div>
                <div class="message-content">{content}</div>
                <div class="message-metadata">🕐 {timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        
        elif role == "assistant":
            # Check for RAG sources
            rag_indicator = ""
            rag_sources_count = metadata.get("rag_sources_count", 0)
            if rag_sources_count > 0:
                rag_indicator = f" 📚 ({rag_sources_count} sumber)"
            
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-header">🇮🇩 Garuda AI{rag_indicator}</div>
                <div class="message-content">{content}</div>
                <div class="message-metadata">
                    🕐 {timestamp}
                    {f" | 🔍 Model: {metadata.get('model', 'Unknown')}" if metadata.get('model') else ""}
                    {f" | 📊 Token: {metadata.get('tokens_used', 0)}" if metadata.get('tokens_used') else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display RAG sources if available (this would need to be stored separately)
            # For now, we'll skip the RAG sources display as it's not in the message metadata
    
    # Chat input
    st.markdown("---")
    
    # Input area with Indonesian styling
    user_input = st.text_area(
        "💭 Tulis pesan Anda:",
        height=100,
        placeholder="Ketik pertanyaan atau permintaan Anda di sini... (Tekan Ctrl+Enter untuk mengirim)",
        key="chat_input"
    )
    
    # Send button row
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        send_button = st.button("🚀 Kirim", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🧹 Bersihkan", use_container_width=True)
    
    # Handle send message
    if send_button and user_input.strip():
        with st.spinner("🤔 Garuda AI sedang berpikir..."):
            try:
                response_data = agent.chat(
                    message=user_input,
                    session_id=current_session_id,
                    provider="openai",  # Default provider
                    use_rag=True
                )
                if response_data.get("success"):
                    st.rerun()
                else:
                    st.error(f"❌ Terjadi kesalahan: {response_data.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {str(e)}")
    
    # Handle clear chat
    if clear_button:
        if current_session_id in agent.sessions:
            agent.sessions[current_session_id].clear()
            st.rerun()

def render_document_manager(agent):
    """Render document manager with Indonesian theme"""
    st.markdown("### 📚 Manajemen Dokumen")
    
    # Document upload with Indonesian styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFE6E6 0%, #FFFFFF 100%); padding: 1.5rem; border-radius: 12px; border: 2px dashed #FF0000; text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
        <div style="color: #FF0000; font-weight: 600; margin-bottom: 0.5rem;">Upload Dokumen</div>
        <div style="color: #6C757D; font-size: 0.9rem;">Dukung format: PDF, TXT, DOCX</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Pilih file dokumen:",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True,
        key="document_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 0, 0, 0.2); margin: 0.5rem 0;">
                    <div style="color: #FF0000; font-weight: 600;">📄 {uploaded_file.name}</div>
                    <div style="color: #6C757D; font-size: 0.9rem;">Ukuran: {uploaded_file.size:,} bytes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📤 Upload", key=f"upload_{uploaded_file.name}"):
                    with st.spinner(f"⏳ Mengupload {uploaded_file.name}..."):
                        try:
                            # Save uploaded file temporarily
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getvalue())
                            
                            # Process document
                            success = agent.vector_manager.load_document(temp_path)
                            
                            # Clean up
                            os.remove(temp_path)
                            
                            if success:
                                st.success(f"✅ {uploaded_file.name} berhasil diupload!")
                            else:
                                st.error(f"❌ Gagal mengupload {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # Document statistics
    st.markdown("### 📊 Statistik Dokumen")
    
    try:
        doc_count = agent.vector_manager.collection.count()
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Dokumen</div>
            <div class="metric-value">{doc_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if doc_count > 0:
            if st.button("🗑️ Hapus Semua Dokumen", type="secondary"):
                try:
                    agent.vector_manager.collection.delete()
                    st.success("✅ Semua dokumen berhasil dihapus!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error menghapus dokumen: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error mengakses database: {str(e)}")

def render_settings(agent, config):
    """Render settings panel with Indonesian theme"""
    st.markdown("### ⚙️ Pengaturan Sistem")
    
    # API Key Management with Indonesian styling
    st.markdown("#### 🔑 Manajemen API Key")
    
    # OpenAI API Key
    openai_key = st.text_input(
        "OpenAI API Key:",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Masukkan API key OpenAI Anda"
    )
    
    # Anthropic API Key
    anthropic_key = st.text_input(
        "Anthropic API Key:",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Masukkan API key Anthropic Anda"
    )
    
    # Save API keys
    if st.button("💾 Simpan API Keys", type="primary"):
        # Update environment variables
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        
        st.success("✅ API Keys berhasil disimpan!")
    
    st.divider()
    
    # Model Parameters
    st.markdown("#### 🎛️ Parameter Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=2.0,
            value=getattr(agent.llm_manager, 'temperature', 0.7),
            step=0.1,
            help="Kontrol kreativitas model (0=konservatif, 2=kreatif)"
        )
    
    with col2:
        max_tokens = st.slider(
            "Max Tokens:",
            min_value=100,
            max_value=4000,
            value=getattr(agent.llm_manager, 'max_tokens', 1000),
            step=100,
            help="Maksimal token dalam respons"
        )
    
    # Update parameters
    if hasattr(agent.llm_manager, 'temperature'):
        agent.llm_manager.temperature = temperature
    if hasattr(agent.llm_manager, 'max_tokens'):
        agent.llm_manager.max_tokens = max_tokens
    
    st.divider()
    
    # RAG Settings
    st.markdown("#### 🔍 Pengaturan RAG")
    
    rag_enabled = st.checkbox(
        "Aktifkan RAG (Retrieval-Augmented Generation)",
        value=getattr(agent, 'use_rag', True),
        help="Gunakan dokumen yang diupload untuk memperkaya respons"
    )
    
    if rag_enabled:
        similarity_threshold = st.slider(
            "Ambang Batas Kemiripan:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Minimum skor kemiripan untuk menggunakan dokumen"
        )
        
        max_sources = st.slider(
            "Maksimal Sumber:",
            min_value=1,
            max_value=10,
            value=5,
            help="Maksimal sumber dokumen yang digunakan"
        )
    
    agent.use_rag = rag_enabled
    
    st.divider()
    
    # System Information
    st.markdown("#### ℹ️ Informasi Sistem")
    
    st.markdown(f"""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 0, 0, 0.2);">
        <div style="color: #FF0000; font-weight: 600; margin-bottom: 1rem;">🇮🇩 Garuda AI Assistant</div>
        <div style="color: #6C757D; line-height: 1.6;">
            <strong>Versi:</strong> 1.0.0 Indonesia Edition<br>
            <strong>Provider:</strong> Multi-Provider Support<br>
            <strong>Database:</strong> ChromaDB Vector Store<br>
            <strong>Framework:</strong> Streamlit + LangChain<br>
            <strong>Tema:</strong> Indonesian Government Colors<br>
            <strong>Dukungan:</strong> Bahasa Indonesia & English
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Export/Import Settings
    st.markdown("#### 📁 Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Percakapan", use_container_width=True):
            # Export conversations to JSON
            import json
            export_data = {
                "conversations": agent.conversations,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            st.download_button(
                label="💾 Download Export",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"garuda_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_backup = st.file_uploader(
            "📥 Import Backup",
            type=['json'],
            help="Upload file backup percakapan"
        )
        
        if uploaded_backup:
            try:
                import json
                backup_data = json.loads(uploaded_backup.getvalue().decode())
                
                if "conversations" in backup_data:
                    agent.conversations.update(backup_data["conversations"])
                    st.success("✅ Backup berhasil di-restore!")
                else:
                    st.error("❌ Format backup tidak valid")
            except Exception as e:
                st.error(f"❌ Error loading backup: {str(e)}") 
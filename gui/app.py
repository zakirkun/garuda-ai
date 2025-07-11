import streamlit as st
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gui.interface import (
    render_sidebar,
    render_chat_interface,
    render_document_manager,
    render_settings,
    render_welcome_message
)
from core.agent import GarudaAIAgent
import yaml

# Indonesian Government Color Scheme CSS
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Indonesian Government Color Palette */
    :root {
        --indo-red: #FF0000;
        --indo-white: #FFFFFF;
        --indo-red-dark: #CC0000;
        --indo-red-light: #FF3333;
        --indo-red-pale: #FFE6E6;
        --text-dark: #2C3E50;
        --text-light: #6C757D;
        --shadow: rgba(255, 0, 0, 0.1);
        --border: rgba(255, 0, 0, 0.2);
    }
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, var(--indo-white) 0%, var(--indo-red-pale) 100%);
        color: var(--text-dark);
    }
    
    /* Main Container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
        background: var(--indo-white);
        border-radius: 15px;
        box-shadow: 0 10px 30px var(--shadow);
        margin: 1rem auto;
        border: 1px solid var(--border);
    }
    
    /* Header */
    h1 {
        color: var(--indo-red) !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 2rem !important;
        font-size: 2.5rem !important;
        text-shadow: 2px 2px 4px rgba(255, 0, 0, 0.1);
    }
    
    h2, h3 {
        color: var(--indo-red-dark) !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--indo-red) 0%, var(--indo-red-dark) 100%);
        border-right: 3px solid var(--indo-red);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
        padding: 1rem;
    }
    
    .sidebar h1, .sidebar h2, .sidebar h3 {
        color: var(--indo-white) !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .sidebar .stSelectbox label,
    .sidebar .stSlider label,
    .sidebar .stTextInput label,
    .sidebar .stTextArea label {
        color: var(--indo-white) !important;
        font-weight: 500 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--indo-red) 0%, var(--indo-red-dark) 100%);
        color: var(--indo-white);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.2);
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--indo-red-dark) 0%, var(--indo-red) 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button Style */
    .secondary-button {
        background: linear-gradient(135deg, var(--indo-white) 0%, var(--indo-red-pale) 100%) !important;
        color: var(--indo-red) !important;
        border: 2px solid var(--indo-red) !important;
    }
    
    .secondary-button:hover {
        background: linear-gradient(135deg, var(--indo-red-pale) 0%, var(--indo-white) 100%) !important;
        border-color: var(--indo-red-dark) !important;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid var(--indo-red);
        transition: all 0.3s ease;
        background: var(--indo-white);
    }
    
    .chat-message:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, var(--indo-red-pale) 0%, var(--indo-white) 100%);
        border-left-color: var(--indo-red);
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, var(--indo-white) 0%, #F8F9FA 100%);
        border-left-color: var(--indo-red-dark);
        margin-right: 2rem;
    }
    
    .message-header {
        font-weight: 600;
        color: var(--indo-red);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .message-content {
        color: var(--text-dark);
        line-height: 1.6;
        font-size: 1rem;
    }
    
    .message-metadata {
        font-size: 0.8rem;
        color: var(--text-light);
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--border);
        border-radius: 8px;
        padding: 0.75rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        background: var(--indo-white);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--indo-red);
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1);
        outline: none;
    }
    
    /* Select Boxes */
    .stSelectbox > div > div {
        background: var(--indo-white);
        border: 2px solid var(--border);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--indo-red-light);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: var(--indo-white);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 10px var(--shadow);
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-light);
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--indo-red) 0%, var(--indo-red-dark) 100%);
        color: var(--indo-white) !important;
        box-shadow: 0 2px 10px rgba(255, 0, 0, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--indo-red-pale);
        color: var(--indo-red);
    }
    
    /* Metrics and Cards */
    .metric-card {
        background: linear-gradient(135deg, var(--indo-white) 0%, var(--indo-red-pale) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px var(--shadow);
        border: 1px solid var(--border);
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.15);
    }
    
    .metric-title {
        color: var(--indo-red);
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-dark);
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    
    /* Status Indicators */
    .status-connected {
        color: #28A745;
        font-weight: 600;
    }
    
    .status-error {
        color: var(--indo-red);
        font-weight: 600;
    }
    
    .status-warning {
        color: #FFC107;
        font-weight: 600;
    }
    
    /* Document Upload Area */
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: var(--indo-white);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--indo-red);
        background: var(--indo-red-pale);
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background: var(--indo-red);
    }
    
    .stSlider > div > div > div > div > div {
        background: var(--indo-red);
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--indo-red) 0%, var(--indo-red-light) 100%);
    }
    
    /* Success Messages */
    .stSuccess {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        border: 1px solid #28A745;
        border-radius: 8px;
        color: #155724;
    }
    
    /* Error Messages */
    .stError {
        background: linear-gradient(135deg, var(--indo-red-pale) 0%, #FFD6D6 100%);
        border: 1px solid var(--indo-red);
        border-radius: 8px;
        color: var(--indo-red-dark);
    }
    
    /* Info Messages */
    .stInfo {
        background: linear-gradient(135deg, #D1ECF1 0%, #BEE5EB 100%);
        border: 1px solid #17A2B8;
        border-radius: 8px;
        color: #0C5460;
    }
    
    /* Warning Messages */
    .stWarning {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFEAA7 100%);
        border: 1px solid #FFC107;
        border-radius: 8px;
        color: #856404;
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
        color: var(--indo-red);
    }
    
    /* Sidebar Indonesian Flag Accent */
    .sidebar::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--indo-red) 50%, var(--indo-white) 50%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 2px solid var(--border);
        color: var(--text-light);
        font-size: 0.9rem;
    }
    
    .footer-brand {
        color: var(--indo-red);
        font-weight: 600;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
            margin: 0.5rem auto;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .user-message,
        .assistant-message {
            margin-left: 0;
            margin-right: 0;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--indo-red-pale);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--indo-red);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--indo-red-dark);
    }
    </style>
    """, unsafe_allow_html=True)

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error("❌ Config file not found. Please ensure config.yaml exists.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading config: {str(e)}")
        return None

def main():
    # Page configuration with Indonesian theme
    st.set_page_config(
        page_title="🇮🇩 Garuda AI Assistant",
        page_icon="🇮🇩",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Garuda AI Assistant - Powered by Indonesian Innovation 🇮🇩"
        }
    )
    
    # Load CSS with Indonesian colors
    load_css()
    
    # Load configuration for validation
    config = load_config()
    if not config:
        return
    
    # Initialize session state
    if 'agent' not in st.session_state:
        # Pass the file path, not the config dictionary
        st.session_state.agent = GarudaAIAgent('config.yaml')
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "💬 Chat"
    
    # App header with Indonesian branding
    st.markdown("""
    <h1>🇮🇩 Garuda AI Assistant</h1>
    <div style="text-align: center; color: #6C757D; margin-bottom: 2rem; font-style: italic;">
        Asisten AI Cerdas untuk Bangsa Indonesia
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar(st.session_state.agent, config)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Documents", "⚙️ Settings"])
    
    with tab1:
        if not st.session_state.agent.sessions:
            render_welcome_message()
        render_chat_interface(st.session_state.agent)
    
    with tab2:
        render_document_manager(st.session_state.agent)
    
    with tab3:
        render_settings(st.session_state.agent, config)
    
    # Footer with Indonesian pride
    st.markdown("""
    <div class="footer">
        <div class="footer-brand">🇮🇩 Garuda AI Assistant</div>
        <div>Membanggakan Indonesia melalui Teknologi AI</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
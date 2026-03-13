import streamlit as st

def load_custom_css():
    st.markdown("""  
    <style>
    /* Main header with seamless background integration */
    .main-header {
        background: transparent;
        padding: 0rem 1rem 0rem 2rem;
        margin-bottom: 1rem;
        text-align: center;
        border: none;
        box-shadow: none;
    }
    
    .main-header img {
        height: auto;
        max-height: 700px;
        width: auto;
        max-width: 1000px;
        display: block;
        margin: 0 auto;
        filter: brightness(1.1) contrast(1.05);
        /* Remove any potential background or border */
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transform: translateY(-70px);
    }      
         
    /* Ensure seamless transition between header and content */
    .main-content {
        background: transparent;
        border-top: none;
    }
    
    /* Remove any potential dividers or separators */
    .main-header::after,
    .main-header::before {
        display: none !important;
    }
    
    /* Sidebar sections with consistent styling */
    .sidebar-section {
        background: rgba(248, 249, 250, 0.05);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4285f4;
        backdrop-filter: blur(10px);
    }
    
    /* Upload area with subtle transparency */
    .upload-area {
        border: 2px dashed rgba(218, 220, 224, 0.3);
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: rgba(250, 251, 252, 0.02);
        margin: 1rem 0;
        backdrop-filter: blur(5px);
    }
    
    /* Enhanced workflow button */
    .workflow-button {
        background: linear-gradient(45deg, #4285f4, #34a853);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
        transition: all 0.3s ease;
    }
    
    .workflow-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
    }
    
    /* Mode selector with transparent background */
    .mode-selector {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(218, 220, 224, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Status indicators */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .active { 
        background-color: #ea4335;
        box-shadow: 0 0 8px rgba(234, 67, 53, 0.5);
    }
    .inactive { 
        background-color: rgba(218, 220, 224, 0.5);
    }
    
    /* API configuration section */
    .api-config-section {
        background: rgba(248, 249, 250, 0.05);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4285f4;
        backdrop-filter: blur(10px);
    }
    
    /* Remove any default Streamlit separators */
    .element-container div[data-testid="stHorizontalBlock"] {
        border: none !important;
    }
    
    /* Ensure consistent dark theme integration */
    .stApp {
        background-color: transparent;
    }
    
    /* Hide any potential divider lines */
    hr {
        display: none !important;
    }
    
    /* Smooth transitions for all elements */
    * {
        transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)
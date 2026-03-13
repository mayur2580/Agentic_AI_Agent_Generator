import streamlit as st
import os
import streamlit as st
import os
import sqlite3
import pandas as pd
import json
import base64
import requests
import tempfile
from app.tools.suggest_tools import suggest_enhanced_tools
from app.agents.user_skill_level import determine_user_skill_level
from app.agents.code import generate_production_code
from app.agents.subtasks import (
    classify_into_subtasks, 
    render_subtasks_for_review, 
    process_complex_subtask_modification
)
from app.agents.followup_questions import (
    render_followup_questions_with_upload,
    init_followup_db
)
from app.rag.analyse_files import analyze_file_requirements, extract_file_data
from app.agents.explain_code import explain_code
from app.agents.api_service import APIService
from app.ui.css import load_custom_css

def initialize_session_database():
    """Initialize database for session management"""
    conn = sqlite3.connect('main_sessions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            stage INTEGER,
            agent_name TEXT,
            goal TEXT,
            refined_goal TEXT,
            subtasks TEXT,
            skill_level TEXT,
            uploaded_files TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def save_session_state(session_id: str):
    """Save current session state to database"""
    conn = initialize_session_database()
    cursor = conn.cursor()
    try:
        session_data = {
            'session_id': session_id,
            'stage': st.session_state.stage,
            'agent_name': st.session_state.data.get('agent_name', ''),
            'goal': st.session_state.data.get('goal', ''),
            'refined_goal': st.session_state.data.get('refined_goal', ''),
            'subtasks': json.dumps(st.session_state.data.get('subtasks', [])),
            'skill_level': st.session_state.data.get('user_skill_level', ''),
            'uploaded_files': json.dumps(st.session_state.data.get('uploaded_files', []))
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO main_sessions
            (session_id, stage, agent_name, goal, refined_goal, subtasks, skill_level, uploaded_files)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data['stage'],
            session_data['agent_name'],
            session_data['goal'],
            session_data['refined_goal'],
            session_data['subtasks'],
            session_data['skill_level'],
            session_data['uploaded_files']
        ))
        conn.commit()
        st.success(f"✅ Session saved: {session_id}")
    except Exception as e:
        st.error(f"Error saving session: {e}")
    finally:
        conn.close()

def render_subtasks_for_review(subtasks: list, goal: str, key_prefix="subtask_review"):
    """Generalized subtask editor"""
    
    st.subheader("📋 Generated Subtasks")
    
    # Show current subtasks
    for idx, task in enumerate(subtasks):
        st.write(f"{idx+1}. {task}")

    # Buttons
    col1, col2, col3 = st.columns(3)
    
    edit_clicked = col1.button("✏️ Edit", key=f"{key_prefix}_edit", use_container_width=True)
    regen_clicked = col2.button("🔄 Regenerate", key=f"{key_prefix}_regen", use_container_width=True)
    continue_clicked = col3.button("✅ Continue", key=f"{key_prefix}_continue", use_container_width=True)

    # Initialize edit state
    edit_key = f"{key_prefix}_editing"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    # Toggle edit mode
    if edit_clicked:
        st.session_state[edit_key] = True

    # Edit form
    if st.session_state[edit_key]:
        st.markdown("---")
        
        # Show examples to help users
        with st.expander("💡 **Example Modification Requests**"):
            st.markdown("""
            **Adding tasks:**
            - "Add security review after step 2"
            - "Insert database backup before step 3"
            - "Add testing phase at the end"
            
            **Removing tasks:**
            - "Remove step 3"
            - "Delete the testing step"
            - "Remove any steps about documentation"
            
            **Modifying tasks:**
            - "Make step 1 more specific about requirements gathering"
            - "Change step 2 to focus on API design"
            - "Update deployment step to use Docker"
            
            **Reordering tasks:**
            - "Move testing to be the last step"
            - "Put database design before implementation"
            - "Swap steps 2 and 3"
            """)
        
        with st.form(f"{key_prefix}_edit_form", clear_on_submit=False):
            st.subheader("🤖 Modify Subtasks")
            
            modification_text = st.text_area(
                "What changes do you want to make?",
                placeholder=" ",
                height=100,
                key=f"{key_prefix}_input"
            )
            
            col_apply, col_cancel = st.columns([1, 1])
            
            with col_apply:
                apply_clicked = st.form_submit_button("🚀 Apply Changes", type="primary")
            
            with col_cancel:
                cancel_clicked = st.form_submit_button("❌ Cancel")
            
            # Handle form submission
            if apply_clicked:
                if modification_text and modification_text.strip():
                    st.write("**🔄 Processing your request...**")
                    
                    # Process the modification
                    updated_tasks = process_complex_subtask_modification(subtasks, modification_text)
                    
                    # Check if tasks actually changed
                    if updated_tasks != subtasks:
                        st.session_state[edit_key] = False
                        st.balloons()
                        return {"action": "save", "subtasks": updated_tasks}
                    else:
                        st.error("❌ **NO CHANGES APPLIED** - see debug info above")
                else:
                    st.error("Please enter what you want to change")
            
            if cancel_clicked:
                st.session_state[edit_key] = False
                st.rerun()

    # Handle other buttons
    if regen_clicked:
        st.session_state[edit_key] = False
        return {"action": "regen"}
    elif continue_clicked:
        st.session_state[edit_key] = False
        return {"action": "continue"}
        
    return None

def render_api_design_section():
    """Render API design configuration section"""
    st.subheader("🔌 API Design Configuration")
    
    # Initialize API service if not exists
    if 'api_service' not in st.session_state:
        st.session_state.api_service = APIService()
    
    # API Configuration Section
    with st.expander("⚙️ Configure API Endpoints", expanded=True):
        api_name = st.text_input("API Name", placeholder="e.g., user_api, payment_api")
        base_url = st.text_input("Base URL", placeholder="https://api.example.com")
        api_key = st.text_input("API Key (optional)", type="password", placeholder="Bearer token or API key")
        
        # Additional headers
        st.markdown("**Additional Headers:**")
        headers_json = st.text_area(
            "Headers (JSON format)",
            placeholder='{"Content-Type": "application/json", "Custom-Header": "value"}',
            height=100
        )
        
        if st.button("Add API Configuration"):
            if api_name and base_url:
                try:
                    headers = json.loads(headers_json) if headers_json else {}
                    config = {
                        'base_url': base_url,
                        'api_key': api_key if api_key else None,
                        'headers': headers
                    }
                    st.session_state.api_service.add_api_config(api_name, config)
                    st.success(f"✅ API configuration added for {api_name}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in headers")
            else:
                st.error("Please provide API name and base URL")
    
    # Display configured APIs
    if st.session_state.api_service.api_configs:
        st.markdown("**Configured APIs:**")
        for api_name, config in st.session_state.api_service.api_configs.items():
            with st.expander(f"📡 {api_name}"):
                st.write(f"**Base URL:** {config['base_url']}")
                st.write(f"**Has API Key:** {'Yes' if config.get('api_key') else 'No'}")
                if config.get('headers'):
                    st.write("**Headers:**")
                    st.json(config['headers'])
    
    # API Testing Section
    with st.expander("🧪 Test API Endpoints"):
        if st.session_state.api_service.api_configs:
            selected_api = st.selectbox(
                "Select API to test",
                options=list(st.session_state.api_service.api_configs.keys())
            )
            
            endpoint = st.text_input("Endpoint", placeholder="/users, /products, etc.")
            method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
            
            if method in ["POST", "PUT", "PATCH"]:
                request_data = st.text_area(
                    "Request Data (JSON)",
                    placeholder='{"key": "value"}',
                    height=100
                )
            else:
                request_params = st.text_area(
                    "Query Parameters (JSON)",
                    placeholder='{"param1": "value1", "param2": "value2"}',
                    height=100
                )
            
            if st.button("🚀 Test API Call"):
                try:
                    data = None
                    params = None
                    
                    if method in ["POST", "PUT", "PATCH"] and request_data:
                        data = json.loads(request_data)
                    elif method == "GET" and request_params:
                        params = json.loads(request_params)
                    
                    # This would be an async call in real implementation
                    with st.spinner("Making API request..."):
                        st.info("API testing functionality would execute here")
                        # result = await st.session_state.api_service.make_request(
                        #     selected_api, endpoint, method, data, params
                        # )
                        st.success("✅ API test completed (mock response)")
                        
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in request data/parameters")
                except Exception as e:
                    st.error(f"API test failed: {str(e)}")
        else:
            st.info("No APIs configured. Add an API configuration above to test endpoints.")
    
    # Generate API Documentation
    with st.expander("📚 Generate API Documentation"):
        if st.button("Generate Documentation"):
            if st.session_state.api_service.api_configs:
                doc_content = "# API Documentation\n\n"
                
                for api_name, config in st.session_state.api_service.api_configs.items():
                    doc_content += f"## {api_name}\n\n"
                    doc_content += f"**Base URL:** `{config['base_url']}`\n\n"
                    
                    if config.get('api_key'):
                        doc_content += "**Authentication:** Bearer Token required\n\n"
                    
                    if config.get('headers'):
                        doc_content += "**Default Headers:**\n```json\n"
                        doc_content += json.dumps(config['headers'], indent=2)
                        doc_content += "\n```\n\n"
                    
                    doc_content += "**Available Endpoints:**\n"
                    doc_content += "- GET /endpoint - Description\n"
                    doc_content += "- POST /endpoint - Description\n"
                    doc_content += "- PUT /endpoint/{id} - Description\n"
                    doc_content += "- DELETE /endpoint/{id} - Description\n\n"
                
                st.markdown(doc_content)
                
                # Download button for documentation
                st.download_button(
                    label="📥 Download Documentation",
                    data=doc_content,
                    file_name="api_documentation.md",
                    mime="text/markdown"
                )
            else:
                st.info("No APIs configured to document.")

def render_sidebar():
    """Render the modern sidebar interface"""
    with st.sidebar:
        # Quick Start Section
        
        st.markdown("### 📁 Upload Files/Folder")
        # st.markdown("**Choose files to analyze**")
        uploader_key = st.session_state.get("uploader_key", 0)

        uploaded_files = st.file_uploader(
            "Choose files/Folder",
            accept_multiple_files=True,
            type=['csv', 'txt', 'json', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'pdf', 'py','md','yml','zip','src','xlsx'],
            key=f"uploader_{uploader_key}",   # 👈 dynamic key
            help="Limit 200MB per file • CSV, TXT, JSON, DOCX, JPG, JPEG, PNG, GIF"
        )

        # Store uploaded files in session state for use in tabs
        if uploaded_files:
            # Store the uploaded files and their analysis in session state
            if 'uploaded_files_data' not in st.session_state:
                st.session_state.uploaded_files_data = []
            
            # Update session state with current uploaded files
            st.session_state.uploaded_files_data = uploaded_files
            
            # Show basic file info in sidebar
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            for file in uploaded_files:
                st.write(f"• {file.name}")
        
        # Clear uploaded files if none selected
        elif 'uploaded_files_data' in st.session_state:
            st.session_state.uploaded_files_data = []
            
        st.markdown('</div>', unsafe_allow_html=True)
        
      
        if st.button("🗑️ Clear Workflow"):
            st.session_state.clear()     # wipe everything
            st.session_state["uploader_key"] = uploader_key + 1   # 👈 force new uploader
            st.rerun()


# def render_main_header():
#         """Render main header with AAxxon AI logo"""
#         logo_path = "Media.png"
        
#         if os.path.exists(logo_path):
#             try:
#                 with open(logo_path, "rb") as f:
#                     logo_data = base64.b64encode(f.read()).decode()
                
#                 st.markdown(f"""
#                 <div class="main-header">
#                     <img src="data:image/jpeg;base64,{logo_data}" 
#                         style="height: 200px; width: auto;">
#                 </div>
#                 """, unsafe_allow_html=True)
                
#             except Exception as e:
#                 st.error(f"Error loading logo: {e}")             
                    
#         else:
#             st.error("ailogo.png not found")
            
def main():
    # Set page config
    st.set_page_config(
        page_title="Agentic AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # render_main_header()
    # Render logo in top-right corner
    # render_fixed_logo()
    
    # Initialize database
    init_followup_db()
    
    # Session state initialization
    if 'stage' not in st.session_state:
        st.session_state.stage = 1
        st.session_state.data = {}
        st.session_state.session_id = f"session_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.mode = 'workflow'
    
    # Render sidebar
    render_sidebar()
    
    
    if st.session_state.stage == 1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 🎯 Define Your Objective")
        st.markdown("**What would you like to accomplish?**")
        
        goal = st.text_area(
            "",
            placeholder="Ask Anything",
            height=180,
            help="Press Ctrl+Enter to apply"
        )
        
        if st.button("🚀 Generate Subtasks", key="start_workflow"):
            if goal.strip():
                st.session_state.data.update({
                    'domain': "AI Assistant",
                    'goal': goal.strip()
                })
                
                with st.spinner("🔍 Analyzing your objective..."):
                    skill_analysis = determine_user_skill_level(goal.strip())
                    st.session_state.data['user_skill_level'] = skill_analysis['skill_level']
                    st.session_state.data['skill_reason'] = skill_analysis['reason']
                
                with st.spinner("⚡ Generating subtasks from your objective..."):
                    try:
                        subtasks = classify_into_subtasks(goal.strip())
                        if not subtasks:
                            st.error("Failed to generate subtasks. Please try again.")
                            return
                        st.session_state.data['subtasks'] = subtasks
                        st.success(f"✅ Generated {len(subtasks)} subtasks!")
                    except Exception as e:
                        st.error(f"Error generating subtasks: {e}")
                        return
                
                st.session_state.stage = 2
                st.rerun()
            else:
                st.error("Please describe what you'd like to accomplish")
        
        # st.info("💡 Start by describing your project objective")
        # st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == 2:
        # st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.header("📋 Generated Subtasks")
        
        if 'user_skill_level' in st.session_state.data:
            skill_level = st.session_state.data['user_skill_level'].upper()
            st.success(f"🔍 **Detected Skill Level:** {skill_level}")
        
        # Show original objective
        # Get current subtasks
        subtasks = st.session_state.data.get('subtasks', [])
        goal = st.session_state.data.get('goal', '')
        
        # Use the render_subtasks_for_review function
        result = render_subtasks_for_review(subtasks, goal, "stage2")
            
        # Handle button actions
        if result:
            if result["action"] == "save":
                st.session_state.data['subtasks'] = result["subtasks"]
                # if 'original_subtasks' not in st.session_state.data:
                    # st.session_state.data['original_subtasks'] = subtasks.copy()
                st.success("🎉 Subtasks have been updated!")
                # st.rerun()
                st.write("**Updated Subtasks:**")
                for i, task in enumerate(result["subtasks"], 1):
                    st.write(f"{i}. {task}")
                st.rerun()
            
            # Force rerun to show changes
            
                
            elif result["action"] == "regen":
                with st.spinner("🔄 Regenerating subtasks..."):
                    try:
                        goal = st.session_state.data.get('goal', '')
                        subtasks = classify_into_subtasks(goal)
                        st.session_state.data['subtasks'] = subtasks
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating subtasks: {e}")
            
            elif result["action"] == "continue":
                # Move to follow-up questions stage
                st.session_state.stage = 3
                st.rerun()
        
        # Back button
        if st.button("🔙 Back to Objective"):
            st.session_state.stage = 1
            st.rerun()
        
        st.info("💡 Edit your subtasks or click Continue to proceed")
        st.markdown('</div>', unsafe_allow_html=True)

    
    elif st.session_state.stage == 3:
        # Follow-up Questions Section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Follow-up Questions")
        
        result = render_followup_questions_with_upload(
            objective=st.session_state.data.get('goal', ''),
            skill_level=st.session_state.data.get('user_skill_level', 'intermediate'),
            session_id=st.session_state.session_id
        )
        
        if result:
            st.session_state.data.update({
                'refined_goal': result['refined_objective'],
                'followup_answers': result['answers'],
                'followup_questions': result['questions'], 
                'uploaded_files': result.get('uploaded_files', []),
                'question_specific_files': result.get('question_specific_files', []),
                'database_configs': result.get('database_configs', [])
            
            })

            
            st.session_state.stage = 4
            st.rerun()
        
        
    elif st.session_state.stage == 4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 WorkFlow")

        # Initialize states if not exists
        if 'current_analysis_tab' not in st.session_state:
            st.session_state.current_analysis_tab = 0
        if 'generated_code' not in st.session_state:
            st.session_state.generated_code = None
        if 'code_explanation' not in st.session_state:
            st.session_state.code_explanation = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'tool_suggestions' not in st.session_state:
            st.session_state.tool_suggestions = None

        # Create tabs for different analyses
        tabs = st.tabs([
            "🎯 Objective Analysis",
           # "👤 User Skill Level",
            "📋 Subtasks Analysis", 
            "❓ Follow-up Analysis",
            "📁 File Analysis",
            "🔧 Tool Suggestions",
            # "🤔 Reasoning",
            "🔌 API Design",
            "💻 Generated Code",
            "📖 Code Explanation"
        ])

        # Objective Analysis Tab
        with tabs[0]:
            st.subheader("🎯 Project Objective")
            st.markdown("**Original Objective:**")
            st.info(st.session_state.data.get('goal', ''))
            if st.session_state.data.get('refined_goal'):
                st.markdown("**Refined Objective:**")
                st.success(st.session_state.data.get('refined_goal', ''))

        # User Skill Level Tab
        # with tabs[1]:
        #     st.subheader("👤 User Skill Level Analysis")
        #     skill_level = st.session_state.data.get('user_skill_level', 'intermediate').upper()
        #     st.success(f"**Detected Skill Level:** {skill_level}")
        #     if 'skill_reason' in st.session_state.data:
        #         with st.expander("View Analysis"):
        #             st.write(st.session_state.data['skill_reason'])

        # Subtasks Analysis Tab
        with tabs[1]:
            st.subheader("📋 Subtask Breakdown")
            subtasks = st.session_state.data.get('subtasks', [])
            for i, subtask in enumerate(subtasks, 1):
                with st.expander(f"Subtask {i}"):
                    st.markdown(f"**Task:** {subtask}")
                    st.markdown("**Dependencies:**")
                    if i > 1:
                        st.markdown(f"- Depends on Subtask {i-1}")

        with tabs[2]:
            st.subheader("❓ Requirements Analysis")
            questions = st.session_state.data.get('followup_questions', [])
            answers = st.session_state.data.get('followup_answers', {})

            if questions:
                for i, q in enumerate(questions):
                    with st.expander(f"Q{i+1}: {q}"):
                        ans = answers.get(i, "No answer provided.")
                        st.write(f"**Answer:** {ans}")

        with tabs[3]:
            st.subheader("📁 File Analysis")
            
            # Check if files are uploaded via sidebar
            uploaded_files = st.session_state.get('uploaded_files_data', [])
            
            if uploaded_files:
                # Analyze files and show results
                st.markdown("**📤 Uploaded Files:**")
                
                # Display file analysis results
                file_analysis_results = analyze_file_requirements(
                    answers=st.session_state.data.get('followup_answers', {}), 
                    uploaded_files=uploaded_files
                )
                
                # Store analysis results in session state
                st.session_state.data['file_analysis_results'] = file_analysis_results
                
                # Display each uploaded file with its analysis
                for i, file in enumerate(uploaded_files):
                    with st.expander(f"📄 {file.name}", expanded=False):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.write(f"**Type:** {file.type}")
                            st.write(f"**Size:** {file.size} bytes")
                        
                        with col2:
                            # Show file analysis results
                            st.write("**Analysis:**")
                            if file_analysis_results:
                                for j, result in enumerate(file_analysis_results):
                                    if j < len(uploaded_files):  # Match results to files
                                        st.info(f"• {result}")
                            
                            # Enhanced file preview based on file type
                            file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
                            
                            try:
                                if file.type.startswith('text/') or file_extension in ['txt', 'csv', 'py', 'js', 'html', 'css', 'md', 'yml', 'yaml', 'xml']:
                                    # Text-based files
                                    content = file.read()
                                    if isinstance(content, bytes):
                                        content = content.decode('utf-8')
                                    
                                    st.write("**Content Preview:**")
                                    st.text_area(
                                        f"Preview of {file.name}",
                                        content[:1000] + ("..." if len(content) > 1000 else ""),
                                        height=200,
                                        disabled=True
                                    )
                                    
                                    # Show file statistics
                                    lines = content.count('\n') + 1
                                    words = len(content.split())
                                    chars = len(content)
                                    st.caption(f"📊 {lines} lines • {words} words • {chars} characters")
                                    
                                elif file.type.startswith('image/') or file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                                    # Image files
                                    st.write("**Image Preview:**")
                                    st.image(file, caption=f"Preview of {file.name}", width=400)
                                    
                                elif file_extension == 'json':
                                    # JSON files
                                    content = file.read()
                                    if isinstance(content, bytes):
                                        content = content.decode('utf-8')
                                    
                                    try:
                                        json_data = json.loads(content)
                                        st.write("**JSON Content Preview:**")
                                        st.json(json_data)
                                        
                                        # JSON statistics
                                        if isinstance(json_data, dict):
                                            st.caption(f"📊 {len(json_data)} top-level keys")
                                        elif isinstance(json_data, list):
                                            st.caption(f"📊 {len(json_data)} items in array")
                                    except json.JSONDecodeError:
                                        st.warning("Invalid JSON format")
                                        st.text_area("Raw content:", content[:500], disabled=True)
                                
                                elif file_extension == 'pdf':
                                    # PDF files
                                    st.write("**PDF Content Preview:**")
                                    
                                    try:
                                        import PyPDF2
                                        import io
                                        
                                        # Reset file pointer
                                        file.seek(0)
                                        
                                        # Create a PDF reader object
                                        pdf_bytes = file.read()
                                        pdf_file = io.BytesIO(pdf_bytes)
                                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                                        
                                        # Get PDF info
                                        num_pages = len(pdf_reader.pages)
                                        st.caption(f"📊 PDF Document • {num_pages} pages • {len(pdf_bytes)} bytes")
                                        
                                        # Extract text from first few pages
                                        extracted_text = ""
                                        max_pages_to_preview = min(3, num_pages)  # Preview first 3 pages
                                        
                                        for page_num in range(max_pages_to_preview):
                                            page = pdf_reader.pages[page_num]
                                            page_text = page.extract_text()
                                            if page_text.strip():
                                                extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                                        
                                        if extracted_text.strip():
                                            # Show extracted text
                                            preview_text = extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else "")
                                            st.text_area(
                                                f"Text Content (First {max_pages_to_preview} pages)",
                                                preview_text,
                                                height=300,
                                                disabled=True
                                            )
                                            
                                            # Text statistics
                                            words = len(extracted_text.split())
                                            chars = len(extracted_text)
                                            st.caption(f"🔤 Extracted: {words} words • {chars} characters")
                                        else:
                                            st.warning("📄 PDF appears to contain images or non-extractable text")
                                            st.info("This might be a scanned PDF or contain only images/graphics")
                                    
                                    except ImportError:
                                        # Fallback: Try alternative PDF libraries
                                        try:
                                            import fitz  # PyMuPDF
                                            
                                            file.seek(0)
                                            pdf_bytes = file.read()
                                            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                                            
                                            num_pages = pdf_document.page_count
                                            st.caption(f"📊 PDF Document • {num_pages} pages • {len(pdf_bytes)} bytes")
                                            
                                            # Extract text from first few pages
                                            extracted_text = ""
                                            max_pages_to_preview = min(3, num_pages)
                                            
                                            for page_num in range(max_pages_to_preview):
                                                page = pdf_document[page_num]
                                                page_text = page.get_text()
                                                if page_text.strip():
                                                    extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                                            
                                            pdf_document.close()
                                            
                                            if extracted_text.strip():
                                                preview_text = extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else "")
                                                st.text_area(
                                                    f"Text Content (First {max_pages_to_preview} pages)",
                                                    preview_text,
                                                    height=300,
                                                    disabled=True
                                                )
                                                
                                                words = len(extracted_text.split())
                                                chars = len(extracted_text)
                                                st.caption(f"🔤 Extracted: {words} words • {chars} characters")
                                            else:
                                                st.warning("📄 PDF appears to contain images or non-extractable text")
                                        
                                        except ImportError:
                                            # Final fallback - show installation instructions
                                            st.error("📄 PDF preview requires additional libraries")
                                            with st.expander("🔧 Installation Instructions"):
                                                st.code("""
# Install PDF processing libraries:
pip install PyPDF2
# OR
pip install PyMuPDF
                                                """)
                                            st.info("PDF detected but cannot preview content without PDF processing libraries")
                                            st.caption(f"File size: {file.size} bytes")
                                    
                                    except Exception as e:
                                        st.error(f"Error processing PDF: {str(e)}")
                                        st.info("📄 PDF file detected but preview failed")
                                        st.caption(f"File size: {file.size} bytes")
                                
                                elif file_extension in ['docx', 'doc']:
                                    # Word documents
                                    st.write("**Word Document Detected:**")
                                    st.info("📝 Word document processing available")
                                    st.caption("Use document processing libraries to extract content")
                                
                                elif file_extension in ['xlsx', 'xls']:
                                    # Excel files
                                    st.write("**Excel File Detected:**")
                                    st.info("📊 Excel spreadsheet processing available")
                                    st.caption("Use pandas or openpyxl to process spreadsheet data")
                                
                                elif file_extension in ['zip', 'rar', '7z']:
                                    # Archive files
                                    st.write("**Archive File Detected:**")
                                    st.info("🗜️ Compressed archive file")
                                    st.caption("Extract contents for individual file analysis")
                                
                                else:
                                    # Unknown file types
                                    st.write("**File Information:**")
                                    st.info(f"📎 {file_extension.upper()} file type detected")
                                    
                                    # Try to read first few bytes for binary analysis
                                    file_bytes = file.read(100)
                                    if file_bytes:
                                        hex_preview = ' '.join([f'{b:02x}' for b in file_bytes[:20]])
                                        st.caption(f"🔍 Binary preview (first 20 bytes): {hex_preview}")
                                    
                                    # Check if it might be text
                                    try:
                                        file.seek(0)
                                        sample = file.read(500)
                                        if isinstance(sample, bytes):
                                            decoded = sample.decode('utf-8')
                                            if all(ord(c) < 128 for c in decoded):  # ASCII check
                                                st.text_area("Possible text content:", decoded, disabled=True, height=100)
                                    except:
                                        pass
                                
                                # Reset file pointer for other operations
                                file.seek(0)
                                
                            except Exception as e:
                                st.error(f"Error previewing file: {str(e)}")
                                st.caption("File might be corrupted or in an unsupported format")
                
                # Overall file analysis summary
                if file_analysis_results:
                    st.markdown("**📋 File Analysis Summary:**")
                    for result in file_analysis_results:
                        st.success(f"✓ {result}")
                
            else:
                st.info("No files uploaded. Use the file uploader in the sidebar to upload files for analysis.")
                
            # Also show any previously stored file analysis from followup questions
            if not st.session_state.data.get('file_analysis') and st.session_state.data.get('followup_answers'):
                with st.spinner("Analyzing file requirements from answers..."):
                    file_analysis = analyze_file_requirements(
                        st.session_state.data.get('followup_answers', {})
                    )
                    st.session_state.data['file_analysis'] = file_analysis

        with tabs[4]:
            st.subheader("🔧 Tool Suggestions")
            
            # Check if we have the necessary data to generate tool suggestions
            subtasks = st.session_state.data.get('subtasks', [])
            followup_answers = st.session_state.data.get('followup_answers', {})
            
            if subtasks and followup_answers:
                # Initialize tool suggestions in session state if not exists
                if 'tool_suggestions' not in st.session_state:
                    st.session_state.tool_suggestions = {}
                
                # Generate button to trigger tool analysis
                if st.button("🚀 Generate Tool Recommendations", type="primary"):
                    st.session_state.tool_suggestions = {}  # Reset previous suggestions
                    
                    with st.spinner("Analyzing your requirements and suggesting appropriate tools..."):
                        # Combine all followup answers into a single string for context
                        combined_answers = " | ".join([
                            f"Q{i+1}: {answer}" for i, answer in followup_answers.items()
                        ])
                        
                        # Generate tool suggestions for each subtask
                        for idx, subtask in enumerate(subtasks):
                            try:
                                suggestion = suggest_enhanced_tools(
                                    subtask=subtask,
                                    answers=combined_answers,
                                    subtask_index=idx
                                )
                                st.session_state.tool_suggestions[f"subtask_{idx}"] = {
                                    'subtask': subtask,
                                    'suggestions': suggestion
                                }
                            except Exception as e:
                                st.error(f"Error generating suggestions for subtask {idx+1}: {e}")
                    
                    st.success("✅ Tool recommendations generated!")
                
                # Display generated tool suggestions
                if st.session_state.tool_suggestions:
                    st.markdown("### 📋 Recommended Tools by Subtask")
                    
                    for key, data in st.session_state.tool_suggestions.items():
                        subtask_num = key.split('_')[1]
                        with st.expander(f"🔨 Subtask {int(subtask_num) + 1}: {data['subtask']}", expanded=False):
                            st.markdown(data['suggestions'])
                    
                    # Additional tool categories from tools.md
                    with st.expander("🌐 Additional Online Tools Available", expanded=False):
                        st.markdown("""
                        ### 📚 Research & Documentation
                        - **Wikipedia** - General information lookup
                        - **Google Scholar** - Academic paper search
                        - **ArXiv** - ML/AI/Math research papers
                        
                        ### 💻 Developer Resources  
                        - **Stack Overflow** - Programming Q&A
                        - **GitHub** - Open-source code repositories
                        - **PyPI** - Python package discovery
                        - **Hugging Face Hub** - Pre-trained ML models
                        
                        ### 🤖 AI-Powered Tools
                        - **Perplexity AI** - AI web search with citations
                        - **Tavily Search** - Fast AI-augmented search
                        - **ChatGPT Browse** - GPT web browsing
                        
                        ### 🛠️ Productivity Tools
                        - **Zapier** - Workflow automation (5000+ app integrations)
                        - **Notion AI** - Knowledge management
                        - **IFTTT** - Simple task automation
                        """)
                    
                    # Export tool recommendations
                    col1, col2 = st.columns(2)
                    with col1:
                        # Prepare export data
                        export_data = {
                            'objective': st.session_state.data.get('goal', ''),
                            'refined_objective': st.session_state.data.get('refined_goal', ''),
                            'subtasks': subtasks,
                            'tool_recommendations': st.session_state.tool_suggestions,
                            'generated_at': pd.Timestamp.now().isoformat()
                        }
                        
                        st.download_button(
                            label="📥 Download Tool Recommendations",
                            data=json.dumps(export_data, indent=2),
                            file_name=f"tool_recommendations_{st.session_state.session_id}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Create a markdown summary for easy reading
                        markdown_content = f"""# Tool Recommendations Report
                        
## Project Objective
{st.session_state.data.get('goal', '')}

## Refined Objective  
{st.session_state.data.get('refined_goal', '')}

## Tool Suggestions by Subtask

"""
                        for key, data in st.session_state.tool_suggestions.items():
                            subtask_num = key.split('_')[1]
                            markdown_content += f"""
### Subtask {int(subtask_num) + 1}: {data['subtask']}

{data['suggestions']}

---
"""
                        
                        st.download_button(
                            label="📄 Download as Markdown",
                            data=markdown_content,
                            file_name=f"tool_recommendations_{st.session_state.session_id}.md",
                            mime="text/markdown"
                        )
                
                else:
                    st.info("💡 Click 'Generate Tool Recommendations' to analyze your requirements and get personalized tool suggestions for each subtask.")
            
            elif not subtasks:
                st.warning("⚠️ No subtasks found. Please complete the subtask generation step first.")
            
            elif not followup_answers:
                st.warning("⚠️ No follow-up answers found. Please complete the requirements gathering step first.")
            
            else:
                st.info("📝 Complete the previous steps to generate tool recommendations based on your specific requirements.")
            
        # API Design Tab
        with tabs[5]:
            render_api_design_section()

        # Generated Code Tab
        with tabs[6]:
            st.subheader("💻 Generated Implementation")
            if not st.session_state.generated_code:
                with st.spinner("⚡ Generating production code..."):
                    enhanced_data = st.session_state.data.copy()
                    if st.session_state.data.get('uploaded_files'):
                        enhanced_data['file_integration_required'] = True
                        enhanced_data['database_required'] = True
                        enhanced_data['file_types'] = [f['file_type'] for f in st.session_state.data['uploaded_files']]
                    st.session_state.generated_code = generate_production_code(enhanced_data)

            if st.session_state.generated_code:
                st.code(st.session_state.generated_code, language='python')
                col1, col2,col3 = st.columns(3)
                with col2:
                    st.download_button(
                        label="📥 Download Code",
                        data=st.session_state.generated_code,
                        file_name=f"{st.session_state.data.get('agent_name', 'multi_agent')}_enhanced.py",
                        mime="text/python",
                        type="secondary",
                        width="stretch",
                    )
                with col1:
                    session_export = {
                        'session_id': st.session_state.session_id,
                        'data': st.session_state.data,
                        'generated_code': st.session_state.generated_code
                    }
                    st.download_button(
                        label="📊 Export Session",
                        data=json.dumps(session_export, indent=2),
                        file_name=f"enhanced_session_{st.session_state.session_id}.json",
                        mime="application/json",
                        type="secondary",
                        width="stretch"
                    )
               
                with col3:
                        with st.expander("🚀 Deployment Tool", expanded=False, width="stretch"):
                            st.subheader("Deployment Tool 🚀")

                            # Choose service type
                            service_type = st.selectbox(
                                "Select Service Type",
                                ["python", "fastapi", "npm"]
                            )

                            # Optional repo name
                            repo_name = st.text_input("Repo Name (leave blank for new repo)")

                            # Upload ZIP file
                            uploaded_file = st.file_uploader("Upload your ZIP folder", type=["zip"])

                            if st.button(label="Deploy", type="primary", use_container_width=True):
                                if uploaded_file is None:
                                    st.error("Please upload a ZIP file before deploying.")
                                else:
                                    # Save uploaded file temporarily
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                                        tmp_file.write(uploaded_file.read())
                                        temp_path = tmp_file.name

                                    st.info(f"Deploying {uploaded_file.name}")

                                    url = "http://training.alignedautomation.com:3000/aa_bot/Single_api/api/deployments/auto-workflow"
                                    
                                    # adjust host/port
                                    try:
                                        with open(temp_path, "rb") as f:
                                            files = {"zip_file": f}
                                            params = {
                                                "service_type": service_type,
                                                "repo_name": "auto-repo-82dd66cb",
                                                "branch_name": "test5",
                                                "commit_message": "Add code from Streamlit uploader"
                                            }

                                            response = requests.post(url, files=files, params=params)
                                            print(response.status_code)
                                            print(response)

                                        if response.status_code == 200:
                                            st.success("Deployment successful! ✅")
                                            st.json(response.json())
                                        else:
                                            st.error(f"Deployment failed ({response.status_code}): {response.text}")

                                    except Exception as e:
                                        st.error(f"Error: {e}")
                                    finally:
                                        if os.path.exists(temp_path):
                                            os.remove(temp_path)

        # Code Explanation Tab
        with tabs[7]:
            st.subheader("📖 Code Documentation & Explanation")
            if not st.session_state.code_explanation and st.session_state.generated_code:
                with st.spinner("Generating documentation..."):
                    st.session_state.code_explanation = explain_code(st.session_state.data)

            if st.session_state.code_explanation:
                explanation_sections = [
                    ("🎯 Overview", "overview"),
                    ("🏗️ Architecture", "architecture"),
                    ("📦 Dependencies", "dependencies"),
                    ("⚙️ Core Components", "components"),
                    ("🔄 Workflow", "workflow"),
                    ("🚀 Usage Examples", "examples")
                ]
                for section_title, section_key in explanation_sections:
                    with st.expander(section_title):
                        st.write(st.session_state.code_explanation.get(section_key, "Section content loading..."))

        # Reset button
        with st.container():
            if st.button("🔄 Generate New System", type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import re
from app.utils.constants import llm_invoke

def process_complex_subtask_modification(current_tasks: list, user_request: str) -> list:
    """Enhanced conversational subtask modification"""
    
    # Enhanced conversational prompt for LLM
    prompt = f"""You are an intelligent assistant responsible for modifying a list of subtasks based on user instructions.

The user may express their wishes in natural language, in various forms.

Possible commands include adding, removing, editing, or reordering subtasks.

Examples of natural requests:
- "Add a new step: Implement security audit after step 3"
- "Remove step 2"
- "Please change step 1 to focus on data validation"  
- "Insert a new subtask between steps 4 and 5: Conduct code review"
- "I want to include streamlit visualization at the end"
- "Can you add data testing before the final step?"
- "Delete the last step"
your task : if the user ask to add the step , then always Read the user's input, understand their intent ,add the step in existing subtasks and return the updated list by adding the step in existing subtasks
your task : if the user ask to remove the step , then always Read the user's input, understand their intent remove the step in existing subtasks and return the updated list by removing the step in existing subtasks
your task : if the user ask to modify the step , then always Read the user's input, understand their intent modify the step in existing subtasks and return the updated list by modifying the step in existing subtasks
Your task: Read the user's input, understand their intent, and return ONLY the updated numbered list of subtasks.

Current subtasks:
{chr(10).join([f"{i+1}. {task}" for i, task in enumerate(current_tasks)])}

User request: {user_request}

Return only the updated numbered subtask list:"""

    try:
        response = llm_invoke(prompt, max_tokens=500, temperature=0.6)
        
        # Parse the response to extract subtasks
        updated_tasks = []
        for line in response.split('\n'):
            line = line.strip()
            if re.match(r'^\d+\.\s', line):
                task = re.sub(r'^\d+\.\s*', '', line).strip()
                if task:
                    updated_tasks.append(task)

        if updated_tasks and len(updated_tasks) > 0:
            if "remove" in user_request.lower():
                if len(updated_tasks) < len(current_tasks):
                    st.success(f"✅ Removed tasks: {len(current_tasks)} → {len(updated_tasks)} tasks")
                    return updated_tasks
                else:
                    st.warning("Remove operation didn't reduce task count")
                    return current_tasks
            else:
                # For other operations, allow same or different count
                if updated_tasks != current_tasks:
                    st.success(f"✅ Updated subtasks based on your request!")
                    return updated_tasks
                else:
                    st.warning("No changes detected in the updated list")
                    return current_tasks
        else:
            st.error("Could not parse updated tasks from LLM response")
            return current_tasks
            
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
        return current_tasks
   


def render_subtasks_for_review(subtasks: list, goal: str, key_prefix="subtask_review"):
    """Simple working subtask editor"""
    
    st.subheader("🔍 Generated Subtasks")
    for idx, task in enumerate(subtasks):
        st.write(f"{idx+1}. {task}")

    # Three buttons
    col1, col2, col3 = st.columns(3)
    
    edit_clicked = col1.button("✏️ Edit", key=f"{key_prefix}_edit", use_container_width=True)
    # regen_clicked = col2.button("🔄 Regenerate", key=f"{key_prefix}_regen", use_container_width=True)
    continue_clicked = col3.button("✅ Continue", key=f"{key_prefix}_continue", use_container_width=True)

    edit_key = f"{key_prefix}_editing"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False
    # Edit mode
    if edit_clicked:
        st.session_state[edit_key] = True

    # Edit form
    if st.session_state[edit_key]:
        st.markdown("---")
        
        with st.form(f"{key_prefix}_edit_form", clear_on_submit=False):
            st.subheader("🤖 Modify Subtasks")
            
            modification_text = st.text_area(
                "What changes do you want?",
                placeholder="Examples:\n- Remove step 3\n- Add security check after step 2\n- Make step 1 more specific",
                height=100,
                key=f"{key_prefix}_input"
            
            )
            
            col_submit, col_cancel = st.columns([1, 1])
            with process_complex_subtask_modification:
                apply_clicked = st.form_submit_button("🚀 Apply Changes", type="primary")
            
            with col_cancel:
                cancel_clicked = st.form_submit_button("❌ Cancel")
            
            # Handle form submission
            if apply_clicked:
                if modification_text and modification_text.strip():
                    st.write("**🔄 Processing your request...**")
                    updated_tasks = process_complex_subtask_modification(subtasks, modification_text)
                    
                    # Check if tasks actually changed
                    if updated_tasks != subtasks:
                        st.session_state[edit_key] = False
                        st.balloons()
                        return {"action": "save", "subtasks": updated_tasks}
                    else:
                        st.error("❌ **NO CHANGES APPLIED**")
                else:
                    st.error("Please enter what you want to change")
            
            if cancel_clicked:
                st.session_state[edit_key] = False
                st.rerun()
    
        
    return None  
def classify_into_subtasks(objective: str) -> list:
    """Generate initial subtasks based on user objective"""
    
    uploaded_files = st.session_state.get('uploaded_files', [])
    file_context = ""
    
    if uploaded_files:
        file_info = []
        for file_data in uploaded_files:
            file_info.append(f"- {file_data.name}: {file_data.read().decode()[:300]}...")
        file_context = f"\n\nUPLOADED FILES CONTEXT:\n" + "\n".join(file_info)

    # KEY CHANGE: More dynamic prompt
    prompt = f"""You are an expert project manager. Analyze this objective and break it down into the appropriate number of actionable subtasks.

PROJECT OBJECTIVE: {objective}

{file_context}

INSTRUCTIONS:
- Generate ONLY the necessary subtasks (minimum 3, maximum 10)
- Simple objectives should have fewer subtasks (3-5)
- Complex objectives can have more subtasks (6-10)
- Each subtask should be specific and implementable
- Use clear, technical language appropriate for the domain
- Focus on concrete development/implementation steps
- Maintain logical sequence and dependencies

Think about the complexity: Is this a simple task that needs 3-5 steps, or a complex project requiring 8-10 steps?

Return ONLY the numbered list of subtasks:"""

    try:
        # Reduce max_tokens to encourage shorter responses
        response = llm_invoke(prompt, max_tokens=600, temperature=0.3)  # Reduced from 800
        
        if not response or len(response.strip()) < 10:
            st.error("❌ LLM returned empty or very short response!")
            return _get_domain_specific_fallback(objective)

        # Parse numbered list
        tasks = []
        for line in response.split('\n'):
            line = line.strip()
            if line and re.match(r'^\d+\.\s', line):
                task = re.sub(r'^\d+\.\s*', '', line).strip()
                if task and len(task) > 10:
                    tasks.append(task)

        # Accept all valid tasks from LLM (no forced slicing)
        if len(tasks) >= 3 and len(tasks) <= 10:
            st.success(f"✅ Generated {len(tasks)} custom subtasks")
            return tasks
        elif len(tasks) > 10:
            st.warning(f"⚠️ LLM generated {len(tasks)} tasks, limiting to 10")
            return tasks[:10]
        else:
            st.warning("⚠️ LLM generated too few tasks, using fallback")
            return _get_domain_specific_fallback(objective)
            
    except Exception as e:
        st.error(f"❌ Error generating subtasks: {e}")
        return _get_domain_specific_fallback(objective)
          

def _get_domain_specific_fallback(objective: str) -> list:
    """Generate domain-specific fallback subtasks with dynamic count"""
    obj_lower = objective.lower()
    
    # Simple objectives (3-5 tasks)
    simple_keywords = ['hello world', 'calculator', 'todo list', 'simple', 'basic']
    is_simple = any(keyword in obj_lower for keyword in simple_keywords)
    
    if any(term in obj_lower for term in ['invoice', 'payment', 'financial', 'revenue', 'vendor']):
        if is_simple:
            return [
                "Analyze invoice data requirements",
                "Design basic invoice processing system",
                "Implement core invoice features",
                "Test and validate invoice processing"
            ]
        else:
            return [
                "Analyze invoice processing requirements and data sources",
                "Design database schema for vendors, payments, and products",
                "Implement data validation and input processing logic",
                "Create invoice parsing and data extraction components",
                "Build automated matching and reconciliation features",
                "Develop reporting dashboard and analytics features",
                "Add user authentication and access control",
                "Deploy system with monitoring and backup procedures"
            ]
    
    elif any(term in obj_lower for term in ['ai', 'ml', 'agent', 'model']):
        if is_simple:
            return [
                "Define AI requirements and data sources",
                "Implement basic AI functionality",
                "Create simple user interface",
                "Test and deploy AI system"
            ]
        else:
            return [
                "Define AI/ML requirements and success metrics",
                "Analyze and prepare training/testing datasets",
                "Design system architecture and agent workflow",
                "Implement core AI/ML processing logic",
                "Create model training and validation pipeline", 
                "Build user interface and interaction layer",
                "Add monitoring and performance tracking",
                "Deploy, test and optimize the system"
            ]
    
    else:
        if is_simple:
            return [
                "Analyze basic requirements",
                "Implement core functionality",
                "Test and validate system"
            ]
        else:
            return [
                "Analyze project requirements and define scope",
                "Design system architecture and data flow",
                "Implement core functionality and features",
                "Add data validation and error handling",
                "Create user interface and experience layer",
                "Deploy and optimize the system"
            ]

"""
Auto-generated agent script with Streamlit interface
Agent: MultiAgent
Goal: You are an intelligent document validation assistant. I have uploaded three files: purchase_order.pdf, grn.pdf, and invoice.pdf.
Your tasks:

	1.	Automatically extract key fields from each PDF:
	•	Purchase Order (PO): Item name, quantity, unit price, total price.
	•	Goods Received Note (GRN): Item name, quantity received, condition.
	•	Invoice: Item name, quantity, unit price, subtotal, tax, total amount.

	2.	Validate the files:
	•	PO details match the invoice (item, quantity, unit price).
	•	GRN matches the quantity and items in the PO and invoice.

	3.	Final Response:
	•	If all fields match perfectly, respond:
"Files matched perfectly. Now you can proceed to payment."
	•	If any mismatch exists, clearly list each mismatched field with suggested corrections.
Requirements:
	•	Keep the process error-free, simple, and systematic.
	•	Use plain English, easy to understand.
	•	Assume PDFs are formatted consistently.
"""
 
from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, END
from together import Together
import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import tempfile
 
def get_together_client():
    return Together(api_key="your_api_key_here")
 
client = get_together_client()
 
def llm_invoke(prompt: str, max_tokens: int = 1024) -> str:
    try:
        resp = client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.2
        )
        return resp.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"
       
class AgentState(TypedDict):
    user_input: Optional[str]
    follow_up_answers: Optional[dict]
    validation_messages: Optional[List[str]]
    error_occurred: Optional[bool]
    files: Optional[dict]
    step_1_result: Optional[Any]
    step_2_result: Optional[Any]
    step_3_result: Optional[Any]
    step_4_result: Optional[Any]
 
def agent_step_1(state: AgentState) -> AgentState:
    """Handles: Analyze invoice data requirements"""
    messages = state.get("validation_messages", [])
    try:
        input_data = state.get("user_input", "")
        files = state.get("files", {})
        prompt = f"""
        Subtask: Analyze invoice data requirements
        Overall Goal: You are an intelligent document validation assistant. I have uploaded three files: purchase_order.pdf, grn.pdf, and invoice.pdf.
Your tasks:

	1.	Automatically extract key fields from each PDF:
	•	Purchase Order (PO): Item name, quantity, unit price, total price.
	•	Goods Received Note (GRN): Item name, quantity received, condition.
	•	Invoice: Item name, quantity, unit price, subtotal, tax, total amount.

	2.	Validate the files:
	•	PO details match the invoice (item, quantity, unit price).
	•	GRN matches the quantity and items in the PO and invoice.

	3.	Final Response:
	•	If all fields match perfectly, respond:
"Files matched perfectly. Now you can proceed to payment."
	•	If any mismatch exists, clearly list each mismatched field with suggested corrections.
Requirements:
	•	Keep the process error-free, simple, and systematic.
	•	Use plain English, easy to understand.
	•	Assume PDFs are formatted consistently.
        Step 1/4
        Input: {input_data}
        Files Available: {list(files.keys())}
        Requirements: {state.get("follow_up_answers", {}).get("Analyze invoice data requirements", "No specific requirements")}
        """
        result = llm_invoke(prompt)
        messages.append("✅ Step 1 done: Analyze invoice data requirements")
        return {**state, "step_1_result": result, "validation_messages": messages}
    except Exception as e:
        messages.append(f"❌ Error in step 1: {e}")
        return {**state, "error_occurred": True, "validation_messages": messages}

def agent_step_2(state: AgentState) -> AgentState:
    """Handles: Design basic invoice processing system"""
    messages = state.get("validation_messages", [])
    try:
        input_data = state.get("step_1_result", "")
        files = state.get("files", {})
        prompt = f"""
        Subtask: Design basic invoice processing system
        Overall Goal: You are an intelligent document validation assistant. I have uploaded three files: purchase_order.pdf, grn.pdf, and invoice.pdf.
Your tasks:

	1.	Automatically extract key fields from each PDF:
	•	Purchase Order (PO): Item name, quantity, unit price, total price.
	•	Goods Received Note (GRN): Item name, quantity received, condition.
	•	Invoice: Item name, quantity, unit price, subtotal, tax, total amount.

	2.	Validate the files:
	•	PO details match the invoice (item, quantity, unit price).
	•	GRN matches the quantity and items in the PO and invoice.

	3.	Final Response:
	•	If all fields match perfectly, respond:
"Files matched perfectly. Now you can proceed to payment."
	•	If any mismatch exists, clearly list each mismatched field with suggested corrections.
Requirements:
	•	Keep the process error-free, simple, and systematic.
	•	Use plain English, easy to understand.
	•	Assume PDFs are formatted consistently.
        Step 2/4
        Input: {input_data}
        Files Available: {list(files.keys())}
        Requirements: {state.get("follow_up_answers", {}).get("Design basic invoice processing system", "No specific requirements")}
        """
        result = llm_invoke(prompt)
        messages.append("✅ Step 2 done: Design basic invoice processing system")
        return {**state, "step_2_result": result, "validation_messages": messages}
    except Exception as e:
        messages.append(f"❌ Error in step 2: {e}")
        return {**state, "error_occurred": True, "validation_messages": messages}

def agent_step_3(state: AgentState) -> AgentState:
    """Handles: Implement core invoice features"""
    messages = state.get("validation_messages", [])
    try:
        input_data = state.get("step_2_result", "")
        files = state.get("files", {})
        prompt = f"""
        Subtask: Implement core invoice features
        Overall Goal: You are an intelligent document validation assistant. I have uploaded three files: purchase_order.pdf, grn.pdf, and invoice.pdf.
Your tasks:

	1.	Automatically extract key fields from each PDF:
	•	Purchase Order (PO): Item name, quantity, unit price, total price.
	•	Goods Received Note (GRN): Item name, quantity received, condition.
	•	Invoice: Item name, quantity, unit price, subtotal, tax, total amount.

	2.	Validate the files:
	•	PO details match the invoice (item, quantity, unit price).
	•	GRN matches the quantity and items in the PO and invoice.

	3.	Final Response:
	•	If all fields match perfectly, respond:
"Files matched perfectly. Now you can proceed to payment."
	•	If any mismatch exists, clearly list each mismatched field with suggested corrections.
Requirements:
	•	Keep the process error-free, simple, and systematic.
	•	Use plain English, easy to understand.
	•	Assume PDFs are formatted consistently.
        Step 3/4
        Input: {input_data}
        Files Available: {list(files.keys())}
        Requirements: {state.get("follow_up_answers", {}).get("Implement core invoice features", "No specific requirements")}
        """
        result = llm_invoke(prompt)
        messages.append("✅ Step 3 done: Implement core invoice features")
        return {**state, "step_3_result": result, "validation_messages": messages}
    except Exception as e:
        messages.append(f"❌ Error in step 3: {e}")
        return {**state, "error_occurred": True, "validation_messages": messages}

def agent_step_4(state: AgentState) -> AgentState:
    """Handles: Test and validate invoice processing"""
    messages = state.get("validation_messages", [])
    try:
        input_data = state.get("step_3_result", "")
        files = state.get("files", {})
        prompt = f"""
        Subtask: Test and validate invoice processing
        Overall Goal: You are an intelligent document validation assistant. I have uploaded three files: purchase_order.pdf, grn.pdf, and invoice.pdf.
Your tasks:

	1.	Automatically extract key fields from each PDF:
	•	Purchase Order (PO): Item name, quantity, unit price, total price.
	•	Goods Received Note (GRN): Item name, quantity received, condition.
	•	Invoice: Item name, quantity, unit price, subtotal, tax, total amount.

	2.	Validate the files:
	•	PO details match the invoice (item, quantity, unit price).
	•	GRN matches the quantity and items in the PO and invoice.

	3.	Final Response:
	•	If all fields match perfectly, respond:
"Files matched perfectly. Now you can proceed to payment."
	•	If any mismatch exists, clearly list each mismatched field with suggested corrections.
Requirements:
	•	Keep the process error-free, simple, and systematic.
	•	Use plain English, easy to understand.
	•	Assume PDFs are formatted consistently.
        Step 4/4
        Input: {input_data}
        Files Available: {list(files.keys())}
        Requirements: {state.get("follow_up_answers", {}).get("Test and validate invoice processing", "No specific requirements")}
        """
        result = llm_invoke(prompt)
        messages.append("✅ Step 4 done: Test and validate invoice processing")
        return {**state, "step_4_result": result, "validation_messages": messages}
    except Exception as e:
        messages.append(f"❌ Error in step 4: {e}")
        return {**state, "error_occurred": True, "validation_messages": messages}

 
# File Agent
def file_agent(state: AgentState) -> AgentState:
    messages = state.get("validation_messages", [])
    files = {}
 
    uploaded_files = []
    if state.get("user_input"):
        uploaded_files.extend([tok for tok in state["user_input"].split() if "." in tok])
    if state.get("follow_up_answers"):
        for ans in state["follow_up_answers"].values():
            if isinstance(ans, str):
                uploaded_files.extend([tok for tok in ans.split() if "." in tok])
 
    for file_path in uploaded_files:
        ext = os.path.splitext(file_path)[-1].lower()
        var_name = os.path.basename(file_path).replace(".", "_").replace(" ", "_").lower()
        try:
            if ext == ".csv":
                files[var_name] = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                files[var_name] = pd.read_excel(file_path)
            elif ext in [".sqlite", ".db"]:
                conn = sqlite3.connect(file_path)
                files[var_name] = conn
            elif ext == ".sql":
                with open(file_path, "r") as f:
                    sql_script = f.read()
                conn = sqlite3.connect(":memory:")
                conn.executescript(sql_script)
                files[var_name] = conn
            elif ext == ".json":
                with open(file_path, "r") as f:
                    files[var_name] = json.load(f)
            elif ext in [".txt", ".md"]:
                with open(file_path, "r") as f:
                    files[var_name] = f.read()
            else:
                files[var_name] = None
            messages.append(f"📂 Loaded file: {file_path}")
        except Exception as e:
            messages.append(f"❌ Error loading {file_path}: {e}")
 
    return {**state, "files": files, "validation_messages": messages}
 
def create_workflow():
    wf = StateGraph(AgentState)
    wf.add_node("file_agent", file_agent)
    wf.add_node("step_1", agent_step_1)
    wf.add_node("step_2", agent_step_2)
    wf.add_node("step_3", agent_step_3)
    wf.add_node("step_4", agent_step_4)
    wf.set_entry_point("file_agent")
    wf.add_edge("file_agent", "step_1")
    wf.add_edge("step_1", "step_2")
    wf.add_edge("step_2", "step_3")
    wf.add_edge("step_3", "step_4")
    wf.add_edge("step_4", END)
    return wf.compile()


# Streamlit Interface
def main():
    st.set_page_config(
        page_title="Document Validation Assistant",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Document Validation Assistant")
    st.markdown("Upload your Purchase Order, GRN, and Invoice files to validate and cross-check the documents.")
    
    # Sidebar for file uploads
    st.sidebar.header("📁 File Upload")
    
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'csv', 'xlsx', 'xls', 'json', 'txt', 'md'],
        help="Upload Purchase Order, GRN, and Invoice files"
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 User Input")
        user_input = st.text_area(
            "Enter additional information or instructions:",
            placeholder="Enter any specific requirements or notes...",
            height=100
        )
        
        # Follow-up questions section
        st.subheader("❓ Follow-up Questions")
        follow_up_answers = {}
        
        questions = [
            "Analyze invoice data requirements",
            "Design basic invoice processing system", 
            "Implement core invoice features",
            "Test and validate invoice processing"
        ]
        
        for question in questions:
            answer = st.text_input(f"{question}:", key=question)
            if answer:
                follow_up_answers[question] = answer
    
    with col2:
        st.subheader("📊 Process Status")
        status_placeholder = st.empty()
        
        st.subheader("📋 Uploaded Files")
        if uploaded_files:
            for file in uploaded_files:
                st.write(f"✅ {file.name}")
        else:
            st.write("No files uploaded yet")
    
    # Process button
    if st.button("🚀 Start Validation Process", type="primary"):
        if uploaded_files:
            # Create temporary directory for uploaded files
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            # Save uploaded files to temporary directory
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
            
            # Update user input with file paths
            files_string = " ".join(file_paths)
            combined_input = f"{user_input} {files_string}".strip()
            
            # Initialize state
            state = AgentState(
                user_input=combined_input,
                follow_up_answers=follow_up_answers,
                validation_messages=[],
                error_occurred=False,
                files={}, 
                step_1_result=None, 
                step_2_result=None, 
                step_3_result=None, 
                step_4_result=None
            )
            
            # Create and run workflow
            with st.spinner("Processing documents..."):
                try:
                    wf = create_workflow()
                    result = wf.invoke(state)
                    
                    # Display results
                    st.success("✅ Workflow Completed!")
                    
                    # Validation messages
                    st.subheader("📋 Process Messages")
                    for msg in result.get("validation_messages", []):
                        if "✅" in msg:
                            st.success(msg)
                        elif "❌" in msg:
                            st.error(msg)
                        else:
                            st.info(msg)
                    
                    # Step results
                    st.subheader("📊 Step Results")
                    for i in range(4):
                        with st.expander(f"Step {i+1} Result"):
                            step_result = result.get(f"step_{i+1}_result")
                            if step_result:
                                st.write(step_result)
                            else:
                                st.write("No result available")
                    
                    # Error handling
                    if result.get("error_occurred"):
                        st.error("⚠️ Some errors occurred during processing. Please check the messages above.")
                    
                except Exception as e:
                    st.error(f"❌ Error running workflow: {str(e)}")
                    
            # Clean up temporary files
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
                
        else:
            st.warning("⚠️ Please upload at least one file to start the validation process.")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Instructions")
    st.markdown("""
    1. **Upload Files**: Use the sidebar to upload your Purchase Order (PO), Goods Received Note (GRN), and Invoice files
    2. **Add Input**: Enter any additional information or specific requirements
    3. **Answer Questions**: Fill in the follow-up questions if needed
    4. **Start Process**: Click the 'Start Validation Process' button to begin
    5. **Review Results**: Check the validation results and any identified mismatches
    
    **Supported File Types**: PDF, CSV, Excel, JSON, Text files
    """)


# Original command line interface (preserved)
def run_command_line():
    state = AgentState(
        user_input="<<< PUT USER INPUT HERE >>>",
        follow_up_answers={},
        validation_messages=[],
        error_occurred=False,
        files={}, step_1_result=None, step_2_result=None, step_3_result=None, step_4_result=None
    )
    wf = create_workflow()
    result = wf.invoke(state)
    print("\n=== Workflow Finished ===")
    for msg in result.get("validation_messages", []):
        print(msg)
    for i in range(4):
        print(f"Step {i+1} result:", result.get(f"step_{i+1}_result"))


if __name__ == "__main__":
    # Check if running with streamlit
    try:
        # This will only work if running with streamlit
        main()
    except:
        # Fallback to command line interface
        run_command_line()
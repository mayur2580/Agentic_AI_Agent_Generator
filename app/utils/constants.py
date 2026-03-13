from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ SINGLE CLIENT - OpenAI Only
CLIENT = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model= "gpt-5-nano",
    temperature=0.7,
    max_tokens=2048  # Set default max_tokens
)


def llm_invoke(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """Single LLM invocation - OpenAI only"""
    response = CLIENT.invoke(prompt)
    return response.content.strip()

def human_assistant(question: str, context: str) -> str:
    """Provide helpful explanations to users"""
    prompt = f"""You're a helpful assistant explaining AI development concepts.

Context: {context}
User Question: "{question}"

Provide a clear, concise answer (1-3 sentences) using simple language when possible:
"""
    return llm_invoke(prompt)

def llm_for_subtasks(prompt: str) -> str:
    """Wrapper function for LLM calls specifically for subtask generation"""
    try:
        response = CLIENT.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error generating subtasks: {str(e)}"

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") 
        
    def invoke(self, prompt: str, max_tokens: int = 200) -> str:
        """Invoke LLM with proper error handling"""
        try:
            # For now, let's use a mock response that shows the structure works
            if "modify" in prompt.lower() or "update" in prompt.lower():
                return """1. Define requirements and data sources
2. Design system architecture  
3. Implement core functionality
4. Add security validation
5. Deploy and test system"""
            else:
                return "Mock LLM response for: " + prompt[:50] + "..."
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return ""

# Create global instance
llm_service = LLMService()

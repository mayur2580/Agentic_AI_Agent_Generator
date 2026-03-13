# 📦 Available Tools
 
Below are the tools that can be used by the LangGraph agent for task automation. These include both **online tools** and **custom internal tools**, organized by **domain**.
 
---
 
## 🌐 Online Tools (Suggested to User)
 
### 🔍 General Research
 
* **[Wikipedia](https://www.wikipedia.org)**
 
  * Use Case: General information lookup
  * Strengths: Authoritative, community-verified content
* **[Google Search](https://www.google.com)**
 
  * Use Case: General-purpose search
  * Strengths: Broadest reach across all domains
 
### 📚 Academic & Technical
 
* **[Arxiv](https://arxiv.org)**
 
  * Use Case: Academic paper search (ML/AI/Math/CS)
  * Strengths: Preprints and peer-reviewed papers
* **[Google Scholar](https://scholar.google.com)**
 
  * Use Case: Search for scholarly literature
  * Strengths: Authoritative sources, citation support
* **[DocsGPT](https://www.docsgpt.com)**
 
  * Use Case: Search technical documentation using AI
  * Strengths: Fast context-aware doc answering
* **[Semantic Scholar](https://www.semanticscholar.org)**
 
  * Use Case: AI-powered academic search engine
  * Strengths: Citation graph and paper recommendations
 
### 💻 Developer Tools
 
* **[Stack Overflow](https://stackoverflow.com)**
 
  * Use Case: Find solutions to programming issues
  * Strengths: Community-driven Q\&A, code examples
* **[PyPI](https://pypi.org)**
 
  * Use Case: Discover Python packages
  * Strengths: Official package repository with docs and versions
* **[Hugging Face Hub](https://huggingface.co/models)**
 
  * Use Case: Explore open-source ML models
  * Strengths: Easy to find pre-trained models and datasets
* **[GitHub](https://github.com)**
 
  * Use Case: Explore open-source codebases
  * Strengths: Real-world code, collaboration history
* **[Codeium](https://codeium.com)**
 
  * Use Case: Free AI code assistant
  * Strengths: IDE autocomplete, context-aware completions
 
### 🛠 Productivity / Utilities
 
* **[Notion AI](https://www.notion.so/product/ai)**
 
  * Use Case: Knowledge base, content generation, notes
  * Strengths: Well integrated with Notion workspace
* **[Zapier](https://zapier.com)**
 
  * Use Case: Automate workflows between web apps
  * Strengths: Connects 5000+ tools, drag & drop interface
* **[IFTTT](https://ifttt.com)**
 
  * Use Case: Automate personal app workflows
  * Strengths: Lightweight task automation
 
### 🚀 AI-Powered Web Search
 
* **[Tavily Search](https://www.tavily.com)**
 
  * Use Case: Fast and AI-augmented web search
  * Strengths: Summarizes top pages; useful for real-time queries
* **[Perplexity AI](https://www.perplexity.ai)**
 
  * Use Case: AI-powered web search and Q\&A
  * Strengths: Cited sources, real-time search
* **[You.com](https://you.com)**
 
  * Use Case: AI assistant for web tasks
  * Strengths: Search + AI apps like coding, writing, charts
* **[ChatGPT Browse](https://chat.openai.com)**
 
  * Use Case: GPT-based web browsing and summarizing
  * Strengths: Deep search summaries with LLM intelligence
 
---
 
## 🔧 Custom Tools (Built Into the Agent)
 
### 🤖 AI Utility
 
* `web_search_tool(query: str)`
 
  * Use Case: User wants web-based information
  * Strengths: Uses LLM to generate summarized search results
* `deep_think_tool(thought: str)`
 
  * Use Case: Brainstorming, logic building, evaluating ideas
  * Strengths: Analytical response from LLM
* `summarize_text_tool(text: str)`
 
  * Use Case: Summarize long content
  * Strengths: Short, clear explanation via LLM
* `question_generator_tool(text: str)`
 
  * Use Case: Generate follow-up questions
  * Strengths: Useful for goal clarification or interviews
* `outline_tool(topic: str)`
 
  * Use Case: Generate structured outline from topic
  * Strengths: Helps in planning or writing
* `tool_selector_tool(task: str)`
 
  * Use Case: Suggest best tool(s) from tools.md for a task
  * Strengths: Automates the recommendation process
 
### 🧠 Developer Help
 
* `explain_code_tool(code: str)`
 
  * Use Case: Understand Python snippets or algorithms
  * Strengths: Step-by-step breakdown of logic
* `generate_code_tool(prompt: str)`
 
  * Use Case: Generate code for apps, automation, utilities
  * Strengths: Fast code prototyping with LLM
* `refactor_code_tool(code: str)`
 
  * Use Case: Clean up or refactor existing code
  * Strengths: Improves readability and performance
* `generate_testcases_tool(code: str)`
 
  * Use Case: Create unit tests from code
  * Strengths: Saves manual test writing effort
* `lint_code_tool(code: str)`
 
  * Use Case: Run linting checks and fix style errors
  * Strengths: Ensures PEP8 and code consistency
 
### 📊 Data Science Helpers
 
* `csv_parser_tool(file: str)`
 
  * Use Case: Parse and summarize uploaded CSV
  * Strengths: Enables tabular insights
* `chart_suggester_tool(data: str)`
 
  * Use Case: Suggest charts from structured data
  * Strengths: Accelerates dashboard design
* `feature_engineering_tool(data: str)`
 
  * Use Case: Generate features for ML models
  * Strengths: Preprocess and enrich datasets
 
---
 
## 🧭 Tool Assignment Strategy
 
* Agent first attempts **automated tool mapping** based on subtask
* If no matching tool is found:
 
  * It suggests **online alternatives** via the UI (see list above)
  * Tool suggestion message is still shown without throwing errors
 
---
 
### 📝 Additions
 
You can extend this list by appending new tools in either section based on use case. This file can be parsed by agents in the future to reason about tool usage more intelligently.
 
Wikipedia
Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and hosted by the Wikimedia Foundation.
 
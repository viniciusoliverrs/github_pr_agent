import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

class AgentBase:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

    def _load_prompt(self, section_name):
        with open("prompts.md", "r") as f:
            content = f.read()
        
        # Simple parsing of the markdown file to get sections
        # This assumes the structure defined in prompts.md
        try:
            start = content.index(f"## {section_name}")
            # Find next header or end of file
            rest = content[start:]
            # Skip the header line
            lines = rest.split('\n')[1:]
            
            prompt_text = ""
            for line in lines:
                if line.startswith("## "):
                    break
                prompt_text += line + "\n"
            return prompt_text.strip()
        except ValueError:
            return f"Error: Could not find section {section_name} in prompts.md"

class PlannerAgent(AgentBase):
    def plan_review(self, diff_content, language="pt-BR", max_tokens=2000):
        system_prompt = self._load_prompt("Planner Prompt")
        
        messages = [
            SystemMessage(content=f"{system_prompt}\n\nPlease output in {language}."),
            HumanMessage(content=f"Here is the PR Diff:\n\n{diff_content}")
        ]
        
        chain = self.llm.bind(max_output_tokens=max_tokens) | StrOutputParser()
        return chain.invoke(messages)

class ExecutorAgent(AgentBase):
    def execute_review(self, diff_content, plan, language="pt-BR", max_tokens=2000):
        system_prompt = self._load_prompt("Executor Prompt")
        
        messages = [
            SystemMessage(content=f"{system_prompt}\n\nPlease output in {language}."),
            HumanMessage(content=f"Here is the Plan:\n{plan}\n\nHere is the PR Diff:\n{diff_content}")
        ]
        
        chain = self.llm.bind(max_output_tokens=max_tokens) | StrOutputParser()
        return chain.invoke(messages)

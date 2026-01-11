"""
Resume Parser Agent for BenchCraft AI
Extracts structured data from uploaded resumes using Gemini LLM and PDF tools
"""
from .base_agent import BaseAgent
from tools.pdf_parser import PDFParserTool
from tools.embeddings import GeminiEmbeddingTool

class ResumeParserAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Resume Parser",
            goal="Extract structured employee data from resumes",
            backstory="An expert in parsing resumes and extracting key information for onboarding.",
            tools=[PDFParserTool(), GeminiEmbeddingTool()]
        )

    def parse_resume(self, pdf_path):
        # Use PDFParserTool to extract text
        text = self.agent.tools[0].parse(pdf_path)
        # Use GeminiEmbeddingTool or LLM to extract structured fields
        structured_data = self.agent.tools[1].extract_fields(text)
        return structured_data

"""
PDF Parser Tool for BenchCraft AI
Extracts text from PDF files using PyPDF2
"""
import PyPDF2

class PDFParserTool:
    def parse(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

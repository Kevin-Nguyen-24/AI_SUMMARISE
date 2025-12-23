"""
Text extraction from different file formats
"""
import re
from pathlib import Path
from typing import Optional
import PyPDF2
from docx import Document
import pandas as pd
from openpyxl import load_workbook


class TextExtractor:
    """Extract text from PDF, DOCX, and TXT files"""
    
    @staticmethod
    def extract_from_pdf(file_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If extraction fails
        """
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            if not text:
                raise ValueError("No text could be extracted from PDF")
            
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: Path) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If extraction fails
        """
        try:
            doc = Document(file_path)
            text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            
            if not text:
                raise ValueError("No text could be extracted from DOCX")
            
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_from_excel(file_path: Path) -> str:
        """
        Extract text from Excel file (XLSX or XLS)
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Extracted text from all sheets
            
        Raises:
            Exception: If extraction fails
        """
        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path, engine='openpyxl' if str(file_path).endswith('.xlsx') else None)
            text_parts = []
            
            for sheet_name in excel_file.sheet_names:
                # Read the sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Add sheet name as header
                text_parts.append(f"\n=== Sheet: {sheet_name} ===")
                
                # Convert DataFrame to string representation
                # Remove NaN values and format nicely
                df_filled = df.fillna('')
                
                # Get column headers
                headers = ' | '.join(str(col) for col in df_filled.columns)
                text_parts.append(headers)
                text_parts.append('-' * len(headers))
                
                # Get row data
                for idx, row in df_filled.iterrows():
                    row_text = ' | '.join(str(val) for val in row.values if str(val).strip())
                    if row_text.strip():
                        text_parts.append(row_text)
                
                text_parts.append("")  # Empty line between sheets
            
            if not text_parts or len(text_parts) <= 1:
                raise ValueError("No data could be extracted from Excel file")
            
            return "\n".join(text_parts)
        except Exception as e:
            raise Exception(f"Failed to extract text from Excel: {str(e)}")
    
    @staticmethod
    def extract_from_txt(file_path: Path) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If extraction fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise ValueError("File is empty")
            
            return text
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return text
            except Exception as e:
                raise Exception(f"Failed to read text file: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize extracted text by removing excessive whitespace
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def extract(self, file_path: Path, file_type: str) -> str:
        """
        Extract and normalize text based on file type
        
        Args:
            file_path: Path to file
            file_type: File extension (pdf, docx, txt)
            
        Returns:
            Extracted and normalized text
            
        Raises:
            ValueError: If file type is unsupported
            Exception: If extraction fails
        """
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            text = self.extract_from_pdf(file_path)
        elif file_type == 'docx':
            text = self.extract_from_docx(file_path)
        elif file_type == 'txt':
            text = self.extract_from_txt(file_path)
        elif file_type in ['xlsx', 'xls']:
            text = self.extract_from_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return self.normalize_text(text)

"""
Summarization API endpoint
"""
import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from app.utils.validators import validate_file, get_file_extension
from app.services.file_service import FileService
from app.services.text_extractor import TextExtractor
from app.services.summarizer import Summarizer


logger = logging.getLogger(__name__)
router = APIRouter()


# Response models
class SummaryResponse(BaseModel):
    """Response model for successful summarization"""
    file_name: str
    file_type: str
    summary_short: List[str]
    summary_detailed: str
    model: str
    processing_time_sec: float


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str


# Service instances
file_service = FileService()
text_extractor = TextExtractor()
summarizer = Summarizer()


@router.post("/summarize", response_model=SummaryResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def summarize_document(file: UploadFile = File(...)):
    """
    Summarize uploaded document
    
    Args:
        file: Uploaded file (PDF, DOCX, or TXT)
        
    Returns:
        Summary response with bullet points and detailed summary
        
    Raises:
        HTTPException: On validation or processing errors
    """
    start_time = time.time()
    file_path = None
    
    try:
        # Step 1: Validate file
        is_valid, error_msg = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Processing file: {file.filename}")
        
        # Step 2: Save uploaded file
        file_path = await file_service.save_upload(file)
        file_type = get_file_extension(file.filename)
        
        # Step 3: Extract text
        logger.info("Extracting text from file")
        try:
            text = text_extractor.extract(file_path, file_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Insufficient text content in document")
        
        logger.info(f"Extracted {len(text)} characters")
        
        # Step 4: Summarize
        try:
            bullet_points, detailed_summary = summarizer.summarize(text)
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
        
        # Step 5: Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        logger.info(f"Successfully processed {file.filename} in {processing_time}s")
        
        # Step 6: Return response
        return SummaryResponse(
            file_name=file.filename,
            file_type=file_type,
            summary_short=bullet_points,
            summary_detailed=detailed_summary,
            model=summarizer.ollama.model,
            processing_time_sec=processing_time
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
    finally:
        # Cleanup: Delete temporary file
        if file_path:
            file_service.delete_file(file_path)

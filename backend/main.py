from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from database import get_db, create_tables, Analysis
from llm_service import LLMService

create_tables()

app = FastAPI(title="LLM Knowledge Extractor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()

class TextInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    id: int
    original_text: str
    summary: str
    title: Optional[str]
    topics: List[str]
    sentiment: str
    keywords: List[str]
    created_at: str

@app.get("/")
async def root():
    return {"message": "LLM Knowledge Extractor API", "status": "running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(text_input: TextInput, db: Session = Depends(get_db)):
    """Process new text and store analysis"""
    try:
        if not text_input.text.strip():
            raise HTTPException(status_code=400, detail="Empty input text")
        
        analysis_result = await llm_service.analyze_text(text_input.text)
        
        db_analysis = Analysis(
            original_text=text_input.text,
            summary=analysis_result["summary"],
            title=analysis_result.get("title"),
            topics=json.dumps(analysis_result["topics"]),
            sentiment=analysis_result["sentiment"],
            keywords=json.dumps(analysis_result["keywords"])
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return AnalysisResponse(
            id=db_analysis.id,
            original_text=db_analysis.original_text,
            summary=db_analysis.summary,
            title=db_analysis.title,
            topics=json.loads(db_analysis.topics),
            sentiment=db_analysis.sentiment,
            keywords=json.loads(db_analysis.keywords),
            created_at=db_analysis.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/search", response_model=List[AnalysisResponse])
async def search_analyses(topic: Optional[str] = None, keyword: Optional[str] = None, db: Session = Depends(get_db)):
    """Search stored analyses by topic or keyword"""
    query = db.query(Analysis)
    
    if topic:
        query = query.filter(Analysis.topics.contains(topic.lower()))
    
    if keyword:
        query = query.filter(Analysis.keywords.contains(keyword.lower()))
    
    analyses = query.order_by(Analysis.created_at.desc()).limit(50).all()
    
    return [
        AnalysisResponse(
            id=analysis.id,
            original_text=analysis.original_text,
            summary=analysis.summary,
            title=analysis.title,
            topics=json.loads(analysis.topics),
            sentiment=analysis.sentiment,
            keywords=json.loads(analysis.keywords),
            created_at=analysis.created_at.isoformat()
        )
        for analysis in analyses
    ]

@app.get("/analyses", response_model=List[AnalysisResponse])
async def get_all_analyses(db: Session = Depends(get_db)):
    """Get all stored analyses"""
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(50).all()
    
    return [
        AnalysisResponse(
            id=analysis.id,
            original_text=analysis.original_text,
            summary=analysis.summary,
            title=analysis.title,
            topics=json.loads(analysis.topics),
            sentiment=analysis.sentiment,
            keywords=json.loads(analysis.keywords),
            created_at=analysis.created_at.isoformat()
        )
        for analysis in analyses
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

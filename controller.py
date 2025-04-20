from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import main
import json
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI(title="Quiz Generator API")
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class QuizRequest(BaseModel):
    context: str
    difficulty: int = 3
    num_questions: int = 3

class Question(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str

class QuizResponse(BaseModel):
    questions: List[Question]

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    try:
        quiz_json = main.get_quiz(
            context=request.context, 
            difficulty=request.difficulty, 
            num_questions=request.num_questions
        )
        
        # Parse the JSON string returned by main.get_quiz()
        quiz_data = json.loads(quiz_json)
        
        # The data structure is {"questions": {"questions": [...]}}
        # We need to restructure it to match our expected response model
        if "questions" in quiz_data and "questions" in quiz_data["questions"]:
            return {"questions": quiz_data["questions"]["questions"]}
        else:
            # Handle case where structure might be different
            raise HTTPException(status_code=500, detail="Unexpected response structure from quiz generator")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.get("/")
async def health_check():
    return {"status": "healthy"}


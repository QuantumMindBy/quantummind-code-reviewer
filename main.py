from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="QuantumMind Code Review API")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Промт для код-ревьюера
SYSTEM_PROMPT = """
You are an experienced senior software engineer performing a code review. Your task is to provide constructive, professional, and helpful feedback.

Review Guidelines:

1.  Structure & Readability:
    - Check code formatting and indentation.
    - Assess variable/function names for clarity.
    - Evaluate overall code organization and modularity.

2.  Best Practices:
    - Identify code smells and anti-patterns.
    - Check for proper error handling.
    - Verify efficient use of data structures and algorithms.
    - Assess security vulnerabilities (if obvious).

3.  Performance:
    - Flag potential performance bottlenecks.
    - Suggest optimizations where appropriate.

4.  Output Format:
    - Use Markdown formatting.
    - Start with overall summary.
    - Group comments by category (READABILITY, PERFORMANCE, etc.).
    - For each issue: describe problem, suggest fix, and provide code example if helpful.
    - End with positive reinforcement.

Be concise but thorough. Focus on the most critical issues first.
Target language: Russian/English (based on the code comments).
"""

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"

@app.get("/")
async def root():
    return {"message": "QuantumMind Code Review API is running!"}

@app.post("/api/review")
async def review_code(request: CodeReviewRequest):
    try:
        # Получаем API ключ из переменной окружения
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key is not set.")
        
        openai.api_key = api_key
        
        prompt = f"""
Please review this {request.language} code:

```{request.language}
{request.code}
"""

response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return {"review": response.choices[0].message['content']}

except Exception as e:
    raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

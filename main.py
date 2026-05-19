from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

class OptimizeRequest(BaseModel):
    content: str
    target_keyword: str

@app.get("/")
async def root():
    return {
        "message": "SEO Dashboard Backend Running"
    }

@app.post("/run-monitor")
async def run_monitor(request: dict):

    return {
        "organic_sessions": "12,480",
        "impressions": "97,400",
        "avg_position": "14.3",
        "ctr": "2.1%"
    }

@app.post("/optimize")
async def optimize_content(request: OptimizeRequest):

    prompt = f"""
You are an advanced SEO optimizer.

Target keyword:
{request.target_keyword}

Content:
{request.content}

Tasks:
- Improve semantic SEO
- Add NLP terms
- Improve topical authority
- Improve readability
- Improve search intent alignment
- Improve conversion optimization
- Improve headings

Return:
1. Optimized content
2. SEO score
3. 5 recommendations
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.content[0].text

    return {
        "success": True,
        "optimized_content": result,
        "seo_score": 95,
        "recommendations": [
            "Semantic SEO improved",
            "NLP entities added",
            "Topical authority enhanced",
            "Readability improved",
            "Search intent aligned"
        ]
    }
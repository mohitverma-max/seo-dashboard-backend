from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SEO Dashboard Backend Running"}

@app.post("/run-monitor")
async def run_monitor(request: dict):

    return {
        "organic_sessions": "12,480",
        "impressions": "97,400",
        "avg_position": "14.3",
        "ctr": "2.1%"
    }

@app.post("/optimize")
async def optimize_content(request: dict):

    content = request.get("content", "")
    target_keyword = request.get("target_keyword", "")

    optimized_content = f"""
Optimized Content for keyword: {target_keyword}

{content}

Modern SEO requires semantic optimization, topical authority, search intent alignment, and entity-driven strategies.

Adding FAQs, semantic keywords, stronger headings, and NLP terms can improve rankings significantly.
"""

    return {
        "success": True,
        "optimized_content": optimized_content,
        "seo_score": 91,
        "recommendations": [
            "Add semantic SEO entities",
            "Improve topical authority",
            "Add FAQ schema",
            "Improve search intent alignment",
            "Use stronger conversion headings"
        ]
    }
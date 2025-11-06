import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Simple in-memory mock for demo purposes. In a real app, use the provided MongoDB helpers.
MOCK_JOBS = [
    {
        "id": 1,
        "title": "Frontend Engineer (React)",
        "company": "Acme Corp",
        "location": "Remote",
        "type": "Full-time",
        "salary": 155000,
        "description": "Build delightful web experiences with React, Vite, and modern tooling.",
        "url": "https://example.com/jobs/1",
        "tags": ["react", "vite", "javascript", "frontend"],
    },
    {
        "id": 2,
        "title": "Backend Engineer (FastAPI)",
        "company": "DataWorks",
        "location": "New York, NY",
        "type": "Full-time",
        "salary": 165000,
        "description": "Design APIs, optimize queries, and ship reliable services with FastAPI.",
        "url": "https://example.com/jobs/2",
        "tags": ["python", "fastapi", "mongodb", "api"],
    },
    {
        "id": 3,
        "title": "Full Stack Developer",
        "company": "BrightLabs",
        "location": "San Francisco, CA",
        "type": "Hybrid",
        "salary": 180000,
        "description": "Own features end-to-end across React frontends and Python backends.",
        "url": "https://example.com/jobs/3",
        "tags": ["react", "node", "python", "fullstack"],
    },
    {
        "id": 4,
        "title": "Data Engineer",
        "company": "StreamFlow",
        "location": "Austin, TX",
        "type": "Contract",
        "salary": 120000,
        "description": "Build data pipelines, ETL jobs, and analytics infrastructure.",
        "url": "https://example.com/jobs/4",
        "tags": ["python", "sql", "airflow", "etl"],
    },
    {
        "id": 5,
        "title": "Mobile Developer (React Native)",
        "company": "PocketTech",
        "location": "Remote",
        "type": "Full-time",
        "salary": 150000,
        "description": "Ship high-quality mobile apps with React Native and TypeScript.",
        "url": "https://example.com/jobs/5",
        "tags": ["react", "react-native", "typescript", "mobile"],
    },
]

@app.get("/api/jobs")
def get_jobs(
    q: Optional[str] = Query(None, description="Search term for title/company/tags"),
    location: Optional[str] = Query(None, description="Preferred location"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    experience: Optional[str] = Query(None, description="Experience level"),
    limit: int = Query(12, ge=1, le=50),
):
    results = MOCK_JOBS

    def matches(job):
        text = (q or "").lower()
        loc = (location or "").lower()
        skill_list = [s.strip().lower() for s in (skills or "").split(",") if s.strip()]

        if text:
            hay = " ".join([
                job["title"], job["company"], job["description"], " ".join(job.get("tags", []))
            ]).lower()
            if text not in hay:
                return False
        if loc and loc not in job["location"].lower():
            return False
        if skill_list and not any(s in job.get("tags", []) for s in skill_list):
            return False
        return True

    filtered = [j for j in results if matches(j)][:limit]

    return {"jobs": filtered, "count": len(filtered)}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

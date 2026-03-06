from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Grant Proposal Generator & Evaluator",
    description="CrewAI multi-agent system for SERB research grant proposal generation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from routes.grants import router as grants_router
from routes.pipeline import router as pipeline_router

app.include_router(grants_router, prefix="/api/grants", tags=["grants"])
app.include_router(pipeline_router, prefix="/api/pipeline", tags=["pipeline"])


@app.get("/")
async def root():
    return {"status": "running", "service": "AI Grant Proposal Generator"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

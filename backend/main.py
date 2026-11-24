from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


from backend.routers import (
    analytics,
    cost,
    destinations,
    recommendations,
)

app = FastAPI(
    title="TravelIQ API",
    description=(
        "An explainable travel destination recommendation, "
        "budget estimation, and analytics API."
    ),
    version="1.0.0",
)

# Allow the local React development server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to the TravelIQ API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(destinations.router)
app.include_router(recommendations.router)
app.include_router(cost.router)
app.include_router(analytics.router)

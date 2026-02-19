from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Hospital AI Survival Lab",
    version="0.1.0",
    description="Economic survival simulation for ER-focused AI agents.",
)

app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

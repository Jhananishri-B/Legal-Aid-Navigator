"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import engine, Base
from app.routers import auth, requests, discovery

# Create all tables on startup (skip if they already exist or DDL is restricted)
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    import warnings
    warnings.warn(
        f"[Legal Aid Navigator] Could not auto-create tables: {e}\n"
        "If using TiDB/MySQL, run the DDL script manually with an admin user."
    )

app = FastAPI(
    title="Legal Aid Navigator API",
    version="1.0.0",
    description="Backend for the Legal Aid Navigator – legal-aid discovery, eligibility, and appointment booking.",
)

# CORS – use permissive origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(discovery.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "Legal Aid Navigator API"}


# Catch-all for unhandled exceptions – ensures CORS headers are always returned
from fastapi.responses import JSONResponse
from starlette.requests import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

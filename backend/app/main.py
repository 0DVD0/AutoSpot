from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers import explorerRouter, postsRouter, userRouter, authRouter, uploadRouter
from app.core.config import settings
from app.db import get_db


app = FastAPI(title=settings.app_name)
app.include_router(postsRouter.router)
app.include_router(userRouter.router)
app.include_router(authRouter.router)
app.include_router(uploadRouter.router)
app.include_router(explorerRouter.router)

@app.get("/")
def read_root():
    return {
        "message": "AutoSpot API is running",
        "docs": "/docs",
    }


@app.get("/health/db")
def check_database(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }
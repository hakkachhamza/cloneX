from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, crawl

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["Crawl Jobs"])

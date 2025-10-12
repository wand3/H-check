import re
from typing import List, Annotated

# from pymongo import DESCENDING

from app.logger import logger
from fastapi import APIRouter, Depends, HTTPException, status, Query

# from webapp.models.blog import Post, get_post_model
# from webapp.models.project import get_project_model, ProjectModel
# from webapp.schemas.blog import BlogPostInDB, BlogPost
# from webapp.schemas.project import Project, ProjectInDB

main = APIRouter()


@main.get("/fhir")
async def root():
    return {"message": "Hello World"}

"""
    Routes for all posts
    
"""

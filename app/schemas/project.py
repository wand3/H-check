from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict

from webapp.schemas import PyObjectId


class TechStack(BaseModel):
    """Details about technologies used in the project."""
    language: Optional[List[str]] = Field(None, description="Programming language (e.g., Python, JavaScript)")
    frameworks: Optional[List[str]] = Field(None, description="Frameworks used (e.g., React, Django)")
    databases: Optional[List[str]] = Field(None, description="Databases used (e.g., PostgreSQL, MongoDB)")
    tools: Optional[List[str]] = Field(None, description="Development/Deployment tools (e.g., Docker, Kubernetes, AWS)")


class TestingDetails(BaseModel):
    """Specifics about testing methodologies and automation."""
    test_types: Optional[List[str]] = Field(None, description='Types of testing performed e.g. "Unit", "Integration", '
                                                              '"E2E, Performance", "Security", "API" ')
    automation_frameworks: Optional[List[str]] = Field(None, description="Automation frameworks used (e.g., Selenium, "
                                                                         "pytest)")
    ci_cd_integration: Optional[List[str]] = Field(None, description="Whether CI/CD was integrated for testing")


class Project(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "_id": "678501e2a246221541ec8a0e",
                "title": "E-commerce Platform",
                "description": "Developed a full-featured e-commerce platform with user authentication, product "
                               "catalog,"
                               "shopping cart, and payment gateway integration.",
                "project_url": "https://example.com/ecommerce",
                "github_url": "https://github.com/yourusername/ecommerce",
                "technologies": [
                    {"language": "Python", "frameworks": ["Django", "Django REST Framework"],
                     "databases": ["PostgreSQL"]},
                    {"language": "JavaScript", "frameworks": ["React"], "tools": ["Webpack"]}
                ],
                "roles": ["Full-Stack Developer", "Test Engineer", "Automation Engineer"],
                "testing_details": {
                    "test_types": ["Unit", "Integration", "E2E", "API"],
                    "automation_frameworks": ["pytest", "Selenium"],
                    "ci_cd_integration": True
                },
                "images": ["image1.png", "image11.mp4"]
            }

        })

    """Comprehensive details about a portfolio project."""
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    title: Optional[str] = Field(..., description="Project title")
    description: Optional[str] = Field(..., description="Detailed project description")
    project_url: Optional[str] = Field(None, description="Link to the live project or demo")
    github_url: Optional[str] = Field(None, description="Link to the GitHub repository")
    technologies: Optional[TechStack] = Field(None, description="List of technologies used")
    roles: Optional[List[str]] = Field(...,
                                       description='Your roles on the project e.g "Full-Stack Developer", "Frontend '
                                                   'Developer", "Backend Developer", "Test Engineer", "Automation '
                                                   'Engineer", "DevOps Engineer"')
    testing_details: Optional[TestingDetails] = Field(None, description="Details about testing and automation")
    images: Optional[List[str]] = Field(None, description="List of URLs to project screenshots/images")


class ProjectInDB(Project):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)  # Alias _id to id
    created_at: datetime
    updated_at: datetime



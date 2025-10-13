import re
from typing import List, Annotated
from app.logger import logger
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database.db_engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.nlp.fhir_nlp_service import FHIRQueryProcessor



main = APIRouter()


@main.get("/fhir")
async def root():
    return {"message": "Hello World"}

"""
    Routes for all posts
    
"""


@main.post("/query")
async def process_query(
        query_data: dict,
        db: AsyncSession = Depends(get_db),
):
    from datetime import datetime
    start_time = datetime.now()

    try:
        # Initialize processor with database session
        processor = FHIRQueryProcessor(db)

        # Build FHIR query
        fhir_query = processor.build_fhir_query(query_data['query'])

        # Execute against real FHIR server
        fhir_response = await processor.execute_fhir_query(fhir_query['fhir_url'])

        # Process the response
        processed_results = await processor.process_fhir_response(fhir_response, fhir_query['filters'])

        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

        # # Log the query
        # await processor.log_query(
        #     user_id=current_user.id,
        #     natural_language_query=query_data['query'],
        #     fhir_query=fhir_query['fhir_url'],
        #     fhir_response=fhir_response,
        #     processed_results=processed_results,
        #     execution_time=execution_time
        # )


        return {
            "original_query": query_data['query'],
            "fhir_query": fhir_query,
            "processed_results": processed_results,
            "execution_time": execution_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@main.get("/suggestions")
async def get_suggestions():
    return {
        "suggestions": [
            "Show me all diabetic patients over 50",
            "Patients with asthma under 30",
            "List patients with hypertension",
            "Count diabetic patients",
            "Show me all patients over 65 with diabetes"
        ]
    }


@main.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    from database import test_db_connection
    db_status = await test_db_connection()
    return {
        "status": "healthy",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }
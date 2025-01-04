from fastapi import APIRouter, HTTPException, status

from .brain import Brain
from .tags import Tags
from .utils import create_knowledge_base_from_sitemap
# from .db import VECTOR_DB

router = APIRouter(
    prefix=Tags.get_router_prefix(Tags.RAG_ENGINE),
    tags=[Tags.RAG_ENGINE],
)

VECTOR_DB = {}

# Load text embedding model
brain = Brain()


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(sitemap_url: str):
    if not sitemap_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sitemap URL is required")

    create_knowledge_base_from_sitemap(brain, sitemap_url, VECTOR_DB)
    
    return {"message": "Knowledge base ingested successfully"}


@router.get("/askQuery", status_code=status.HTTP_200_OK)
def get_prompt(prompt: str):
    if not prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")

    response = brain.generate_response(prompt, VECTOR_DB)

    return {"response": response}

@router.get("/printVectorDD", status_code=status.HTTP_200_OK)
def print_vector_db():
    data = VECTOR_DB.get("data")
    data_length = len(data) if data else 0
    return {"data_length": data_length, "sample_data": data[:5] if data else []}
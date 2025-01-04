from fastapi import APIRouter, HTTPException, status

from .brain import Brain
from .tags import Tags
from .utils import create_knowledge_base_from_sitemap


router = APIRouter(
    prefix=Tags.get_router_prefix(Tags.RAG_ENGINE),
    tags=[Tags.RAG_ENGINE],
)

# # Load text embedding model
brain = Brain()

VECTOR_DB = {}

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(sitemap_url: str):
    if not sitemap_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sitemap URL is required")

    documents = create_knowledge_base_from_sitemap(sitemap_url)
    
    return {"message": "Knowledge base ingested successfully"}


@router.get("/askQuery", status_code=status.HTTP_200_OK)
def get_prompt(prompt: str):
    if not prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")

    response = "This is a response"

    return {"response": response}
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.params import Depends

from .brain import Brain
from .db import get_db
from .tags import Tags
from .utils import create_knowledge_base_from_sitemap, load_vector_db_from_pickle_file, store_vector_db_in_pickle_file

router = APIRouter(
    prefix=Tags.get_router_prefix(Tags.RAG_ENGINE),
    tags=[Tags.RAG_ENGINE],
)

# Initialize the brain
brain = Brain()


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(sitemap_url: str, store_in_pickle: bool, background_tasks: BackgroundTasks, db = Depends(get_db)):
    if not sitemap_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sitemap URL is required")

    background_tasks.add_task(create_knowledge_base_from_sitemap, brain, sitemap_url, db)
    
    if store_in_pickle:
        store_vector_db_in_pickle_file(db)
    
    return {"message": "Knowledge base ingestion started"}


@router.get("/ask-query", status_code=status.HTTP_200_OK)
def get_prompt(prompt: str, db = Depends(get_db)):
    if not prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")
    
    if not db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base is empty")

    response = brain.generate_response(prompt, db)

    return {"response": response}


@router.get("/load-vector-db-from-pickle", status_code=status.HTTP_201_CREATED)
def load_vector_db_from_pickle(db = Depends(get_db)):
    load_vector_db_from_pickle_file(db)
    
    if not db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Knowledge base is empty")
    
    return {"message": "Vector DB loaded successfully"}
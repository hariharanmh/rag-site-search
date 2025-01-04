from fastapi import FastAPI, HTTPException, status

from apis.ragengine.routes import router as rag_engine_router

from configs import constants


app = FastAPI(
    title=constants.APP_TITLE,
    description=constants.APP_DESCRIPTION,
    version=constants.APP_VERSION,
    openapi_url=constants.OPENAPI_URL,
    docs_url=constants.DOCS_URL,
    redoc_url=constants.REDOC_URL,
    debug=constants.APP_DEBUG,
    contact=constants.CONTACT
)

app.include_router(rag_engine_router)


@app.get("/", tags=["System Check"])
def root():
    return {"message": f"Welcone to {constants.APP_TITLE}"}
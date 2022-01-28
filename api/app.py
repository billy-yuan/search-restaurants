from fastapi import FastAPI
from search_service.encoder import SbertEncoder
from search_service.indexer import FaissIndexer
from search_service.s3_helpers import load_env_var


FILE_NAME = load_env_var("EMBEDDING_PATH")

app = FastAPI()
E = SbertEncoder()
F = FaissIndexer(FILE_NAME)


@app.get("/")
def read_root():
    return "Encoder"


@app.get("/search")
def get_results(q: str):
    if q:
        embedding = E.encode([q])
        result = F.search(embedding)
        return {"response": result}
    else:
        return "Need query"

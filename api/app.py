from fastapi import FastAPI
from encoder.encoder import SbertEncoder

app = FastAPI()
E = SbertEncoder()


@app.get("/")
def read_root():
    return "Encoder"


@app.get("/encode")
def get_encoding(q: str):
    if q:
        embedding = E.encode([q])
        return {"encoding": embedding.shape}
    else:
        return "Need query"

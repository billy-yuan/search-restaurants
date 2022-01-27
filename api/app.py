from fastapi import FastAPI
from encoder.encoder import SbertEncoder

app = FastAPI()
E = SbertEncoder()


@app.get("/")
def read_root():
    import boto3

    s3 = boto3.resource('s3')

    result = []
    for bucket in s3.buckets.all():
        result.append(bucket.name)

    return result


@app.get("/encode")
def get_encoding(q: str):
    if q:
        embedding = E.encode([q])
        return {"encoding": embedding.shape}
    else:
        return "Need query"

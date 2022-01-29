# search-restaurants

API that takes a query and returns restaurants that were featured in articles most similar to the query. Restaurants are from Eater.com NY.

For the text search, semantic search is applied:
* Sentence embeddings created using [Sentence Transformers](https://www.sbert.net/examples/applications/semantic-search/README.html).
* For fast searching of high dimensional vectors, [FAISS](https://github.com/facebookresearch/faiss) is used.
* MongoDb is the database.

Try the API [here](https://search-eater.herokuapp.com/docs#/default/get_results_search_get). It may be slow since it is hosted on a low cost Heroku server.

## To build a docker image

`docker build -t <image name> .`

Example: `docker build -t my-project .`

## Troubleshooting

### Segmentation fault error

Make sure Faiss 1.6.5 (not the latest version) is installed as directed in `requirements.txt`. If not, then a segmentation fault error will happen since one of the Sbert packages uses the latest Faiss. See this [comment](https://github.com/facebookresearch/faiss/issues/2099#issuecomment-961172708).

### FileNotFound when downloading from S3

`FileNotFoundError: [Errno 2] No such file or directory: 'search_service/download/embeddings.D6C33CDd'`
Make sure the local directory of where S3 files are being downloaded to is created before you download otherwise you will see this error.

If the path for the embeddings is `search_service/download/embeddings`, then `search_service/download` must be created before the server starts. You won't need to worry about this if you are saving files in `search_service/download` since the `Dockerfile` creates this directory, but if you change the directory, then make sure you update the Dockerfile.

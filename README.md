# search-restaurants

## To build a docker image

`docker build -t <image name> .`

Example: `docker build -t my-project .`

## Troubleshooting

### Segmentation fault error

Make sure Faiss 1.6.5 (not the latest version) is installed as directed in `requirements.txt`. If not, then a segmentation fault error will happen since one of the Sbert packages uses the latest Faiss. See this [comment](https://github.com/facebookresearch/faiss/issues/2099#issuecomment-961172708).

### FileNotFound when downloading from S3

`FileNotFoundError: [Errno 2] No such file or directory: 'search_service/download/embeddings.D6C33CDd'`
Make sure the directory of where you will download files from S3 is created before you download otherwise you will see this error.

If the S3 object key for the embeddings is `search_service/download/embeddings`, then `search_service/download` must be created before the server starts. You won't need to worry about this if you are saving files in `search_service/download` since the `Dockerfile` creates this directory, but if you change the directory, then make sure you update the Dockerfile.

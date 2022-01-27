# search-restaurants

## To build a docker image

`docker build -t <image name> .`

Example: `docker build -t my-project .`

## Troubleshooting

Make sure Faiss 1.6.5 is installed as directed in `requirements.txt`. If not, then a segmentation fault error will happen since one of the Sbert packages uses the latest Faiss. See this [comment](https://github.com/facebookresearch/faiss/issues/2099#issuecomment-961172708).

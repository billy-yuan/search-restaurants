from search_service.s3_helpers import download_file_from_s3, upload_file_to_s3, load_env_var
import pickle

FILE_NAME = "search_service/test_file"
BUCKET = load_env_var("BUCKET_NAME")


# Make test file + save to file
x = [1, 2, 3, 4]


pickle.dump(x, open(FILE_NAME, "wb"))
print("Dumped file to file")


# Upload file to s3
if upload_file_to_s3(FILE_NAME, BUCKET):
    print("Uploaded file")

# load indexer if exists


if download_file_from_s3(FILE_NAME, BUCKET, FILE_NAME):
    print("Downloaded file")

# open file
loaded_file = pickle.load(open(FILE_NAME, 'rb'))
print(loaded_file)
# class Indexer:

#     def __init__(self):
#         pass

#     def load_index():
#         pass

#     def add_to_index():
#         pass

#     def write_to_s3():
#         pass

from minio import Minio

BUCKET_NAME = "don-t-ttach-my-docs"

client = Minio("localhost:9000", access_key="remi_czn", secret_key="password", secure=False)

found = client.bucket_exists(BUCKET_NAME)
if not found:
    client.make_bucket(BUCKET_NAME)
else:
    print(BUCKET_NAME + " already exists")

client.fput_object(BUCKET_NAME, "1234.jpeg", r"C:\Users\cazin\Pictures\bda.jpeg")
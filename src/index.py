import os

from flask import Flask, request, make_response, jsonify
from minio import Minio

BUCKET_NAME = "don-t-ttach-my-docs"

client = Minio("localhost:9000", access_key="remi_czn", secret_key="password", secure=False)


def upload_to_minio(file):
    found = client.bucket_exists(BUCKET_NAME)
    if not found:
        client.make_bucket(BUCKET_NAME)
    else:
        print(BUCKET_NAME + " already exists")

    size = os.fstat(file.fileno()).st_size
    client.put_object(BUCKET_NAME, file.filename, file, size)


app = Flask(__name__)
PORT = 3200
HOST = "0.0.0.0"


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return make_response(jsonify({"error": "Missing"}), 400)

    req = request.files["file"]
    upload_to_minio(req)
    return make_response()


@app.route("/files", methods=['GET'])
def get_files():
    bucket = client.list_objects(BUCKET_NAME)
    res = []
    for objet in bucket:
        print(client.get_presigned_url("GET", BUCKET_NAME, str(objet.object_name)))
        res.append(client.presigned_get_object(BUCKET_NAME, str(objet.object_name)))
    return make_response(jsonify(res))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

import os

import jwt
import requests

from flask import Flask, request, make_response, jsonify, Response
from minio import Minio
from urllib.parse import urlparse

BUCKET_NAME = "don-t-ttach-my-docs"
SECRET = "secret"

client = Minio("localhost:9000", access_key="remi_czn", secret_key="password", secure=False)


def upload_to_minio(file, email):
    check_bucket_exists()

    size = os.fstat(file.fileno()).st_size
    client.put_object(BUCKET_NAME, email + "/" + file.filename, file, size)
    return build_url(email, file.filename)


def build_url(email, filename):
    url = client.presigned_get_object(BUCKET_NAME, email + "/" + filename)
    query = str(urlparse(url).query)
    token = jwt.encode({"query": query}, SECRET, algorithm="HS256")
    res_url = "/file/" + filename + "?sender=" + email + "&token=" + token
    return res_url


def check_bucket_exists():
    found = client.bucket_exists(BUCKET_NAME)
    if not found:
        client.make_bucket(BUCKET_NAME)


app = Flask(__name__)
PORT = 3200
HOST = "0.0.0.0"


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files or "email" not in request.form:
        return make_response(jsonify({"error": "Missing arguments: file or email"}), 400)

    res = []
    for file in request.files.getlist("file"):
        url = upload_to_minio(file, request.form["email"])
        res.append(url)
    return make_response(res)


@app.route("/file/<file_name>", methods=["GET"])
def get(file_name):
    if "sender" not in request.args or "token" not in request.args:
        return make_response(jsonify({"error": "Missing query arguments: sender or token"}), 400)

    filename = file_name
    email = request.args["sender"]
    token = request.args["token"]
    try:
        infos = jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as err:
        print(err)
        return make_response(jsonify({"error": "Wrong token"}))
    file_url = "http://localhost:9000/"+BUCKET_NAME+"/"+email+"/"+filename+"?"+infos["query"]
    file = requests.get(file_url)
    if file.status_code == 200:
        return Response(file.content, mimetype=file.headers.get("Content-Type"))
    else:
        return make_response(jsonify({"error": "Unable to retrieve the file"}))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

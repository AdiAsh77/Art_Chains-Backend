from flask import Flask, request, jsonify
import requests
import json
from pymongo import MongoClient

app = Flask(__name__)

# PINATA_API_KEY = "757d1d4a47cc7ab3d947"
# PINATA_SECRET_KEY = "b8c1251775cdac989b19fe1bae8044d0119d08594d4c414b6a21e2c03125fd57"
# PINATA_PIN_FILE_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

# MongoDB connection
MONGO_URL = "mongodb+srv://AdiAsh77:{quote_plus(password)}@cluster0.bhxmoh4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client["HackOasis"]
gallary_collection = db["Gallary"]


@app.route("/upload/", methods=["POST"])
def upload_file():
    if "file" not in request.files or "name" not in request.form:
        return jsonify({"error": "File and name are required"}), 400

    file = request.files["file"]
    name = request.form["name"]

    files = {"file": (file.filename, file.read())}
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }

    # Call plagiarism check (local endpoint)
    data = {"d": "45", "vb": "ddddddd444"}
    response2 = requests.post("http://127.0.0.1:5000/plagarism", json=data).json()

    if response2["plagarism"] < 0.6:
        return jsonify({"error": "Plagiarism detected. Upload rejected."}), 400

    attributes = response2["attributes"]
    attributes.append(file.content_type)

    metadata = {
        "name": file.filename,
        "attributes": attributes
    }

    # Upload to Pinata
    response = requests.post(
        PINATA_PIN_FILE_URL,
        files=files,
        headers=headers,
        data={"pinataMetadata": json.dumps(metadata)}
    )

    if response.status_code == 200:
        result = response.json()
        cid = result["IpfsHash"]
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"

        newdata = {
            "userPublicKey": "5GGx8UxRqnaNPje65dJraVxiELvPgtBrQWsiWYN1zqPD",
            "title": "A Day in the Park yay",
            "description": "A stunning, sun-drenched photograph of a park scene in the spring.",
            "ipfsUri": url,
            "tags": attributes
        }

        # Call NFT mint API
        response3 = requests.post("https://hacosis.onrender.com/api/mint", json=newdata).json()

        # Save in DB
        data_to_store = {
            "name": name,
            "filename": file.filename,
            "cid": cid,
            "url": url,
            "nft": response3.get("nftAddress"),
            "pinataMetadata": metadata,
            "db_response": response2
        }
        gallary_collection.insert_one(data_to_store)

        return jsonify({"message": "success", "response": response3})
    else:
        return jsonify({"error": response.text}), 500


@app.route("/database", methods=["POST"])
def save_to_db():
    data = request.json
    result = gallary_collection.insert_one(data)
    return jsonify({"Creator": data["name"], "CID": data["cid"]})


@app.route("/plagarism", methods=["POST"])
def plag_end():
    atri = ["water", "green"]
    return jsonify({"attributes": atri, "plagarism": 0.8})


@app.route("/gallary", methods=["GET"])
def get_user():
    documents = [doc["cid"] for doc in gallary_collection.find()]
    return jsonify(documents)


if __name__ == "__main__":
    app.run()

from fastapi import FastAPI, File, UploadFile, Form
import requests
import json
import motor.motor_asyncio
import httpx


app = FastAPI()

# PINATA_API_KEY = "757d1d4a47cc7ab3d947"
# PINATA_SECRET_KEY = "b8c1251775cdac989b19fe1bae8044d0119d08594d4c414b6a21e2c03125fd57"
# PINATA_PIN_FILE_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

MONGO_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# password = "Aditya@77s"
# url = f"mongodb+srv://AdiAsh77:{quote_plus(password)}@cluster0.bhxmoh4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = motor.motor_asyncio.AsyncIOMotorClient(url)

db = client["HackOasis"]
gallary_collection = db["Gallary"]



@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), name: str = Form(...) ):
    files = {
        'file': (file.filename, await file.read())
    }

    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }

    data = {"d":"45", "vb" : "ddddddd444"}
    response2 = (await httpx.AsyncClient().post("http://127.0.0.1:8000/plagarism", json=data)).json()
    if response2["plagarism"] < 0.6:
        return {"error": "Plagiarism detected. Upload rejected."}
    atributes = response2["attributes"]
    atributes.append(file.content_type)
    
    metadata = {
        "name": file.filename,
        "attributes": atributes
    }

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
            "tags": atributes
        }
        response3 = (await httpx.AsyncClient().post("https://hacosis.onrender.com/api/mint", json=newdata)).json()
        data =  {"name": name, "filename": file.filename, "cid": cid, "url": url, "nft": response3["nftAddress"], "pinataMetadata": metadata, "db_response": response2}
        rep = (await httpx.AsyncClient().post("http://127.0.0.1:8000/database", json=data)).json()
        return {"message": "success", "response": response3}

    else:
        return {"error": response.text}


@app.post("/database")
async def test_endpoint(data: dict):
    result = await gallary_collection.insert_one(data)
    return {"Creator": data["name"], "CID": data["cid"]}

@app.post("/plagarism")
async def plag_end(data: dict):
    # result = await gallary_collection.insert_one(data)
    atri = ["water", "green"]
    return {"attributes": atri, "plagarism": 0.8}

@app.get("/gallary")
async def get_user():
    documents = []
    async for doc in gallary_collection.find():
        documents.append(doc["d"])
    return documents
    

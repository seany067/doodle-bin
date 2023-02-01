import os
import uuid
import boto3
from dotenv import dotenv_values
from typing import Optional
from botocore.exceptions import ClientError
from pathlib import Path
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.exceptions import HTTPException

# Setup

ROOT_DIR = Path(__file__).parent

with open(ROOT_DIR / "templates/index.html", "r") as f:
        html_content =  f.read()

class Model(BaseModel):
    id: Optional[str]
    content: Optional[str]

if not os.environ.get("DB_REGION_NAME", False):
    env = dotenv_values("/run/secrets/aws")
else:
    env = os.environ

#AWS

AWS_SETTINGS = {
    "aws_access_key_id": env.get("DB_ACCESS_KEY_ID"),
    "aws_secret_access_key": env.get("DB_SECRET_ACCESS_KEY"),
    "region_name": env.get("DB_REGION_NAME")
}

table_name = "doodle-bin"

# FastAPI

app = FastAPI()
app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")

@app.on_event("startup")
async def startup():
    app.state.db = boto3.resource('dynamodb', **AWS_SETTINGS)

# Routes

@app.get("/")
def index():
    return RedirectResponse(url=f"/{uuid.uuid4()}")

@app.get("/{id}")
def index(request: Request, id: uuid.UUID):
    return HTMLResponse(
        content=html_content,
        status_code=200
    )
 
@app.post("/{id}")
async def save(request: Request, id: str, body: Model):
    table = request.app.state.db.Table(table_name)
    try:
        res = table.put_item(Item={'id': id, 'content': body.content})
    except ClientError as e:
        raise e
        # raise HTTPException(status_code=404, detail="Doodle could not be saved found")
    return Response("Ok", status_code=200)


@app.get("/load/{id}")
async def load(request: Request, id: str):
    try:
        table = request.app.state.db.Table(table_name)
        res = table.get_item(Key={'id': id})
        return res["Item"]
    except:
        raise HTTPException(status_code=404, detail="Doodle not found")

import os
import uuid
import boto3
from io import BytesIO, StringIO
from dotenv import dotenv_values
from typing import Optional
from botocore.exceptions import ClientError
from pathlib import Path
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Setup

ROOT_DIR = Path(__file__).parent

templates = Jinja2Templates(directory=ROOT_DIR / "templates")

class Model(BaseModel):
    id: Optional[str]
    content: Optional[str]
    image: Optional[str]

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
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/widget/{id}")
def widge_index(request: Request, id: uuid.UUID):
    try:
        table = request.app.state.db.Table(table_name)
        res = table.get_item(Key={'id': str(id)})
    except:
        raise HTTPException(status_code=404, detail="Doodle not found")

    if res is None or 'image' not in res["Item"]:
        raise HTTPException(status_code=404, detail="Doodle not found")
    img_data: str = res["Item"]["image"]
    return Response(img_data, status_code=200, headers={"Content-type": "image/svg+xml"}, media_type="image/svg+xml")

@app.get("/png/{id}")
def widge_index(request: Request, id: uuid.UUID):
    try:
        table = request.app.state.db.Table(table_name)
        res = table.get_item(Key={'id': str(id)})
    except:
        raise HTTPException(status_code=404, detail="Doodle not found")

    if res is None or 'image' not in res["Item"]:
        raise HTTPException(status_code=404, detail="Doodle not found")
    img_data: str = res["Item"]["image"]
    img_io = StringIO()
    img_io.write(img_data)
    img_io.seek(0)
    render_obj = svg2rlg(img_io)
    out_io = BytesIO()
    renderPM.drawToFile(render_obj, out_io, fmt="PNG")
    out_io.seek(0)
    return StreamingResponse(out_io, status_code=200, headers={"Content-type": "image/png"}, media_type="image/png")


@app.post("/{id}")
async def save(request: Request, id: str, body: Model):
    table = request.app.state.db.Table(table_name)
    try:
        table.put_item(Item={'id': id, 'content': body.content, 'image': body.image})
    except ClientError:
        raise HTTPException(status_code=404, detail="Doodle could not be saved found")
    return Response("Ok", status_code=200)


@app.get("/load/{id}")
async def load(request: Request, id: str):
    try:
        table = request.app.state.db.Table(table_name)
        res = table.get_item(Key={'id': id})
        return res["Item"]
    except:
        raise HTTPException(status_code=404, detail="Doodle not found")

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import shutil
from dotenv import load_dotenv
import os
from pydantic import BaseModel

app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# CORS settings to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change if frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = r"C:\Users\Robin Roy\Desktop\idkhack\files\upload"    # ROBIN
# UPLOAD_DIR =          # shreesh
# UPLOAD_DIR =          # swagat

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    print(file)
    if not file.filename:
        raise ValueError("No filename provided")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "message": "File uploaded successfully"}


class Query(BaseModel):
    prompt: str
    video_version: str      # this is the file name in /edit


@app.post("/query")
async def user_query(query: Query):
    """
    work on the mentioned video version using the given prompt.

    example: trim this video from 2nd second to the 7th second.

    It'll then use this prompt on the specified video with the name "video_version.mp4".
    """


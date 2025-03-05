from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import shutil
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Tuple
import subprocess


app = FastAPI()
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


SYSTEM_INSTRUCTION = """
Write ffmpeg code for the queries given. Use the best code possible for the best output.
"""

# CORS settings to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change if frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = r"C:\Users\Robin Roy\Desktop\idkhack\files\upload"  # ROBIN
# UPLOAD_DIR =          # shreesh
# UPLOAD_DIR =          # swagat

os.makedirs(UPLOAD_DIR, exist_ok=True)

def ffmpeg_runner(ffmpeg_code: str):
    """
    ffmpeg_code: the command line code for running ffmpeg
    """
    
    print(ffmpeg_code)


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    print(file)
    if not file.filename:
        raise ValueError("No filename provided")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(f'ffmpeg -i "../files/upload/{file.filename}" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1" -r 30 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 -movflags +faststart "../files/upload/normalized_{file.filename}"')
    except subprocess.CalledProcessError as e:
        print(e)
        raise ValueError("Normalizing failed")

    return {"filename": file.filename, "message": "File uploaded successfully"}


class Query(BaseModel):
    prompt: str
    video_version: str  # this is the file name in /edit

@app.post("/query")
async def user_query(query: Query) -> Tuple[bool, str]:
    """
    work on the mentioned video version using the given prompt.

    example: trim this video from 2nd second to the 7th second.

    It'll then use this prompt on the specified video with the name "video_version.mp4".

    Returns the new video version number as a string
    """

    chat = client.aio.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[ffmpeg_runner]
        ),
    )

    response = await chat.send_message(query.prompt)

    return False, response.text
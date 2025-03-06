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

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = r"C:\Users\HP\Desktop\Hacknight\idkhack\files\upload"
EDIT_DIR = r"C:\Users\HP\Desktop\Hacknight\idkhack\files\edit"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EDIT_DIR, exist_ok=True)

def ffmpeg_runner(ffmpeg_code: str):
    print(ffmpeg_code)
    try:
        process = subprocess.run(
            ffmpeg_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with error:\n{e.output}")
        return False

def scene_detect_runner(scene_detect_code: str):
    print(scene_detect_code)
    try:
        process = subprocess.run(
            scene_detect_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Scene detection failed with error:\n{e.output}")
        return False

def whisper_runner(whisper_code: str):
    print(whisper_code)
    try:
        process = subprocess.run(
            whisper_code, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Whisper failed with error:\n{e.output}")
        return False

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    print(file)
    if not file.filename:
        raise ValueError("No filename provided")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".mp4"):
        try:
            subprocess.run(f'ffmpeg -i "../files/upload/{file.filename}" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1" -r 30 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 -movflags +faststart "../files/upload/normalized_{file.filename}"')
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValueError("MP4 Normalizing failed")
    elif file.filename.endswith(".mp3"):
        try:
            subprocess.run(
                f'ffmpeg -i "../files/upload/{file.filename}" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -b:a 192k -ar 44100 "../files/upload/normalized_{file.filename}"',
                shell=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValueError("MP3 normalizing failed")

    os.remove(f"../files/upload/{file.filename}")
    os.rename(f"../files/upload/normalized_{file.filename}", f"../files/upload/{file.filename}")

    
    return {"filename": file.filename, "message": "File uploaded successfully"}

class Query(BaseModel):
    prompt: str
    video_version: str

@app.post("/query")
async def user_query(query: Query) -> Tuple[bool, int]:
    num_files = len([name for name in os.listdir(EDIT_DIR) if os.path.isfile(os.path.join(EDIT_DIR, name))])
    
    SYSTEM_INSTRUCTION = f"""
Write command-line code based on user queries. The files are inside ../files/upload. 
If the user asks for scene detection, use the command:
    scenedetect -i ../files/upload/{query.video_version} detect-content split-video -o ../files/edit/{num_files+1}
If the user asks for subtitles, use Whisper with the command:
    whisper ../files/upload/{query.video_version} --language English --output_format srt --output_dir ../files/edit
Otherwise, use ffmpeg. Save output videos in ../files/edit as {num_files+1}.mp4.

ALWAYS CALL THE APPROPRIATE FUNCTION: ffmpeg_runner for FFmpeg, scene_detect_runner for scene detection, or whisper_runner for Whisper.
"""

    chat = client.aio.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[ffmpeg_runner, scene_detect_runner, whisper_runner]
        ),
    )

    response = await chat.send_message(query.prompt)
    print(response)

    try:
        if response.automatic_function_calling_history[-1].parts[0].function_response.response['result']:
            return True, num_files+1
        else:
            return False, -1
    except Exception as e:
        print(e)
        return False, -1
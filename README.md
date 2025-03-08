# easyEdits: your copilot for video editing

> [!IMPORTANT]  
> The application is under active development. Please join the [Discord server](https://discord.gg/GSknuxubZK) if you're going to run it.

![image](https://github.com/user-attachments/assets/18563506-65d6-4ea4-91df-2913dc9c2314)

easyEdits helps you to avoid the clutter and complexity of a modern video editor. Just say what you want and it'll achieve the task for you ✨

See the demo here: https://youtu.be/T5y9oxNX14Q?si=OIYCUJhH0hD3Mygn

## Key Features
- ✨ **Prompt based edit workflow:** You can trim/merge/crop videos and so much more by just prompting.
- 🌿**Version control styled editing:** Every edit you make is a new version, providing you fine grained control and the ability to mix and match videos from different iterations.
- 🔗**Integrations:**
    - OpenAI whisper helps you make quick transcriptions.
    - Scenedetect for splitting videos into different clips based on shot changes.
    - Gemini for Audio descriptions.
- 🏡**Self Hostable:** Open source and easy to deploy locally.

## How do I use this?

Currently, you've to setup the application locally since we provide no hosted alternatives (coming soon!). Follow the steps below:
#### 🦄Local Setup
#### 1. **Clone the repository**

````
git clone https://github.com/robinroy03/easyEdits.git
````
#### 2. **Open the folder /backend and install the requirements**
Do this when you're inside the folder `easyEdits/backend`
```
python -m venv venv
venv/Scripts/activate       (if you're on windows)
source venv/bin/activate    (if you're on mac/linux)
pip install -r requirements.txt
```
#### 3. **Open the folder /frontend and install the requirements**
Do this when you're inside the folder `easyEdits/frontend`
```
npm i
```
#### 4. **Download FFmpeg**
https://ffmpeg.org/download.html

These guides might be of help,

Windows: https://www.wikihow.com/Install-FFmpeg-on-Windows

MacOS: https://phoenixnap.com/kb/ffmpeg-mac

#### 5. **Setup the Environment Variables**
Add a `.env` file inside `/backend` with the following content
```
GEMINI_API_KEY = your_gemini_api_key
```
Get Gemini API key from [Google AI Studio](http://aistudio.google.com/) for free.

#### 🤩How to run the software
You need to have 2 terminals running parallelly with the following commands, one is for frontend and the other for backend.

To run frontend, go to `/frontend` folder and do
```
npm run dev
```
To run backend, go to `/backend` folder and do
```
fastapi dev main.py
```

Now the app will be functional on `http://localhost:5173/`. if it's not, check the URL on the frontend terminal.

## Architecture:
![architecture](https://github.com/user-attachments/assets/5dab916a-2ba8-40d9-afed-b52f0cd66c18)

## 💫Built with
* **[FFmpeg](https://ffmpeg.org/)** 
* **[Google Gemini](https://deepmind.google/technologies/gemini/)**
* **[OpenAI Whisper](https://openai.com/index/whisper/)**
* **[scenedetect](https://pypi.org/project/scenedetect/)**
* **[FastAPI](https://fastapi.tiangolo.com/)** 
* **[Vite](https://vite.dev/)**

#

Developed with [Swagat Mitra](https://github.com/swagatmitra22) and [Shreesh R Nair](https://github.com/Shreesh-Nair) in 36 hours for a hackathon. We'll continue shipping more features and iterating 🚀 Send us your feedback on **X** [@_RobinRoy](https://x.com/_RobinRoy), [Discord](https://discord.gg/GSknuxubZK) or via **GitHub** as [Discussions](https://github.com/robinroy03/easyEdits/discussions)/[Issues](https://github.com/robinroy03/easyEdits/issues)/[Pull Requests](https://github.com/robinroy03/easyEdits/pulls).

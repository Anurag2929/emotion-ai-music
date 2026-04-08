import streamlit as st
import numpy as np
import cv2
from deepface import DeepFace
import requests
import random

# 🔐 JAMENDO KEY
JAMENDO_CLIENT_ID = "c5978efb"

st.set_page_config(page_title="Emotion AI Music", page_icon="🎧", layout="centered")

# 🎨 UI
st.markdown("""
<style>
body { background-color: #0b0f1a; }
.title { text-align:center; font-size:36px; font-weight:700; color:white; }
.card { background:#1e293b; padding:15px; border-radius:12px; margin-top:10px; }
.emotion { padding:12px; border-radius:10px; background:#22c55e; color:white; text-align:center; font-size:18px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🎧 Emotion AI Music</div>", unsafe_allow_html=True)

# 🧠 PROPER DEEPFACE USAGE (NO OVER-COMPLEXITY)
def detect_emotion(frame):
    try:
        result = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend="opencv"
        )

        emotion = result[0]['dominant_emotion']

        # minimal correction only
        if emotion in ["fear", "disgust"]:
            emotion = "surprise"

        return emotion

    except:
        return "neutral"

# 🎯 QUERY
def get_query(emotion):
    mapping = {
        "happy": "happy upbeat",
        "sad": "sad piano",
        "angry": "intense rock",
        "neutral": "lofi chill",
        "surprise": "edm party"
    }
    return mapping.get(emotion, "chill music")

# 🎵 JAMENDO + FALLBACK
def fetch_tracks(emotion):
    try:
        url = "https://api.jamendo.com/v3.0/tracks/"
        params = {
            "client_id": JAMENDO_CLIENT_ID,
            "format": "json",
            "limit": 8,
            "namesearch": get_query(emotion),
            "audioformat": "mp31"
        }

        res = requests.get(url, params=params, timeout=3)
        data = res.json()

        tracks = [
            {"name": t["name"], "artist": t["artist_name"], "audio": t["audio"]}
            for t in data.get("results", [])
        ]

        if tracks:
            return tracks

    except:
        pass

    # 🔥 ALWAYS WORKING FALLBACK
    return [
        {
            "name": "Fallback Music",
            "artist": "AI System",
            "audio": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        },
        {
            "name": "Chill Mood",
            "artist": "AI System",
            "audio": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        }
    ]

# 🎭 EMOJI
emoji = {
    "happy": "😄",
    "sad": "😢",
    "angry": "😡",
    "neutral": "😐",
    "surprise": "😲"
}

# STATE
if "tracks" not in st.session_state:
    st.session_state.tracks = []
    st.session_state.index = 0
    st.session_state.last_emotion = None

# 📸 CAMERA
image = st.camera_input("")

if image:
    file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    st.image(frame, use_container_width=True)

    emotion = detect_emotion(frame)

    # 🔄 LOAD MUSIC ONLY WHEN EMOTION CHANGES
    if emotion != st.session_state.last_emotion:
        st.session_state.tracks = fetch_tracks(emotion)
        random.shuffle(st.session_state.tracks)
        st.session_state.index = 0
        st.session_state.last_emotion = emotion

    # 🎭 DISPLAY (NO BUGS NOW)
    st.markdown(
        f"<div class='emotion'>{emoji.get(emotion,'😐')} {emotion.upper()}</div>",
        unsafe_allow_html=True
    )

    # 🎵 PLAYER
    if st.session_state.tracks:
        track = st.session_state.tracks[st.session_state.index]

        st.markdown(f"""
        <div class='card'>
            <h3>{track['name']}</h3>
            <p>{track['artist']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.audio(track["audio"])

    # 🎛 CONTROLS
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏭ Next"):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.tracks)

    with col2:
        if st.button("🔀 Shuffle"):
            random.shuffle(st.session_state.tracks)   # shuffle full list
            st.session_state.index = 0                # start from first

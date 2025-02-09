import speech_recognition as sr
import google.generativeai as genai
import asyncio
import edge_tts
import pygame
import os
import streamlit as st
import sounddevice as sd
import wavio
import numpy as np

voices = ["en-US-JennyNeural", "en-GB-RyanNeural", "zh-CN-XiaoxiaoNeural"]

# Set API KEY
genai.configure(api_key="AIzaSyC9dxcqFEUiowMKZ1WzD7zLVI2PcHW18SY")
# Select the model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

VOICE = voices[0]  # Default voice selection
OUTPUT_FILE = "test_speed.mp3"
DURATION = 5  # Recording time in seconds
SAMPLE_RATE = 44100  # Sample rate

# Memory to maintain the conversation
conversation_history = []

def create_prompt(user_input):
    conversation = "\n".join(conversation_history)
    prompt = f"""
    You are an AI-powered English tutor. Your role is to help users improve their English language skills. Please follow these guidelines:

    1. Respond directly to the user’s query with the appropriate English language assistance (translation, grammar correction, etc.).
    2. If the user’s query is not in English, translate it to English and encourage them to rephrase in English.
    3. If the user asks about grammar or language topics, provide clear explanations and examples.
    4. Be polite and encouraging, gently correcting mistakes.
    5. Encourage users to practice by rephrasing their questions or asking follow-ups.
    6. **Do not respond to queries unrelated to English language learning** (e.g., programming questions, calculations, or general knowledge). Politely redirect them by saying: "Sorry sir, I am here to help with English language skills! Please feel free to ask about grammar, language learning, or English-related topics."
    7. **Stay to the point**. Provide concise answers without unnecessary detail. Focus only on the essential information needed to assist the user with their query.

    Here is the conversation so far:
    {conversation}

    User's latest query: {user_input}
    """
    return prompt

async def amain(TEXT):
    communicator = edge_tts.Communicate(TEXT, VOICE)
    await communicator.save(OUTPUT_FILE)

    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.quit()
    os.remove(OUTPUT_FILE)

# Function to record audio using sounddevice
def record_audio():
    st.write("🎤 Listening... Speak now!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    wavio.write("temp_audio.wav", audio_data, SAMPLE_RATE, sampwidth=2)
    st.write("✅ Recording complete!")

# Function to transcribe recorded audio
def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."

# Streamlit UI
st.title("🎙️ Real-Time English Tutor")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

st.write("Click **Start Chat** to begin a real-time conversation.")

if st.button("Start Chat"):
    st.session_state.chat_active = True

if st.session_state.chat_active:
    while True:
        record_audio()  # Automatically record after each AI response
        text = transcribe_audio()

        if text:
            st.session_state.conversation_history.append(f"User: {text}")
            prompt = create_prompt(text)
            response = model.generate_content(prompt)
            TEXT = response.text if response else "Sorry, I couldn't process that."

            st.session_state.conversation_history.append(f"AI Tutor: {TEXT}")
            # st.write("**AI Tutor:**", TEXT)
            asyncio.run(amain(TEXT))  # Speak the response automatically

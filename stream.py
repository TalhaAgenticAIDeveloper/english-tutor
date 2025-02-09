import speech_recognition as sr
import google.generativeai as genai
import asyncio
import edge_tts
import pygame
import os
import streamlit as st

voices = ["en-US-JennyNeural", "en-GB-RyanNeural", "zh-CN-XiaoxiaoNeural"]

# Set API KEY
genai.configure(api_key="AIzaSyC9dxcqFEUiowMKZ1WzD7zLVI2PcHW18SY")
# Select the model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

VOICE = voices[0]  # Default voice selection
OUTPUT_FILE = "test_speed.mp3"

st.title("🎤 English Tutor - AI Chatbot")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

recognizer = sr.Recognizer()

def create_prompt(user_input):
    conversation = "\n".join(st.session_state.conversation_history)
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
    """Generate speech from text and play it."""
    communicator = edge_tts.Communicate(TEXT, VOICE)
    await communicator.save(OUTPUT_FILE)

    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.quit()
    os.remove(OUTPUT_FILE)

def listen_speech():
    """Capture user's speech input and return the text."""
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.5)
        st.write("Listening... 🎤")
        audio = recognizer.listen(mic)

        try:
            text = recognizer.recognize_google(audio)  # Uses Google Web Speech API
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."

# **Chatbot Loop** - Runs each time user clicks "Start Chat"
if st.button("Start Chat 🎙️"):
    while True:
        # **User Speech Input**
        user_input = listen_speech()

        if user_input.lower() == "exit":
            st.write("Chat ended. Restart to begin again.")
            break

        st.session_state.conversation_history.append(f"User: {user_input}")

        # **AI Response**
        prompt = create_prompt(user_input)
        response = model.generate_content(prompt)
        ai_response = response.text if response else "Sorry, I couldn't process that."

        st.session_state.conversation_history.append(f"AI Tutor: {ai_response}")

        # **Display AI Response**
        st.write("**AI Tutor:**", ai_response)

        # **Text-to-Speech Response**
        asyncio.run(amain(ai_response))

        # Automatically loop back and allow the user to speak again

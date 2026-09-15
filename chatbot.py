
import streamlit as st
from groq import Groq
from gtts import gTTS
import io

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="centered")

client = Groq(api_key="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")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 780px; }
    [data-testid="stChatMessage"] { border-radius: 16px; padding: 0.8rem 1rem; margin-bottom: 0.4rem; }
    h1 { text-align: center; font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Asistente de voz")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "system",
            "content": "Responde de forma breve y directa, en 2 a 4 oraciones como máximo. No des explicaciones largas ni te extiendas con detalles innecesarios, pero sé claro y completo en lo esencial."
        }
    ]

if "ultimo_audio_id" not in st.session_state:
    st.session_state.ultimo_audio_id = None

for msg in st.session_state.mensajes:
    if msg["role"] != "system":
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

def procesar_mensaje(prompt):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Pensando..."):
            respuesta = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=st.session_state.mensajes
            )
            reply = respuesta.choices[0].message.content
        st.markdown(reply)

        tts = gTTS(text=reply, lang="es")
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes.getvalue(), format="audio/mp3")

    st.session_state.mensajes.append({"role": "assistant", "content": reply})

audio = st.audio_input("Graba tu mensaje")
prompt_texto = st.chat_input("O escribe tu mensaje")

if audio and audio.file_id != st.session_state.ultimo_audio_id:
    st.session_state.ultimo_audio_id = audio.file_id
    try:
        transcripcion = client.audio.transcriptions.create(
            file=("audio.wav", audio.read()),
            model="whisper-large-v3-turbo"
        )
        if transcripcion.text.strip():
            procesar_mensaje(transcripcion.text)
        else:
            st.warning("No se detectó voz. Intenta de nuevo.")
    except Exception as e:
        st.error(f"No se pudo procesar el audio: {e}")

elif prompt_texto:
    procesar_mensaje(prompt_texto)
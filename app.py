import streamlit as st
import time
from dotenv import load_dotenv
load_dotenv()
import os
from utils import run_excecuter
from openai import OpenAI
import streamlit as st
import base64


# Creación de cliente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant_id = os.getenv("ASSISTANT_ID")
print("assistant id: ", assistant_id)

# Título de la app
st.title("Asistente de Ventas - Aynitech")

# Logo de la empresa
with open("AYGroup.jpeg", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

    st.sidebar.markdown(
        f"""
        <div style="display:table;margin-top:-20%;margin-left:20%;">
            <img src="data:image/png;base64,{data}" width="202" height="70">
        </div>
        """,
        unsafe_allow_html=True,
    )

# Inicializar historial de chat si no existe en el estado de la sesión
if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes del historial en la aplicación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para mostrar texto con efecto de máquina de escribir
def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

# Aceptar entrada del usuario
if prompt := st.chat_input("Escribir mensaje..."):
    # Agregar mensaje del usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Mostrar mensaje del usuario en el contenedor de mensajes del chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Mostrar respuesta del asistente en el contenedor de mensajes del chat
    with st.chat_message("assistant"):
        # Generar texto por el asistente
        message_box = client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=prompt)
       
        # Ejecutar el run
        run = client.beta.threads.runs.create(
            thread_id = st.session_state.thread_id,
            assistant_id = assistant_id
        )
        # Mostrar spinner y mensaje temporal mientras el asistente responde
        with st.spinner('Aynitech está escribiendo ...'):
            #st.toast('Estamos agradecidos por tu contacto!', icon='🎉')
            run_excecuter(run)
            message_assistant = client.beta.threads.messages.list(thread_id=st.session_state.thread_id).data[0].content[0].text.value
        # Mostrar respuesta del asistente con efecto de máquina de escribir
        typewriter(message_assistant, 50)

    # Agregar respuesta del asistente al historial de chat
    st.session_state.messages.append({"role": "assistant", "content": message_assistant})

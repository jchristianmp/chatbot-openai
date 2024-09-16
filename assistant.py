from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools_list=[
    {
    "type": "function",
    "function": {
      "name": "registrar_datos_gsheets",
      "description": "Esta herramienta servirá para registrar al nuevo lead en google sheets",
      "parameters": {
        "type": "object",
        "properties": {
          "nombre_lead":{
              "type":"string",
              "description":"El nombre del lead interesado"
          },
          "correo_lead":{
              "type":"string",
              "description":"correo del lead interesado"
          },
          "servicio_de_interes":{
              "type":"string",
              "description":"Servicio del cual el lead está interesado"
          }
        },
        "required": ["nombre_lead","correo_lead","servicio_de_interes"]
      }
    }
},
    {
    "type": "function",
    "function": {
      "name": "enviar_correo_lead",
      "description": "Función utilizada para enviar un correo electrónico al lead interesado informándole que un asesor de ventas se contactará con él",
      "parameters": {
        "type": "object",
        "properties": {
          "nombre_lead":{
              "type":"string",
              "description":"El nombre del lead interesado"
          },
          "correo_lead":{
              "type":"string",
              "description":"correo del lead interesado"
          },
          "mensaje_para_lead":{
              "type":"string",
              "description":"Mensaje generado por el asistente para enviar al lead por correo electrónico"
          }
        },
        "required": ["nombre_lead","correo_lead","mensaje_para_lead"]
      }
    }
},
     {
    "type": "function",
    "function": {
      "name": "enviar_whatsapp_asesor",
      "description": "Funcion para enviar un mensaje de whatsapp al asesor indicándole que se ha agregado un interesado a la base de datos",
      "parameters": {
        "type": "object",
        "properties": {
          "nombre_asesor":{
              "type":"string",
              "description":"El nombre del asesor elegido para atender al lead interesado"
          },
          "numero_whatsapp_asesor":{
              "type":"string",
              "description":"número de whatsapp del asesor elegido para atender al lead interesado"
          },
          "mensaje_asesor":{
              "type":"string",
              "description":"Mensaje generado por el asistente para el asesor"
          }
        },
        "required": ["nombre_asesor","numero_whatsapp_asesor","mensaje_asesor"]
      }
    }
},
 {"type":"file_search"}
]

# Creamos un vector Store para guardar la base de conocimientoas para el asistente
vector_store = client.beta.vector_stores.create(name="Información_vector1")

# Leemos los archivos para subir a OpenAI
file_paths = ["/Project_Chatbot_OpenAI/chatbot-aynitech/src/AT_2021.pdf",]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

print(file_batch.status)  # estado
print(file_batch.file_counts) # conteo de archivos


assistente = client.beta.assistants.create(
    name="Asistente Aynitech 2024",
    instructions="""

    Eres un asistente de ventas de Aynitech SAC, me ayudarás a atender las consultas de los clientes interesados en algún servicio. Debes seguir las siguientes instrucciones:

    1. Tono de Respuesta:

      - Responde a los interesados con un tono amigable y profesional.
      - Usa la información proporcionada en la base de conocimiento para responder a sus consultas.

    2. Solicitud de Contacto con un Asesor de Ventas:

      - Si un interesado solicita contactarse con un asesor de ventas para más detalles, ejecuta la función registrar_datos_gsheets.
      - Para ejecutar esta función, necesitas pedir y registrar los siguientes datos del interesado:
          - Nombre completo
          - Correo electrónico
          - Servicio de interés

      - La función 'registrar_datos_gsheets' devolverá 'true' si el registro es exitoso, y 'false' si el correo electrónico no existe o no está validado.

    3. Contacto con el Asesor de Ventas:

      - Si 'registrar_datos_gsheets' devuelve true, envía un mensaje al asesor de ventas al número de WhatsApp utilizando la función 'enviar_whatsapp_asesor'.
      - El mensaje debe mencionar que hay un posible comprador interesado y que debe ser contactado urgentemente. Incluye el nombre del interesado y su correo electrónico en el mensaje.

    4. Confirmación al Interesado:

      - Si el registro del interesado en la base de datos se completa satisfactoriamente ('registrar_datos_gsheets' devuelve true), envía un correo electrónico al interesado utilizando la función 'enviar_correo'.
      - En el correo, menciona que un asesor de ventas se contactará muy pronto con él. Proporciona también información detallada del programa de interés.
      - Recuerda ser claro y preciso en todos los mensajes y asegurar que toda la información relevante sea comunicada adecuadamente.

    """,
    model="gpt-4-turbo-preview",
    tools=tools_list,

    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)
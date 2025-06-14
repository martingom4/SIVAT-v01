from fastapi.responses import PlainTextResponse
from app.config import VERIFY_TOKEN, redis_client
from app.models.redis_model import crear_usuario, actualizar_usuario, obtener_usuario, eliminar_usuario, verificar_usuario
from app.services.message_handler import mensaje_bienvenida
from app.logic.flow import manejar_flujo
import redis
import os




def verify_webhook(request):
    mode = request.query_params.get("hub.mode") # Obtiene el modo de verificación
    token = request.query_params.get("hub.verify_token") # Obtiene el token de verificación
    challenge = request.query_params.get("hub.challenge") # Obtiene el desafío de verificación
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200) # Responde con el desafío si la verificación es exitosa
        return PlainTextResponse("Forbidden", status_code=403) # Responde con Forbidden si la verificación falla


async def process_incoming_message(data: dict):
    try:
        value = data['entry'][0]['changes'][0]['value']

        if "messages" in value:
            message = value['messages'][0]
            wa_id = message['from']
            text = message['text']['body'].strip()

            print(f"📩 Mensaje recibido de {wa_id}: '{text}'")

            # Crear usuario si no existe
            if not verificar_usuario(redis_client, wa_id):
                crear_usuario(redis_client, wa_id, paso=0.0)
                return mensaje_bienvenida(wa_id)

            # Delegar al manejador de flujo
            return manejar_flujo(redis_client, wa_id, text)

        else:
            print("📥 Evento recibido no es un mensaje de texto.")
            return {"status": "ignored", "message": "Evento no procesado."}

    except Exception as e:
        print(f"❌ Error procesando el mensaje: {e}")
        return {"status": "error", "message": str(e)}


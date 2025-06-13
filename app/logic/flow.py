# Se define los pasos del flujo conversacional para evitarl el uso de if anidados

import re
from datetime import datetime
from app.config import redis_client
from app.models.redis_model import crear_usuario, actualizar_usuario, obtener_usuario, eliminar_usuario, verificar_usuario
from app.client.whatsapp_api import send_text_message
from app.services.message_handler import mensaje_menu, mensaje_fiebre_2_5, mensaje_fiebre_2 ,mensaje_debug, mensaje_fiebre_final

#posteriormente despues de dar el mensaje de bienvendia hace este paso, donde se recolecta el nombre y la cedula y se guarda en redis
def paso_0(wa_id, texto):
    try:
        validador = re.match(r"(.*)\s(\d{5,})$", texto.strip())
        if validador:
            nombre = validador.group(1).strip()
            cedula = validador.group(2)
        else:
            send_text_message(wa_id, "❌ Formato incorrecto. Usa: Nombre Apellido Cédula (sin guiones).")
            return {"status": "error", "message": "Formato inválido"}
        actualizar_usuario(redis_client, wa_id, nombre=nombre, cedula=cedula, paso=1.0)
        mensaje_menu(wa_id)
        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Error paso_0: {e}")
        send_text_message(wa_id, "❌ Hubo un error procesando tus datos. Intenta nuevamente.")
        return {"status": "error", "message": str(e)}

# esta es el paso donde se pregtuna al usuario el motivo de su consulta
def paso_1(wa_id, texto):
    actualizar_usuario(redis_client, wa_id, motivo=texto) # este paso no debe de ser el primero en realidad
    if texto == "1":
        actualizar_usuario(redis_client, wa_id, paso = 2.0)
        mensaje_fiebre_2(wa_id)
        return {"status": "ok", "message": "Fiebre registrada, solicitando fecha de síntomas."}
    elif texto == "2":
        actualizar_usuario.hset(wa_id, "paso", 6)
        return send_text_message(wa_id, "🐄 ¿Qué especie es el animal? (Ej: vaca, cerdo, perro...)")
    elif texto == "3":
        actualizar_usuario.hset(wa_id, "paso", 10)
        return send_text_message(wa_id, "🦝 ¿Qué animal silvestre observaste?")
    elif texto == "4":
        actualizar_usuario.hset(wa_id, "paso", 14)
        return send_text_message(wa_id, "🧪 En breve, un miembro del equipo se comunicará contigo.")
    elif texto == "5":
        actualizar_usuario.hset(wa_id, "paso", 15)
        return send_text_message(wa_id, "📝 Por favor, indica brevemente tu consulta.")
    else:
        return send_text_message(wa_id, "Por favor, elige una opción del 1 al 5.")

def paso_2(wa_id, texto):
    try:
        fecha = datetime.strptime(texto.strip(), "%d-%m-%Y")
        if fecha > datetime.now():
            mensaje_debug(wa_id, "❌ Fecha futura no válida. Por favor, ingresa una fecha pasada o presente.")
            return {"Status": "error", "message": "Fecha futura no válida"}

        fecha = fecha.strftime("%d-%m-%Y")  # Formatear la fecha a DD-MM-AAAA
        actualizar_usuario(redis_client, wa_id, fecha_sintomas = fecha, paso = 2.5 )
        mensaje_fiebre_2_5(wa_id)

        return {"status": "ok", "message": "Fecha de síntomas registrada, solicitando otros síntomas."}

    except Exception as e:
        print(f"❌ Error al procesar la fecha: {e}")
        return {"status": "error"}

def paso_2_5(wa_id, texto):
    sintomas = texto.strip()
    try:
        if not sintomas:
            mensaje_debug(wa_id, "❌ No se ingresaron síntomas. Por favor, ingresa al menos un síntoma.")
            return {"status": "error", "message": "No se ingresaron síntomas"}
        sintomas_lista = [s.strip() for s in sintomas.split(",") if s.strip()]  # Limpiar y separar síntomas
        sintomas_str = ", ".join(sintomas_lista)  # Convertir lista a string
        actualizar_usuario(redis_client , wa_id , sintomas= sintomas_str, paso = 3.0)
        mensaje_fiebre_final(wa_id)
        eliminar_usuario(redis_client, wa_id)  # Eliminar usuario después de completar el flujo
        return {"status": "ok", "message": "Síntomas registrados, enviando mensaje final."}
    except Exception as e:
        print(f"❌ Error al procesar los síntomas: {e}")
        return {"status": "error", "message": str(e)}


def paso_3(wa_id, texto):
    actualizar_usuario.hset(wa_id, "otros_sintomas", texto)
    actualizar_usuario.hset(wa_id, "paso", 4)
    return send_text_message(wa_id, "📞 Gracias por la información. Un médico se comunicará contigo pronto.")

# tabla de decisiones
pasos_handlers = {
    0.0: paso_0,
    1.0: paso_1,
    2.0: paso_2,
    2.5: paso_2_5,
    3.0: paso_3
}


# --- función manejar_flujo agregada al final del archivo ---
def manejar_flujo(redis_client, wa_id, texto):
    usuario = obtener_usuario(redis_client, wa_id)
    paso_actual = float(usuario.get("paso", 0.0))

    handler = pasos_handlers.get(paso_actual)
    if handler:
        return handler(wa_id, texto)
    else:
        send_text_message(wa_id, "⚠️ Ha ocurrido un error. Por favor, intenta nuevamente más tarde.")
        return {"status": "error", "message": f"No hay handler definido para el paso {paso_actual}"}

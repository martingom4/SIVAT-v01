# aca vamos a poner los mensaje que se tienne que enviar al usuario
from app.client.whatsapp_api import send_text_message


def mensaje_bienvenida(wa_id:str):
    """
    Envía un mensaje de bienvenida al usuario.
    """
    message = "👋 ¡Hola! Soy SIVAT. Bienvenido al Sistema Integrado de Alerta Temprana y Respuesta a Brotes de Enfermedades Zoonóticas Emergentes. Por favor, indícanos tu NOMBRE COMPLETO y tu CÉDULA sin guiones (Ej.: 80000000)."
    send_text_message(wa_id, message)

def mensaje_menu(wa_id:str):
    message = "✅ Muchas gracias. ¿Cuál es el motivo de tu consulta? \n 1️⃣ Tengo fiebre o un familiar con fiebre \n 2️⃣ He observado un animal doméstico enfermo o muerto \n 3️⃣ He observado un animal silvestre enfermo o muerto \n 4️⃣ Consulta de resultados de laboratorio \n 5️⃣ Otro motivo"
    return send_text_message(wa_id, message)

def mensaje_fiebre_2(wa_id:str):
    message = "¿Desde qué fecha tú o tu familiar presentan síntomas? (Formato: DD-MM-AAAA)"
    return send_text_message(wa_id, message)

def mensaje_fiebre_2_5(wa_id:str):
    message = "¿Qué otros síntomas presentan? Puedes listar varios (Ej.: dolor de cabeza, diarrea, vómitos, mareos, etc.)"
    return send_text_message(wa_id, message)

def mensaje_fiebre_final(wa_id:str):
    message = "📞 Gracias por la información. Un médico del equipo SIVAT se comunicará contigo lo antes posible para evaluar tu estado de salud."
    return send_text_message(wa_id, message)


def mensaje_debug(wa_id:str, message = str):
    return send_text_message(wa_id, message)

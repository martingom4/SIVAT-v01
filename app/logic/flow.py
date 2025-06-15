# Se define los pasos del flujo conversacional para evitarl el uso de if anidados

import re
from datetime import datetime
from app.config import redis_client
from app.models.redis_model import crear_usuario, actualizar_usuario, obtener_usuario, eliminar_usuario, verificar_usuario
from app.client.whatsapp_api import send_text_message
from app.services.message_handler import mensaje_menu, mensaje_fiebre_2_5, mensaje_fiebre_2 ,mensaje_debug, mensaje_fiebre_final, mensaje_animal_domestico_3, mensaje_animal_domestico_3_5, mensaje_animal_domestico_4_0, mensaje_animal_domestico_final, mensaje_animal_silvestre_5_0,mensaje_animal_silvestre_5_5,  mensaje_animal_silvestre_6_0, mensaje_animal_silvestre_final, mensaje_resultados_laboratorio,mensaje_otro_motivo_7_0

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
        actualizar_usuario(redis_client, wa_id, paso = 3.0)
        mensaje_animal_domestico_3(wa_id)
        return {"status": "ok", "message": "Animal doméstico registrado, solicitando especie."}
    elif texto == "3":
        actualizar_usuario(redis_client , wa_id, paso = 5.0)
        mensaje_animal_silvestre_5_0(wa_id)
        return {"status": "ok", "message": "Animal silvestre registrado, solicitando descripción."}
    elif texto == "4":
        mensaje_resultados_laboratorio(wa_id)
        return {"status": "ok", "message": "Resultados de laboratorio solicitados."}

    elif texto == "5":
        actualizar_usuario(redis_client, wa_id, paso=7.0)
        mensaje_otro_motivo_7_0(wa_id)
        return {"status": "ok", "message": "Otro motivo registrado, solicitando consulta."}
    else:
        send_text_message(wa_id, "Por favor, elige una opción del 1 al 5.")
        return {"status": "error", "message": "Opción inválida. Por favor, ingresa una opción válida."}

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
    try:
        sintomas = texto.strip()
        if not sintomas:
            mensaje_debug(wa_id, "❌ No se ingresaron síntomas. Por favor, ingresa al menos un síntoma.")
            return {"status": "error", "message": "No se ingresaron síntomas"}
        sintomas_lista = [s.strip() for s in sintomas.split(",") if s.strip()]  # Limpiar y separar síntomas
        sintomas_str = ", ".join(sintomas_lista)  # Convertir lista a string
        actualizar_usuario(redis_client , wa_id , sintomas= sintomas_str) # no hay necesidad de ponerle mas pasos
        mensaje_fiebre_final(wa_id)
        eliminar_usuario(redis_client, wa_id)  # Eliminar usuario después de completar el flujo
        return {"status": "ok", "message": "Síntomas registrados, enviando mensaje final."}
    except Exception as e:
        print(f"❌ Error al procesar los síntomas: {e}")
        return {"status": "error", "message": str(e)}

#Flujo 1 terminado

# Flujo 2: Animal doméstico
def paso_3(wa_id, texto):
    # se valida que opcion se ingreso
    try:
        texto = texto.strip().lower()
        if not texto:
            mensaje_debug(wa_id, "❌ No se ingresó la especie del animal. Por favor, intenta nuevamente.")
            return {"status": "error", "message": "No se ingresó la especie del animal"}
        animal_lista = [s.strip() for s in texto.split(",") if s.strip()]  # Limpiar y separar especies
        especie_animal = ", ".join(animal_lista)  # Convertir lista a string
        actualizar_usuario(redis_client, wa_id,especie_animal=especie_animal, paso=3.5)
        mensaje_animal_domestico_3_5(wa_id)
        return {"status" , "ok"}
    except Exception as e:
        return{"status": "error", "message": "Opción inválida. Por favor, ingresa una opción válida."}


def paso_3_5(wa_id, texto):
    try:
        fecha = datetime.strptime(texto.strip(), "%d-%m-%Y")
        if fecha > datetime.now():
            mensaje_debug(wa_id, "❌ Fecha futura no válida. Por favor, ingresa una fecha pasada o presente.")
            return {"Status": "error", "message": "Fecha futura no válida"}
        fecha = fecha.strftime("%d-%m-%Y")
        actualizar_usuario(redis_client, wa_id , fecha_evento = fecha, paso = 4.0)
        mensaje_animal_domestico_4_0(wa_id)
        return {"status": "ok", "message": "Fecha del evento registrada, enviando mensaje final."}
    except Exception as e:
        print(f"❌ Error al procesar los síntomas: {e}")
        return {"status": "error", "message": str(e)}

def paso_4(wa_id,texto):
    try:
        texto = texto.strip().lower()
        if texto not in ["si", "no"]:
            mensaje_debug(wa_id, "❌ Respuesta inválida. Por favor, responde con 'Sí' o 'No'.")
            return {"status": "error", "message": "Respuesta inválida"}

        otros_animales = "Sí" if texto == "sí" else "No" # convertimos de texto a booleano
        actualizar_usuario(redis_client, wa_id, otros_animales=otros_animales)
        mensaje_animal_domestico_final(wa_id)
         # Enviamos el mensaje final y eliminamos al usuario
        eliminar_usuario(redis_client, wa_id)  # Eliminar usuario después de completar el flujo
        return {"status": "ok", "message": "Información registrada y usuario eliminado."}

    except Exception as e:
        print(f"❌ Error al procesar la respuesta: {e}")
        return {"status": "error", "message": str(e)}

def paso_5(wa_id, texto):
    try:
        text = texto.strip()
        if not text:
            mensaje_debug(wa_id, "❌ No se ingresó la consulta. Por favor, intenta nuevamente.")
            return {"status": "error", "message": "No se ingresó la consulta"}
        # Guardar la consulta libre en Redis
        actualizar_usuario(redis_client, wa_id, especie_silvestre=text, paso=5.5)
        mensaje_animal_silvestre_5_5(wa_id)
        return {"status": "ok", "message": "Consulta registrada, enviando mensaje final."}
    except Exception as e:
        print(f"❌ Error al procesar la respuesta: {e}")
        return {"status": "error", "message": str(e)}

def paso_5_5(wa_id, texto):
    try:
        text = texto.strip()
        if not text:
            mensaje_debug(wa_id, "❌ No se ingresó ningún texto. Por favor, intenta nuevamente.")
            return {"status": "error", "message": "Texto vacío"}

        if not contiene_fecha_valida(text):
            mensaje_debug(wa_id, "❌ La fecha ingresada no es válida o no está en el formato DD-MM-AAAA. Intenta nuevamente.")
            return {"status": "error", "message": "Fecha no válida"}

        # Guardar el texto tal como llega
        actualizar_usuario(redis_client, wa_id, lugar_fecha_observacion=text, paso=6)
        mensaje_animal_silvestre_6_0(wa_id)
        return {"status": "ok", "message": "Lugar y fecha registrados, finalizando caso."}

    except Exception as e:
        print(f"❌ Error al procesar la respuesta: {e}")
        return {"status": "error", "message": str(e)}

def paso_6(wa_id, texto):
    try:
        texto = texto.strip().lower()
        if texto not in ["si", "no"]:
            mensaje_debug(wa_id, "❌ Respuesta inválida. Por favor, responde con 'Sí' o 'No'.")
            return {"status": "error", "message": "Respuesta inválida"}

        otros_animales = "Sí" if texto == "sí" else "No" # convertimos de texto a booleano
        actualizar_usuario(redis_client, wa_id, otros_animales=otros_animales)
        mensaje_animal_silvestre_final(wa_id)

         # Enviamos el mensaje final y eliminamos al usuario
        eliminar_usuario(redis_client, wa_id)  # Eliminar usuario después de completar el flujo
        return {"status": "ok", "message": "Información registrada y usuario eliminado."}

    except Exception as e:
        print(f"❌ Error al procesar la respuesta: {e}")
        return {"status": "error", "message": str(e)}

def paso_7_0(wa_id, texto ):
    try:
        texto = texto.strip()
        if not texto:
            mensaje_debug(wa_id, "❌ No se ingresó la consulta. Por favor, intenta nuevamente.")
            return {"status": "error", "message": "No se ingresó la consulta"}
        actualizar_usuario(redis_client, wa_id, consulta_libre=texto)
         # Enviamos el mensaje final y eliminamos al usuario
        mensaje_debug(wa_id, "Gracias por la informacion, un miembro del equipo SIVAT se pondrá en contacto contigo.")
        eliminar_usuario(redis_client, wa_id)  # Eliminar usuario después de completar el flujo
    except Exception as e:
        print(f"❌ Error al procesar la respuesta: {e}")
        return {"status": "error", "message": str(e)}



# tabla de decisiones
pasos_handlers = {
    0.0: paso_0,
    1.0: paso_1,
    2.0: paso_2,
    2.5: paso_2_5,
    3.0: paso_3,
    3.5: paso_3_5,
    4.0: paso_4,
    5.0: paso_5,
    5.5: paso_5_5,
    6.0: paso_6,
    7.0: paso_7_0

}

#TODO pasar a carpeta utils
def contiene_fecha_valida(texto):
    patron_fecha = r'\b(\d{2})-(\d{2})-(\d{4})\b'
    coincidencias = re.findall(patron_fecha, texto)

    for dia, mes, anio in coincidencias:
        try:
            datetime.strptime(f"{dia}-{mes}-{anio}", "%d-%m-%Y")
            return True
        except ValueError:
            continue
    return False

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

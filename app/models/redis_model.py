#Modelos de Redis para llenar con los datos de los usuarios entrantes

'''
logica para uso de redis

set(key, value)  # Establece un valor en Redis
get(key)  # Obtiene un valor de Redis
del(key)  # Elimina un valor de Redis
# Ejemplo de uso:
redis_client.set("test_key", "test_value")  # Establece un valor
redis_client.get("test_key")  # Obtiene el valor establecido
redis_client.delete("test_key")  # Elimina el valor establecido
'''

def crear_usuario(redis_client, wa_id: str, **datos):
    # Valores por defecto
    defaults = {
    # Identificación básica
    "nombre": "",
    "cedula": "",
    "paso": 0.0,              # Paso actual en el flujo
    "motivo": "",           # 1 a 5 (motivo seleccionado por el usuario)

    # Flujo 1️⃣ - Síntomas en humanos
    "fecha_sintomas": "",   # DD-MM-AAAA
    "sintomas": "",         # Lista en string: "vómitos, mareos, dolor de cabeza"

    # Flujo 2️⃣ - Animal doméstico
    "especie_animal": "",   # Ej.: "vaca, perro"
    "fecha_evento": "",     # Fecha en que se observó el animal enfermo/muerto
    "otros_animales": "",   # Sí / No

    # Flujo 3️⃣ - Animal silvestre
    "especie_silvestre": "",   # Descripción del animal silvestre
    "lugar_fecha": "",         # Lugar + fecha del avistamiento
    "otros_silvestres": "",    # Sí / No

    # Flujo 5️⃣ - Otro motivo
    "consulta_libre": "",      # Texto libre ingresado por el usuario
}


    # Sobrescribir con los valores que vengan por parámetro
    defaults.update(datos)
    # Guardar en Redis
    redis_client.hset(wa_id, mapping=defaults)

def actualizar_usuario(redis_client, wa_id: str, **datos):
    redis_client.hset(wa_id, mapping=datos)

def obtener_usuario(redis_client, wa_id: str) -> dict:
    return redis_client.hgetall(wa_id)

def eliminar_usuario(redis_client, wa_id: str):
    redis_client.delete(wa_id)

def verificar_usuario(redis_client, wa_id: str) -> bool:
    return redis_client.exists(wa_id) > 0


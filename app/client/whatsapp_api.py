# whatsapp_api.py
import httpx
from app.config import ACCESS_TOKEN, PHONE_NUMBER_ID, API_URL

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


def send_text_message(to_number: str, message: str):
    url = f"{API_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }

    response = httpx.post(url, headers=HEADERS, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)
    return response

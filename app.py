import os
import time
import threading
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from bot_logic import BotWhatsApp

# Cargar variables de entorno (SID y Token)
load_dotenv()

app = Flask(__name__)
bot = BotWhatsApp()

# Configuración de Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
twilio_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+5491173739122')

def monitorear_timeouts():
    """Hilo que corre en paralelo revisando inactividad cada 30 segundos."""
    while True:
        try:
            proactivos = bot.verificar_timeouts()
            for telefono, mensaje in proactivos:
                print(f"DEBUG: Enviando recordatorio a {telefono}")
                client.messages.create(
                    body=mensaje,
                    from_=twilio_number,
                    to=telefono
                )
        except Exception as e:
            # Silenciamos errores de límite para no llenar la terminal
            if "exceeded the 50 daily messages limit" not in str(e):
                print(f"Error en monitoreo: {e}")
        
        time.sleep(30)

# Iniciar el hilo de monitoreo
monitor_thread = threading.Thread(target=monitorear_timeouts, daemon=True)
monitor_thread.start()

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    # Obtener el mensaje y el remitente
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    try:
        # Procesar lógica del bot
        respuesta_bot = bot.procesar_mensaje(sender_number, incoming_msg)
    except Exception as e:
        print(f"ERROR: {e}")
        respuesta_bot = "Ups, tuve un error interno. Escribí MENU para reiniciar. 😅"
    
    # Crear respuesta TwiML
    resp = MessagingResponse()
    resp.message(respuesta_bot)
    
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(port=5000, debug=True) # Volvemos a True para ver errores en tiempo real

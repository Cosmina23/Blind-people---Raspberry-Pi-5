import asyncio
import websockets
import json
from textToSpeech import speak_text
from voiceToText import recognize_speech

current_app = None

async def autentificare():
    speak_text("Buna, ai deja cont?")
    cont = await recognize_speech()
    print(f"Ai cont? : {cont}")
    if not cont :
        print("Nu s-a inteles raspunsul")
        await send_message("Eroare: nu am inteles raspunsul")
        return
    await send_message(f'Cont existent: {cont}')

    speak_text("te rog sa imi spui numele de utilizator")
    name = await recognize_speech()
    print(f"Nume preluat: {name}")
    if not name:
        print("Numele nu a fost recunoscut corect")
        await send_message("Eroare: Nu am recunoscut numele.")
        return
    await send_message(f'Nume: "{name}"')

    speak_text("Te rog sa imi spui codul pentru autentificare format doar din cifre")
    code = await recognize_speech()
    print(f"Cod preluat: {code}")
    if not code:
        print("Codul nu a fost recunoscut corect")
        await send_message("Eroare: Nu am recunoscut codul.")
        return
    await send_message(f'Cod: "{code}"')

    speak_text(f"Vrei sa te conectezi cu numele {name}?")
    conectare_ok = await recognize_speech()
    print(f'Credentiale bune = {conectare_ok}')
    if conectare_ok.lower() =="da" :
        await send_message(f'Credentiale bune: {conectare_ok}')
        speak_text("Te rog sa astepti cateva secunde")
        response = await receive_message_from_app()
    else:
        speak_text("Reintroduce credentialele de conectare")

async def handle_connection(websocket, path=None):
    global current_app
    
    if current_app:
        await current_app.close()
        print("Conexiune curată / Aplicație anterioară deconectată")

    current_app = websocket
    print("Conexiune nouă stabilită")

    try:
        print("Aștept comenzile utilizatorului...")
        await autentificare()

        while True:
            message = await websocket.recv()
            print(f"Mesaj primit: {message}")

            try:
                data = json.loads(message)
                if data.get("message") == "logout" or data.get("message") == "user logout":
                    speak_text("Utilizatorul s-a deconectat")
                    print("Utilizatorul s-a deconectat")
                    break
                else:
                    print(f"Mesaj necunoscut: {data}")
            except json.JSONDecodeError:
                print(f"Mesaj invalid: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Conexiune închisă din cauza unei erori: {e}")
    except Exception as e:
        print(f"A apărut o eroare necunoscută: {e}")
    finally:
        current_app = None


async def receive_message_from_app():
    if current_app:
        message = await current_app.recv()
        print(f"Mesaj primit de la aplicație: {message}")
        return message

async def send_message(message):
    if current_app:
        await current_app.send(json.dumps({"message": message}))
        print(f"Trimis la aplicație: {message}")
    else:
        print("Nicio aplicație conectată")

async def start_websocket_server():
    print("Începem serverul WebSocket...")
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print("Server WebSocket pornit pe portul 8765")

    try:
        # Ține serverul activ la nesfârșit
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Serverul WebSocket a fost anulat.")
        server.close()
        await server.wait_closed()


import websockets
import json
import asyncio
from src.takeCredentials import autentificare, reset_credentials
from src.navigator_maps import obtine_ruta

current_app = None
last_location = None

async def handle_connection(websocket, path=None):
    global current_app
    global last_location
    if current_app:
        await current_app.close()
        print("Conexiune curată / Aplicație anterioară deconectată")

    current_app = websocket
    print("Conexiune nouă stabilită")

    try:
        print("Aștept comenzile utilizatorului...")
        await autentificare(websocket)

        while True:
            message = await websocket.recv()
            print(f"Mesaj primit: {message}")

            try:
                data = json.loads(message)
                if data.get("message") == "logout" or data.get("message") == "user logout":
                    print("Utilizatorul s-a deconectat")
                    reset_credentials()
                    break

                msg_type = data.get("type")

                if msg_type == "location" :
                    last_location = (data.get("lat"), data.get("lng"))
                    print(f"Ultima locatie actualizata: {last_location}")
                elif msg_type == "searchedLocation":
                    if last_location:
                        start = last_location
                        end = (data.get("lat"), data.get("lng"))
                        print(f"Calculam ruta de la start la finish")

                        indicatii, coordonate_ruta = obtine_ruta(start,end)

                        # for indicatie in indicatii : 
                        #     await websocket.send(json.dumps({"message_indicatie: ": indicatie}))

                        with open("indicaii_ruta.txt", "w") as f :
                            for indicatie in indicatii : 
                                f.write(indicatie+"\n")
                        print(f"Indicatii salvate in fisierul: indicaii_ruta.txt")

                        await websocket.send(json.dumps({
                            "type" : "ruta",
                            "coordonate" : [{"latitude": lat, "longitude": lng} for lat, lng in coordonate_ruta]
                        }))

                        print(f"S-au trimis coordonatele la aplicatie")

                else: print(f"Mesaj necunoscut: {data}")
            except json.JSONDecodeError:
                print(f"Mesaj invalid: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Conexiune închisă din cauza unei erori: {e}")
    except Exception as e:
        print(f"A apărut o eroare necunoscută: {e}")
    finally:
        current_app = None


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



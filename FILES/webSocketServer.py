import websockets
import json
import asyncio
from src.takeCredentials import autentificare, reset_credentials
from src.navigator_maps import obtine_ruta
from src.indicatioRoutes import comenzi_deplasare
from textToSpeech import speak_text
from voiceToText import recognize_speech
from src.indicatioRoutes import geocode_adresa
# import openrouteservice


current_app = None
last_location = None
location_queue = asyncio.Queue()

ORS_API_KEY = "5b3ce3597851110001cf62483ed29d9e4b9b47a58f40e20891efb908"
# client = openrouteservice.Client(key=ORS_API_KEY)


async def handle_connection(websocket, path=None):
    global current_app
    global last_location

    if current_app:
        await current_app.close()
        print("Conexiune curată / Aplicație anterioară deconectată")

    current_app = websocket
    print("Conexiune nouă stabilită")

    # try:
    #     print("Aștept comenzile utilizatorului...")
    #     await autentificare(websocket)

    #     while True:
    #         message = await websocket.recv()
    #         print(f"Mesaj primit: {message}")

    #         try:
    #             data = json.loads(message)

    #             if data.get("message") in ["logout", "user logout"]:
    #                 print("Utilizatorul s-a deconectat")
    #                 reset_credentials()
    #                 break

    #             msg_type = data.get("type")

    #             if msg_type == "location":
    #                 last_location = (data.get("lat"), data.get("lng"))
    #                 print(f"Ultima locație actualizată: {last_location}")
    #                 await location_queue.put(data)  

    #             elif msg_type == "searchedLocation":
    #                 if last_location:
    #                     start = last_location
    #                     # end = (data.get("lat"), data.get("lng"))
    #                     speak_text('Spuneti adresa unde doriti sa ajungeti')
    #                     destinatie = await recognize_speech()
    #                     print(f'DESTINATIE: {destinatie}')
    #                     opriri = []

    #                     # speak_text('Vreți să faceți opriri pe drum?')
    #                     # raspuns = await recognize_speech()
    #                     # print(f'OPRIRI? Raspusn primit: {raspuns}')

    #                     # if raspuns.lower() in ["da", "sigur", "ok", "vreau", "desigur"]:
    #                     #     speak_text('Cate opriri vreti sa faceti?')
    #                     #     nr_opriri = await recognize_speech()
    #                     #     try:
    #                     #         nr_opriri = int(''.join(filter(str.isdigit, nr_opriri_text)))
    #                     #     except ValueError:
    #                     #         speak_text("Nu am înțeles numărul de opriri. Vom continua fără opriri.")
    #                     #         nr_opriri = 0
                            

    #                     end = await geocode_adresa(destinatie)

    #                     #adauga buton cand apasa pe el sa fie ascultata locatia unde doreste sa ajunga 
    #                     if not end:
    #                         speak_text('Locatia nu a fost identificata')
    #                         return

    #                     print(f"Calculăm ruta de la start la finish...")

    #                     #indicatii, coordonate_ruta, durata = obtine_ruta_ors(start, end, ORS_API_KEY)

    #                     #speak_text(f'Traseul pana la destinatie dureaza {durata} minute')
    #                     # speak_text('Vrei sa faic opriri pe drum?')
    #                     # raspuns = await recognize_speech()

    #                     indicatii, coordonate_ruta, durata_traseu = obtine_ruta(start,end)
    #                     speak_text(f'Traseul pana la destinatie dureaza aproximativ {durata_traseu} minute')

    #                     with open("indicatii_ruta.txt", "w") as f:
    #                         for indicatie in indicatii:
    #                             f.write(indicatie + "\n")
    #                     # print("Indicatii salvate îi indicatii_ruta.txt")

    #                     #salvare coordonate
    #                     with open("coordonate_ruta.json", "w") as f:
    #                         json.dump(
    #                             [{"latitude": lat, "longitude": lng} for lat, lng in coordonate_ruta],
    #                             f,
    #                             indent=2
    #                         )
    #                     # print("Coordonatele salvate în coordonate_ruta.json")

    #                     # Obținem numele locației de start și final 
    #                     # try:
    #                     #     reverse_end = client.pelias_reverse(location=[end[1], end[0]])
    #                     #     nume_end = reverse_end['features'][0]['properties'].get('label', 'Locatie necunoscuta')
    #                     # except Exception as e:
    #                     #     print("Eroare la reverse geocoding:", e)
    #                     #     nume_end = "Locatie necunoscuta"


    #                     await websocket.send(json.dumps({
    #                         "type": "ruta",
    #                         "coordonate": [{"latitude": lat, "longitude": lng} for lat, lng in coordonate_ruta]
    #                     }))
    #                     print("Coordonatele au fost trimise către aplicație")

    #                     #date trimise pentru salvare in tabelul rute din baza de date
    #                     await websocket.send(json.dumps({
    #                         "type": "traseu_nou",
    #                         "locatie_start_lat": start[0],
    #                         "locatie_start_lng": start[1],
    #                         "locatie_end_lat": end[0],
    #                         "locatie_end_lng": end[1],
    #                         "opriri": [] 
    #                     }))
    #                     print("TRIMIS TRASEU NOU !!!!!!!!!!!!!!!")

                       
    #                     asyncio.create_task(comenzi_deplasare(location_queue))

    #             else:
    #                 print(f"Mesaj necunoscut: {data}")

    #         except json.JSONDecodeError:
    #             print("Mesaj JSON invalid")

    try:
        print("Aștept comenzile utilizatorului...")
        await autentificare(websocket)

        # Așteptăm locația curentă (prima locație trimisă)
        while last_location is None:
            message = await websocket.recv()
            try:
                data = json.loads(message)
                if data.get("type") == "location":
                    last_location = (data.get("lat"), data.get("lng"))
                    await location_queue.put(data)
                    print(f"Locație inițială setată: {last_location}")
            except:
                continue

        # După ce avem locația, începem interacțiunea vocală
        speak_text("Spuneți adresa unde doriți să ajungeți.")
        destinatie = await recognize_speech()
        print(f"[Asistent] Destinație rostită: {destinatie}")

        end = await geocode_adresa(destinatie)

        if not end:
            speak_text("Locația nu a fost identificată. Încercați din nou mai târziu.")
            return

        print("[Asistent] Calculăm traseul...")

        indicatii, coordonate_ruta, durata_traseu = obtine_ruta(last_location, end)
        speak_text(f'Traseul până la destinație durează aproximativ {durata_traseu} minute.')

        # Salvare fișiere
        with open("indicatii_ruta.txt", "w") as f:
            for indicatie in indicatii:
                f.write(indicatie + "\n")

        with open("coordonate_ruta.json", "w") as f:
            json.dump(
                [{"latitude": lat, "longitude": lng} for lat, lng in coordonate_ruta],
                f,
                indent=2
            )

        await websocket.send(json.dumps({
            "type": "ruta",
            "coordonate": [{"latitude": lat, "longitude": lng} for lat, lng in coordonate_ruta]
        }))

        await websocket.send(json.dumps({
            "type": "traseu_nou",
            "locatie_start_lat": last_location[0],
            "locatie_start_lng": last_location[1],
            "locatie_end_lat": end[0],
            "locatie_end_lng": end[1],
            "opriri": []
        }))

        print("Traseu trimis. Începem ghidarea vocală...")
        asyncio.create_task(comenzi_deplasare(location_queue))

        # Continuă să asculte locațiile în fundal
        while True:
            message = await websocket.recv()
            try:
                data = json.loads(message)
                if data.get("type") == "location":
                    last_location = (data.get("lat"), data.get("lng"))
                    await location_queue.put(data)
            except:
                continue

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Conexiune închisă: {e}")

    except Exception as e:
        print(f"Eroare necunoscută: {e}")

    finally:
        current_app = None


async def start_websocket_server():
    print("Pornim serverul WebSocket...")
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print("Server WebSocket pornit pe portul 8765")
    await asyncio.Future() 

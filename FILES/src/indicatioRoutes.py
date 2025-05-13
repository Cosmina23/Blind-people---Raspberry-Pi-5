import asyncio
import json
from textToSpeech import speak_text
from geopy.distance import geodesic as GD

PROXIMITY_METERS = 15

def calculate_distance(lat_s, lng_s, lat_e, lng_e):
    return GD((lat_s, lng_s), (lat_e, lng_e)).km

def get_indicatii():
    with open("indicatii_ruta.txt", "r") as f:
        indicatii = [linie.strip() for linie in f.readlines()]

    with open("coordonate_ruta.json", "r") as f:
        coordonate = json.load(f)

    return indicatii, coordonate

async def comenzi_deplasare(location_queue):
    print("[Asistent] Modulul de ghidare vocală a început.")
    indicatii, coordonate = get_indicatii()
    pas_curent = 0

    while pas_curent < len(coordonate):
        try:
            data = await location_queue.get()

            lat_user = data.get("lat")
            lng_user = data.get("lng")
            lat_end = coordonate[pas_curent]["latitude"]
            lng_end = coordonate[pas_curent]["longitude"]

            dist = calculate_distance(lat_user, lng_user, lat_end, lng_end)
            
            print(f"[Asistent] Distanță până la pasul {pas_curent+1}: {dist*1000:.1f} m")

            if dist * 1000 <= PROXIMITY_METERS:
                instructiune = indicatii[pas_curent]
                mesaj = f"În {PROXIMITY_METERS} de metri, {instructiune.lower()}"
                print(f"[Asistent] Instrucțiune: {instructiune}")
                speak_text(mesaj)
                pas_curent += 1

        except Exception as e:
            print(f"[Asistent] Eroare la procesarea instrucțiunilor: {e}")
            break

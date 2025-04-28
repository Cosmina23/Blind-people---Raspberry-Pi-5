import osmnx as ox 
import networkx as nx 
from geopy.distance import geodesic
from gtts import gTTS
import os 
import math 
import folium

def calculeaza_unghi(p1,p2,p3):
    #vectorii ce formeaza unghiul
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    prod = v1[0]*v2[0] + v1[1]*v2[1]
    norm_u = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    norm_v = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    if norm_u*norm_v == 0:
        return 0

    cos_angle = prod / (norm_u * norm_v)
    cos_angle = max(-1, min(1, cos_angle))
    angle = math.degrees(math.acos(cos_angle))

    #determina semnul unghiului
    determinant = v1[0]*v2[1] - v1[1]*v2[0]
    if determinant > 0:
        return angle #stanga
    else:
        return -angle #dreapta 

def nearest_node(graf, coord):
    return ox.distance.nearest_nodes(graf, X=coord[1], Y=coord[0])

def genereaza_indicatie(angle):
    prag_dreapta = 20
    prag_stanga = -20
    if angle > prag_dreapta:
        return "La dreapta"
    elif angle < prag_stanga:
        return "La stanga"
    else:
        return "Inainte"

def salveaza_harta(graf, ruta):
    noduri = [(graf.nodes[n]['y'], graf.nodes[n]['x']) for n in ruta]
    m = folium.Map(location=noduri[0], zoom_start=15)
    folium.PolyLine(noduri, color='blue', weight=5).add_to(m)
    folium.Marker(noduri[0], tooltip='Start').add_to(m)
    folium.Marker(noduri[-1], tooltip='Finish').add_to(m)
    m.save('maps.html')


def obtine_ruta(start, end):
    print("⏳ Se descarcă harta Timișoara de pe OpenStreetMap...")
    #la prima rulare , decomenteazxa linia pentru a se descaer
    #timisoara_g = ox.graph_from_place("Timișoara, Romania", network_type = "walk")
    print("✅ Harta a fost descărcată cu succes.")

    #ox.save_graphml(timisoara_g, "timisoara.graphml")
    timisoara_g = ox.load_graphml("timisoara.graphml")

    start_node = nearest_node(timisoara_g, start)
    end_node = nearest_node(timisoara_g,end)

    ruta = nx.shortest_path(timisoara_g, start_node, end_node, weight = 'length')

    # map = ox.plot_graph_route(timisoara_g, ruta, route_color='blue')
    # map.save('map.html')

    indicatii = []
    for i in range(len(ruta) - 2):
        u,v,w = ruta[i], ruta[i+1], ruta[i+2]
        lat1, lon1 = timisoara_g.nodes[u]['y'], timisoara_g.nodes[u]['x']
        lat2, lon2 = timisoara_g.nodes[v]['y'], timisoara_g.nodes[v]['x']
        lat3, lon3 = timisoara_g.nodes[w]['y'], timisoara_g.nodes[w]['x']

        distanta = geodesic((lat1, lon1), (lat2,lon2)).meters
        angle = calculeaza_unghi((lat1, lon1), (lat2,lon2), (lat3, lon3))

        #obtine indicatia audio pentru directie
        indicatie_directie = genereaza_indicatie(angle)

        #formeaza mesajul
        mesaj = f"Mergi aproximativ {distanta:.1f} metri, apoi {indicatie_directie}"
        indicatii.append(mesaj)
        #print(mesaj)
        #reda indicatia
        #redare audio

    coordonate_ruta = [(timisoara_g.nodes[n]['y'], timisoara_g.nodes[n]['x']) for n in ruta]
    salveaza_harta(timisoara_g, ruta)
    return indicatii, coordonate_ruta

# start = (45.72787, 21.23604) #Kaufland martirilor
# end = (45.73559, 21.25672) #altex stand vidrighin
# indicatii = obtine_ruta(start,end)
# for indicatie in indicatii:
#     print(indicatie)

#pentru a apela din main, comenteaza liniile 87-91 si decomenteaza 94-97
# def calcul_traseu(start,end):
#     indicatii = obtine_ruta(start,end)
#     for indicatie in indicatii:
#         print(indicatie)
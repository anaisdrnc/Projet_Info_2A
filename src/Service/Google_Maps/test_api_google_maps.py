import googlemaps
from datetime import datetime
import folium
import os


API_KEY = "AIzaSyAkDMMJJmp_xAwa_eBGB9VTCZrf-bCSyy0"


# Initialiser le client Google Maps
gmaps = googlemaps.Client(key=API_KEY)

origin = "ENSAI, Bruz, France"
destination = "Rennes, France"

# Récupérer les directions
now = datetime.now()
directions = gmaps.directions(
    origin,
    destination,
    mode="driving",
    departure_time=now
)

leg = directions[0]['legs'][0]
distance = leg['distance']['text']
duration = leg['duration']['text']
start_location = leg['start_location']
end_location = leg['end_location']

print(f"🚗 Itinéraire de {origin} à {destination}")
print(f"🛣️ Distance : {distance}")
print(f"⏱️ Durée estimée : {duration}")

# Carte créée avec Folium
m = folium.Map(location=[start_location['lat'], start_location['lng']], zoom_start=6)

# Ajouter un marqueur pour le point de départ et d’arrivée
folium.Marker(
    [start_location['lat'], start_location['lng']],
    popup=f"Départ : {origin}",
    icon=folium.Icon(color='green')
).add_to(m)

folium.Marker(
    [end_location['lat'], end_location['lng']],
    popup=f"Arrivée : {destination}",
    icon=folium.Icon(color='red')
).add_to(m)

# === 7️⃣ Tracer le chemin sur la carte ===
# Extraire les points du polyligne
steps = leg['steps']
path = []
for step in steps:
    lat = step['start_location']['lat']
    lng = step['start_location']['lng']
    path.append((lat, lng))
path.append((end_location['lat'], end_location['lng']))

# Ajouter la ligne sur la carte
folium.PolyLine(path, color="blue", weight=5, opacity=0.7).add_to(m)

# === 8️⃣ Enregistrer la carte ===
m.save("itineraire.html")
print("\n🗺️ Carte enregistrée dans 'itineraire.html' — ouvre-la dans ton navigateur !")


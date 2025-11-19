import os
from datetime import datetime

import folium
import googlemaps
from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env")
load_dotenv("/PROJET_INFO_2A/.env")
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")

# Initialiser le client Google Maps
gmaps = googlemaps.Client(key=API_KEY)


def calculer_itineraire(origin: str, destination: str, transport_mode: str) -> gmaps.directions:
    """Calcule l'itinéraire entre deux adresses et renvoie l'objet 'directions' de Google Maps."""
    try:
        directions = gmaps.directions(origin=origin, destination=destination, mode=transport_mode, units="metric")

        if directions:
            print("Itinéraire calculé avec succès!")
            return directions
        else:
            print("Aucun itinéraire trouvé.")
            return None

    except Exception as e:
        print(f"Erreur lors du calcul de l'itinéraire: {e}")
        return None


def display_itinerary_details(directions):
    """Affiche les détails de l'itinéraire dans la console"""
    if not directions or not directions[0]["legs"]:
        print("Aucun détail d'itinéraire disponible")
        return

    leg = directions[0]["legs"][0]

    print("\nÉtapes principales:")
    for i, step in enumerate(leg["steps"], 1):  # Afficher toutes les étapes
        instruction = (
            step["html_instructions"]
            .replace("<b>", "")
            .replace("</b>", "")
            .replace('<div style="font-size:0.9em">', " - ")
            .replace("</div>", "")
        )
        print(f"   {i}. {instruction} ({step['distance']['text']})")


# Récupérer les directions
def create_map(origin, destination, transport_mode):
    now = datetime.now()
    directions = gmaps.directions(
        origin,
        destination,
        mode=transport_mode,
        departure_time=now,
    )

    leg = directions[0]["legs"][0]
    distance = leg["distance"]["text"]
    duration = leg["duration"]["text"]
    start_location = leg["start_location"]
    end_location = leg["end_location"]

    print(f" Itinéraire de {origin} à {destination}")
    print(f" Distance : {distance}")
    print(f" Durée estimée : {duration}")

    # Carte créée avec Folium
    m = folium.Map(location=[start_location["lat"], start_location["lng"]], zoom_start=6)

    # Ajouter un marqueur pour le point de départ et d’arrivée
    folium.Marker(
        [start_location["lat"], start_location["lng"]],
        popup=f"Départ : {origin}",
        icon=folium.Icon(color="green"),
    ).add_to(m)

    folium.Marker(
        [end_location["lat"], end_location["lng"]],
        popup=f"Arrivée : {destination}",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    # Extraire les points du polyligne
    path = []

    for step in leg["steps"]:
        polyline = step["polyline"]["points"]
        decoded_points = googlemaps.convert.decode_polyline(polyline)
        for point in decoded_points:
            path.append((point["lat"], point["lng"]))

    # Trace une ligne détaillée sur la carte
    folium.PolyLine(path, color="blue", weight=5, opacity=0.7).add_to(m)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "delivery_path.html")
    m.save(output_path)

    return output_path

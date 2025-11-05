import os
import sys
from datetime import datetime

import config
import folium
import googlemaps

#from src.DAO.DriverDAO import DriverDAO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Google_Maps.check_address import (
    is_address_sufficient_for_routing,
    validate_and_get_routable_address,
)

API_KEY = config.API_KEY_GOOGLE_MAPS

# Initialiser le client Google Maps
gmaps = googlemaps.Client(key=API_KEY)


def calculer_itineraire(origin: str, destination: str):
    """Calcule l'itinéraire entre deux adresses."""
    try:
        directions = gmaps.directions(
            origin=origin, destination=destination, mode="driving", units="metric"
        )

        if directions:
            print("Itinéraire calculé avec succès!")
            return directions
        else:
            print("Aucun itinéraire trouvé.")
            return None

    except Exception as e:
        print(f"Erreur lors du calcul de l'itinéraire: {e}")
        return None


# Récupérer les directions
def create_map(origin, destination, transport_mode):
    now = datetime.now()
    directions = gmaps.directions(
        origin,
        destination,
        mode=transport_mode,  # souvent "driving"
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
    m = folium.Map(
        location=[start_location["lat"], start_location["lng"]], zoom_start=6
    )

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
        # Chaque step contient une polyline encodée
        polyline = step["polyline"]["points"]
        decoded_points = googlemaps.convert.decode_polyline(polyline)
        # Ajoute tous les points décodés à la liste globale
        for point in decoded_points:
            path.append((point["lat"], point["lng"]))  # noqa: PERF401

    # Tracer une ligne détaillée sur la carte
    folium.PolyLine(path, color="blue", weight=5, opacity=0.7).add_to(m)

    # Enregistre la carte dans le même dossier que les scripts python
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "itineraire.html")
    m.save(output_path)


def main():
    """Fonction principale de votre application de navigation."""
    print("=== SYSTÈME DE NAVIGATION ===")

    # Adresse d'origine fixe
    origin = "ENSAI, Rennes, France"

    # Vérification que l'origine est utilisable
    is_origin_routable, origin_complete = is_address_sufficient_for_routing(origin)
    if not is_origin_routable:
        print("Adresse d'origine non utilisable pour l'itinéraire!")
        return

    print(f"Adresse d'origine: {origin_complete}")

    # Saisie de la destination avec validation
    print("\n" + "=" * 50)
    destination = validate_and_get_routable_address(
        "Entrez votre adresse de destination: "
    )

    if not destination:
        print("Impossible de continuer sans adresse de destination valide.")
        return

    # Calcul de l'itinéraire
    directions = calculer_itineraire(origin_complete, destination)

    if directions:
        # Affichage de la carte
        create_map(origin_complete, destination, "driving")
        # driving
        # bicycling
        # walking
        # transit


if __name__ == "__main__":
    main()

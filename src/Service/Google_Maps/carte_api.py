import os
import sys
from datetime import datetime

import folium
import googlemaps
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.DAO.DriverDAO import DriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.Service.OrderService import OrderService

load_dotenv()
load_dotenv(".env")
load_dotenv("/PROJET_INFO_2A/.env")
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")

# Initialiser le client Google Maps
gmaps = googlemaps.Client(key=API_KEY)


def calculer_itineraire(origin: str, destination: str, transport_mode: str) -> gmaps.directions:
    """Calcule l'itinéraire entre deux adresses."""
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


def difference_time_value_to_time_str(seconds):
    # Convertit des secondes en format heures:minutes
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        print(f"Il y a une différence de {hours}h {minutes:02d}min")
    else:
        print(f"Il y a une différence de {minutes}min")


def main():
    """
    Vérifie si l'adresse rentrée par le client est correcte,
    calcule les temps de trajet pour une voiture et un vélo,
    attribue la commande à un livreur et lui affiche l'itinéraire.
    """
    # Adresse d'origine fixe
    origin = "ENSAI, Rennes, France"

    driver_dao = DriverDAO()
    driver_id = int(input("Enter your driver ID: "))
    driver = driver_dao.get_by_id(driver_id)

    if not driver:
        print(f"Aucun conducteur trouvé avec l'ID {driver_id}.")
        return

    print(f"Conducteur trouvé : {driver.first_name} {driver.last_name}")
    print(f"Moyen de transport : {driver.mean_of_transport}")

    transport_mapping = {"Car": "driving", "Bike": "bicycling", "Walk": "walking"}
    transport_mode = transport_mapping.get(driver.mean_of_transport, "driving")

    if driver.mean_of_transport == "Bike":
        # Filter all orders that are adapted to bicycling
        max_bike_time = 30 * 60  # 30 minutes
        all_ready_orders = OrderService(OrderDAO()).list_all_orders_ready()
        filtered_orders = []

        for order_data in all_ready_orders:
            order_address = order_data["address"]
            destination = f"{order_address.address}, {order_address.postal_code} {order_address.city}"

            try:
                directions_velo = calculer_itineraire(origin, destination, "bicycling")

                if directions_velo and directions_velo[0]["legs"]:
                    duration_velo_seconds = directions_velo[0]["legs"][0]["duration"]["value"]
                    duration_velo_minutes = duration_velo_seconds // 60

                    if duration_velo_seconds <= max_bike_time:
                        filtered_orders.append(order_data)
                        print(f"Commande {order_data['order'].id_order}: {duration_velo_minutes} min")
                    else:
                        print(f"Commande {order_data['order'].id_order}: {duration_velo_minutes} min (trop loin)")
                else:
                    print(f"Commande {order_data['order'].id_order}: impossible de calculer l'itinéraire")

            except Exception as e:
                print(f" Erreur pour la commande {order_data['order'].id_order}: {e}")
                continue

        ready_orders_list_of_dict = filtered_orders
    else:
        ready_orders_list_of_dict = OrderService(OrderDAO()).list_all_orders_ready()

    if not ready_orders_list_of_dict:
        print("Aucune commande prête pour le moment.")
        return
    else:
        oldest_order = ready_orders_list_of_dict[0]  # Commande la plus ancienne
        order_id = oldest_order["order"].id_order

    print(f"Commande disponible: ID {order_id}")
    print(
        f"Adresse: {oldest_order['address'].address}, {oldest_order['address'].postal_code} {oldest_order['address'].city}"
    )

    answer_driver = str(input("Do you accept the next order ? (y/n): "))
    if answer_driver == "y":
        success = OrderService(OrderDAO()).assign_order(driver_id, order_id)

        if success:
            print(f"Commande {order_id} assignée avec succès!")

            OrderService(OrderDAO()).mark_as_en_route(order_id)
            print("Commande marquée comme 'En route'")

            order_address = oldest_order["address"]
            destination_address = f"{order_address.address}, {order_address.postal_code} {order_address.city}"
            directions = calculer_itineraire(origin, destination_address, transport_mode)

            # Affiche la carte et l'itinéraire
            print("\n" + "=" * 60)
            print("Affichage de l'itinéraire de livraison")
            print("=" * 60)

            if directions:
                # Afficher les détails dans la console
                display_itinerary_details(directions)

                # Créer et afficher la carte
                map_path = create_map(origin, destination_address, transport_mode)
                if map_path:
                    print(f"   {map_path}")
                else:
                    print("Impossible de créer la carte")
            else:
                print("Impossible de calculer l'itinéraire")

        else:
            print("Erreur lors de l'assignation de la commande")
            return

    elif answer_driver.lower() == "n":
        print("Au revoir!")
    elif answer_driver == "n":
        pass
    else:
        pass


if __name__ == "__main__":
    main()

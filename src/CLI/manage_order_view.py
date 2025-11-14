# manage_order.py
import os
import sys
from datetime import datetime

import folium
import googlemaps
from dotenv import load_dotenv
from InquirerPy import inquirer

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
utils_dir = os.path.join(project_root, "utils")

# Ajouter tous les paths nécessaires
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)
sys.path.insert(0, utils_dir)

try:
    from CLI.session import Session
    from CLI.view_abstract import VueAbstraite
    from DAO.DriverDAO import DriverDAO
    from DAO.OrderDAO import OrderDAO
    from Service.Google_Maps.map import calculer_itineraire, create_map, display_itinerary_details
    from Service.OrderService import OrderService
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print(f"Python path: {sys.path}")
    raise

# Chargement des variables d'environnement
load_dotenv()
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")

# Initialiser le client Google Maps
gmaps = googlemaps.Client(key=API_KEY)


class ManageOrderView(VueAbstraite):
    def __init__(self, message=""):
        super().__init__(message)
        self.driver_id = Session().get_id_role()
        self.driver_dao = DriverDAO()
        self.order_service = OrderService(OrderDAO())

    def get_available_orders(self):
        """Récupère les commandes disponibles selon le moyen de transport"""
        driver = self.driver_dao.get_by_id(self.driver_id)

        if not driver:
            print("Conducteur non trouvé")
            return []

        print(f"Livreur : {driver.first_name} {driver.last_name}")
        print(f"Moyen de transport : {driver.mean_of_transport}")

        # Adresse d'origine fixe (dépôt)
        origin = "ENSAI, Rennes, France"

        if driver.mean_of_transport == "Bike":
            # Filtrer les commandes adaptées au vélo (max 30 minutes)
            max_bike_time = 30 * 60
            all_ready_orders = self.order_service.list_all_orders_ready()
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
                        else:
                            print(f"Commande {order_data['order'].id_order}: {duration_velo_minutes} min (trop loin)")
                    else:
                        print(f"Commande {order_data['order'].id_order}: impossible de calculer l'itinéraire")

                except Exception as e:
                    print(f"Erreur pour la commande {order_data['order'].id_order}: {e}")
                    continue

            return filtered_orders
        else:
            # Toutes les commandes sont disponibles pour la voiture
            return self.order_service.list_all_orders_ready()

    def choisir_menu(self):
        """Menu principal de gestion des commandes pour les livreurs"""
        print("\n" + "=" * 50)
        print("        GESTION DES LIVRAISONS")
        print("=" * 50)

        # Vérifier si le driver existe
        driver = self.driver_dao.get_by_id(self.driver_id)
        if not driver:
            error_message = "Erreur: Conducteur non trouvé"
            from src.CLI.menu_driver import MenuDriver

            return MenuDriver(message=error_message)

        # Récupérer les commandes disponibles
        available_orders = self.get_available_orders()

        if not available_orders:
            message = "Aucune commande disponible pour le moment."
            print(message)
            from src.CLI.menu_driver import MenuDriver

            return MenuDriver(message=message)

        # Afficher la commande la plus ancienne
        oldest_order = available_orders[0]
        order_id = oldest_order["order"].id_order
        order_address = oldest_order["address"]

        print("\n COMMANDE DISPONIBLE:")
        print(f"   ID: {order_id}")
        print(f"   Adresse: {order_address.address}")
        print(f"   Ville: {order_address.city} {order_address.postal_code}")
        print(f"   Montant: {oldest_order['order'].total_amount}€")

        # Proposer d'accepter ou refuser
        choice = inquirer.select(
            message="Souhaitez-vous accepter cette livraison?",
            choices=[
                {"Accepter la livraison"},
                {"Refuser la livraison"},
                {"Retour au menu"},
            ],
        ).execute()

        if choice == "Accepter la livraison":
            return self.accept_delivery(oldest_order)
        elif choice == "Refuser la livraison":
            message = "Livraison refusée"
            print(message)
            from src.CLI.menu_driver import MenuDriver

            return MenuDriver(message=message)
        else:  # back
            from src.CLI.menu_driver import MenuDriver

            return MenuDriver()

    def accept_delivery(self, order_data):
        """Traite l'acceptation d'une livraison"""
        order_id = order_data["order"].id_order
        order_address = order_data["address"]

        # Assigner la commande au driver
        success = self.order_service.assign_order(self.driver_id, order_id)

        if not success:
            message = "Erreur lors de l'assignation de la commande"
            print(message)
            from src.CLI.menu_driver import MenuDriver

            return MenuDriver(message=message)

        # Marquer comme en route
        self.order_service.mark_as_en_route(order_id)
        print("Commande assignée et marquée comme 'En route'")

        # Calculer et afficher l'itinéraire
        driver = self.driver_dao.get_by_id(self.driver_id)
        transport_mapping = {"Car": "driving", "Bike": "bicycling", "Walk": "walking"}
        transport_mode = transport_mapping.get(driver.mean_of_transport, "driving")

        origin = "ENSAI, Rennes, France"
        destination = f"{order_address.address}, {order_address.postal_code} {order_address.city}"

        print("\n" + "=" * 60)
        print("CALCUL DE L'ITINÉRAIRE")
        print("=" * 60)

        directions = calculer_itineraire(origin, destination, transport_mode)

        if directions:
            # Afficher les détails avec la fonction importée
            display_itinerary_details(directions)

            # Créer la carte avec la fonction importée
            map_path = create_map(origin, destination, transport_mode)
            if map_path:
                print(f"Carte sauvegardée: {map_path}")

                # Proposer d'ouvrir la carte
                open_map = inquirer.confirm(
                    message="Voulez-vous ouvrir la carte dans le navigateur?", default=True
                ).execute()

                if open_map:
                    import webbrowser

                    webbrowser.open(f"file://{os.path.abspath(map_path)}")
            else:
                print("Impossible de créer la carte")
        else:
            print("Impossible de calculer l'itinéraire")

        message = f"Livraison {order_id} acceptée! Itinéraire calculé."
        from src.CLI.menu_driver import MenuDriver

        return MenuDriver(message=message)


# Fonction main pour utilisation standalone
# def main():
#     """Fonction main pour lancer le gestionnaire de commandes standalone"""
#     view = ManageOrderView()
#     view.choisir_menu()


# if __name__ == "__main__":
#     main()


def main():
    """Fonction main pour lancer le gestionnaire de commandes standalone"""
    # Pour le standalone, créer une session temporaire
    driver_id = input("Entrez votre ID de livreur: ").strip()
    if not driver_id.isdigit():
        print("ID invalide")
        return

    # Créer une session temporaire
    class TempSession:
        def get_id_role(self):
            return int(driver_id)

    # Remplacer la session
    import CLI.session as session_module

    original_session = session_module.Session
    session_module.Session = TempSession

    try:
        view = ManageOrderView()
        view.choisir_menu()
    finally:
        # Restaurer la session originale
        session_module.Session = original_session


if __name__ == "__main__":
    main()

import os
import sys

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
    from CLI.view_abstract import VueAbstraite
    from DAO.DriverDAO import DriverDAO
    from DAO.OrderDAO import OrderDAO
    from Service.Google_Maps.map import calculer_itineraire, create_map, display_itinerary_details
    from Service.OrderService import OrderService
    from src.CLI.session import Session
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
    def __init__(self, message="", driver_id=None):
        try:
            super().__init__(message)

            self.driver_dao = DriverDAO()
            self.order_service = OrderService(OrderDAO())

            if driver_id is not None:
                self.driver_id = driver_id
            else:
                session = Session()
                print(f"Session: {session.__dict__}")

                self.driver_id = session.id_role

                # Si ID est None, on cherche par username
                if self.driver_id is None and session.username:
                    print(f"Recherche par username: {session.username}")
                    try:
                        driver = self.driver_dao.get_by_username(session.username)
                        if driver:
                            self.driver_id = driver.id_driver
                            print(f"ID trouvé via username: {self.driver_id}")
                    except:
                        # Sinon chercher dans tous les drivers
                        all_drivers = self.driver_dao.get_all()
                        for driver in all_drivers:
                            if hasattr(driver, 'user_name') and driver.user_name == session.username:
                                self.driver_id = driver.id_driver
                                print(f"ID trouvé dans liste: {self.driver_id}")
                                break
            
            print(f"Driver ID: {self.driver_id}")
            
        except Exception as e:
            print(f"Erreur: {e}")
            self.driver_id = None



    def get_available_orders(self):
        try:
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Erreur: Driver non trouvé dans get_available_orders")
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
                orders = self.order_service.list_all_orders_ready()
                return orders

        except Exception as e:
            print(f"ERREUR dans get_available_orders: {e}")
            import traceback
            traceback.print_exc()
            return []


    def choisir_menu(self):
        """Menu principal de gestion des commandes"""
        try:
            print("\n" + "=" * 50)
            print("        GESTION DES LIVRAISONS")
            print("=" * 50)

            # Vérifier le driver
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Driver non trouvé")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Driver non trouvé")

            print(f"Livreur : {driver.first_name} {driver.last_name}")

            # Récupérer les commandes
            available_orders = self.get_available_orders()

            if not available_orders:
                print("Aucune commande disponible")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Aucune commande disponible")

            # Afficher la commande
            oldest_order = available_orders[0]
            print("\nCOMMANDE DISPONIBLE:")
            print(f"   ID: {oldest_order['order'].id_order}")
            print(f"   Adresse: {oldest_order['address'].address}")
            print(f"   Montant: {oldest_order['order'].total_amount}€")

            choice = inquirer.select(
                message="Souhaitez-vous accepter cette livraison?",
                choices=[
                    "Accepter la livraison",
                    "Refuser la livraison",
                    "Retour au menu driver"
                ],
            ).execute()

            if choice == "Accepter la livraison":
                return self.accept_delivery(oldest_order)
            elif choice == "Refuser la livraison":
                print("Livraison refusée")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Livraison refusée")
            else:
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver()

        except Exception as e:
            print(f"Erreur: {e}")
            from CLI.driver.menu_driver import MenuDriver
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
        self.order_service.mark_as_on_the_way(order_id)
        print("Commande assignée et marquée comme 'On the way'")

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
        print(message)

        choice = inquirer.select(
                message="Que voulez-vous faire maintenant?",
                choices=[
                    "Voir d'autres commandes",
                    "Retour au menu driver"
                ],
            ).execute()
        try:
            if choice == "Voir d'autres commandes":
                    # On rappelle choisir_menu pour voir d'autres commandes
                    return self.choisir_menu()
            else:
                    # On retourne au menu driver
                    print("Retour au menu driver...")
                    from CLI.driver.menu_driver import MenuDriver
                    return MenuDriver(message=message)

        except Exception as e:
            print(f"Erreur dans accept_delivery: {e}")
            return None

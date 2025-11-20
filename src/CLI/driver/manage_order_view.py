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
    from Service.Google_Maps.map import compute_itinerary, create_map, display_itinerary_details
    from Service.OrderService import OrderService
    from CLI.session import Session
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
    """
    Class that defines the view for managing an order from the deliverer's side.
    """
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
                    print(f"Searching by username: {session.username}")
                    try:
                        driver = self.driver_dao.get_by_username(session.username)
                        if driver:
                            self.driver_id = driver.id_driver
                            print(f"ID found via username: {self.driver_id}")
                    except:
                        # Sinon chercher dans tous les drivers
                        all_drivers = self.driver_dao.get_all()
                        for driver in all_drivers:
                            if hasattr(driver, 'user_name') and driver.user_name == session.username:
                                self.driver_id = driver.id_driver
                                break

            print(f"Driver ID: {self.driver_id}")

        except Exception as e:
            print(f"Error: {e}")
            self.driver_id = None



    def get_available_orders(self):
        """
        Lists all the available orders. If the deliverer uses a bike, he cannot take orders
        that are more than 30 minutes away from ENSAI.
        """
        try:
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Error : driver not found in get_available_orders")
                return []

            print(f"Mean of transport : {driver.mean_of_transport}")

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
                        directions_velo = compute_itinerary(origin, destination, "bicycling")

                        if directions_velo and directions_velo[0]["legs"]:
                            duration_velo_seconds = directions_velo[0]["legs"][0]["duration"]["value"]
                            duration_velo_minutes = duration_velo_seconds // 60

                            if duration_velo_seconds <= max_bike_time:
                                filtered_orders.append(order_data)
                            else:
                                print(f"Order {order_data['order'].id_order}: {duration_velo_minutes} min (too far)")
                        else:
                            print(f"Order {order_data['order'].id_order}: impossible to compute the itinerary")

                    except Exception as e:
                        print(f"Error for the delivery {order_data['order'].id_order}: {e}")
                        continue

                return filtered_orders

            else:
                orders = self.order_service.list_all_orders_ready()
                return orders

        except Exception as e:
            print(f"Error in get_available_orders: {e}")
            import traceback
            traceback.print_exc()
            return []


    def choisir_menu(self):
        """Main menu for managing orders"""
        try:
            print("\n" + "=" * 50)
            print("        Managing orders")
            print("=" * 50)

            # Vérifier le driver
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Driver not found")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Driver found")

            print(f"Deliverer : {driver.first_name} {driver.last_name}")

            # Récupérer les commandes
            available_orders = self.get_available_orders()

            if not available_orders:
                print("No available orders")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="No available orders")

            # Afficher la commande
            oldest_order = available_orders[0]
            print("\nAvailable orde:")
            print(f"   ID: {oldest_order['order'].id_order}")
            print(f"   Address: {oldest_order['address'].address}")
            print(f"   Total amount: {oldest_order['order'].total_amount}€")

            choice = inquirer.select(
                message="Do you accept the delivery ?",
                choices=[
                    "Accept the delivery",
                    "Refuse the delivery",
                    "Return to the main menu"
                ],
            ).execute()

            if choice == "Accept the delivery":
                return self.accept_delivery(oldest_order)
            elif choice == "Refuse the delivery":
                print("Order refused")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Order refused")
            else:
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver()

        except Exception as e:
            print(f"Error: {e}")
            from CLI.driver.menu_driver import MenuDriver
            return MenuDriver()


    def accept_delivery(self, order_data):
        """Handles the acceptation of an order"""
        order_id = order_data["order"].id_order
        order_address = order_data["address"]

        # Assigner la commande au driver
        success = self.order_service.assign_order(self.driver_id, order_id)

        if not success:
            message = "Error during the assignement of the order"
            print(message)
            from CLI.menu_driver import MenuDriver

            return MenuDriver(message=message)

        # Marquer comme en route
        self.order_service.mark_as_on_the_way(order_id)
        print("Order assigned and marked as 'On the way'")

        # Calculer et afficher l'itinéraire
        driver = self.driver_dao.get_by_id(self.driver_id)
        transport_mapping = {"Car": "driving", "Bike": "bicycling"}
        transport_mode = transport_mapping.get(driver.mean_of_transport, "driving")

        origin = "ENSAI, Rennes, France"
        destination = f"{order_address.address}, {order_address.postal_code} {order_address.city}"

        print("\n" + "=" * 60)
        print("Computing itinerary")
        print("=" * 60)

        directions = compute_itinerary(origin, destination, transport_mode)

        if directions:
            # Afficher les détails avec la fonction importée
            display_itinerary_details(directions)

            # Créer la carte avec la fonction importée
            map_path = create_map(origin, destination, transport_mode)
            if map_path:
                print(f"Map saved: {map_path}")
                print("You can now open the map path by downloading the file delivery_path.html in the Google_Maps service")
            else:
                print("Impossible to compute a map")
        else:
            print("Impossible to compute an itinerary")

        message = f"Delivery {order_id} accepted. Itinerary computed."
        print(message)

        choice = inquirer.select(
                message="What do you want to do now ?",
                choices=[
                    "Check other orders",
                    "Return to the driver's menu"
                ],
            ).execute()
        try:
            if choice == "Check other orders":
                    # On rappelle choisir_menu pour voir d'autres commandes
                    return self.choisir_menu()
            else:
                    # On retourne au menu driver
                    print("Returning to the driver's menu...")
                    from CLI.driver.menu_driver import MenuDriver
                    return MenuDriver(message=message)

        except Exception as e:
            print(f"Error in accept_delivery: {e}")
            return None

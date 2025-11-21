import os

import googlemaps
from dotenv import load_dotenv
from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.DriverDAO import DriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.Service.Google_Maps.map import compute_itinerary, create_map, display_itinerary_details
from src.Service.OrderService import OrderService

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)


class ManageOrderView(AbstractView):
    """
    View for managing orders from the deliverer's perspective.
    """

    def __init__(self, message="", driver_id=None):
        try:
            super().__init__(message)
            self.driver_dao = DriverDAO()
            self.order_service = OrderService(OrderDAO())

            # Retrieving driver's id
            if driver_id is not None:
                self.driver_id = driver_id
            else:
                session = Session()
                print(f"Session: {session.__dict__}")
                self.driver_id = session.id_role

                # If ID is None, search by username
                if self.driver_id is None and session.username:
                    print(f"Searching by username: {session.username}")
                    try:
                        driver = self.driver_dao.get_by_username(session.username)
                        if driver:
                            self.driver_id = driver.id_driver
                            print(f"ID found via username: {self.driver_id}")
                    except Exception as e:
                        # Otherwise search all drivers
                        print(f"Error fetching driver by username: {e}")
                        all_drivers = self.driver_dao.get_all()
                        for driver in all_drivers:
                            if hasattr(driver, "user_name") and driver.user_name == session.username:
                                self.driver_id = driver.id_driver
                                break
            print(f"Driver ID: {self.driver_id}")
        except Exception as e:
            print(f"Error: {e}")
            self.driver_id = None

    def get_available_orders(self):
        """
        Lists all available orders. Deliverers using a bike cannot take orders
        that are more than 30 minutes away from ENSAI.
        """
        try:
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Error: driver not found in get_available_orders")
                return []

            print(f"Transport type: {driver.mean_of_transport}")
            origin = "ENSAI, Rennes, France"

            # If the deliverer uses a bike, he can only deliver orders that are less than 30 minutes away
            if driver.mean_of_transport == "Bike":
                max_bike_time = 30 * 60
                all_ready_orders = self.order_service.list_all_orders_ready()
                filtered_orders = []

                for order_data in all_ready_orders:
                    order_address = order_data["address"]
                    destination = f"{order_address.address}, {order_address.postal_code} {order_address.city}"

                    try:
                        directions_bike = compute_itinerary(origin, destination, "bicycling")
                        if directions_bike and directions_bike[0]["legs"]:
                            duration_seconds = directions_bike[0]["legs"][0]["duration"]["value"]
                            duration_minutes = duration_seconds // 60

                            if duration_seconds <= max_bike_time:
                                filtered_orders.append(order_data)
                            else:
                                print(f"Order {order_data['order'].id_order}: {duration_minutes} min (too far)")
                        else:
                            print(f"Order {order_data['order'].id_order}: unable to compute itinerary")
                    except Exception as e:
                        print(f"Error for delivery {order_data['order'].id_order}: {e}")
                        continue

                return filtered_orders

            # For the other drivers, they can deliver all orders
            else:
                return self.order_service.list_all_orders_ready()

        except Exception as e:
            print(f"Error in get_available_orders: {e}")
            import traceback
            traceback.print_exc()
            return []

    def choose_menu(self):
        """Main menu for managing orders"""
        try:
            print("\n" + "=" * 50)
            print("        Managing Orders")
            print("=" * 50)

            # Retrieving driver's id
            driver = self.driver_dao.get_by_id(self.driver_id)
            if not driver:
                print("Driver not found")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="Driver not found")

            # Showing driver's main info
            print(f"Deliverer: {driver.first_name} {driver.last_name}")
            available_orders = self.get_available_orders()

            if not available_orders:
                print("No available orders")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message="No available orders")

            # Showing the first order's main info
            oldest_order = available_orders[0]
            print("\nAvailable order:")
            print(f"   ID: {oldest_order['order'].id_order}")
            print(f"   Address: {oldest_order['address'].address}")
            print(f"   Total amount: {oldest_order['order'].total_amount}€")

            choice = inquirer.select(
                message="Do you accept the delivery?",
                choices=["Accept the delivery", "Refuse the delivery", "Return to the main menu"],
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
        """Handle accepting an order"""
        order_id = order_data["order"].id_order
        order_address = order_data["address"]

        # Assign the order to the driver
        success = self.order_service.assign_order(self.driver_id, order_id)
        if not success:
            message = "Error assigning the order"
            print(message)
            from CLI.menu_driver import MenuDriver
            return MenuDriver(message=message)

        # Mark as 'on the way'
        self.order_service.mark_as_on_the_way(order_id)
        print("Order assigned and marked as 'On the way'")

        # Compute and display the itinerary
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
            display_itinerary_details(directions)
            map_path = create_map(origin, destination, transport_mode)
            if map_path:
                print(f"Map saved: {map_path}")
                print("You can now open the map file 'delivery_path.html' in the Google_Maps service")
            else:
                print("Unable to compute map")
        else:
            print("Unable to compute itinerary")

        print(f"Delivery {order_id} accepted. Itinerary computed.")

        # As long as the driver has not delivered the order, he cannot accept an other one
        while True:
            answer = input("Have you delivered the order? (y/n): ")
            if answer == "y":
                self.order_service.mark_as_delivered(order_id)
                break
            elif answer == "n":
                print("Please deliver the order")
            else:
                print("Invalid answer")

        choice = inquirer.select(
            message="What do you want to do now ?",
            choices=["Check other orders", "Return to the driver's menu"],
        ).execute()

        try:
            if choice == "Check other orders":
                return self.choose_menu()
            else:
                print("Returning to the driver's menu...")
                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message=f"Delivery {order_id} completed")
        except Exception as e:
            print(f"Error in accept_delivery: {e}")
            return None

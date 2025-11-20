import logging

import dotenv

from src.CLI.opening.openingview import OpeningView
from src.utils.log_init import initialize_logs

if __name__ == "__main__":
    dotenv.load_dotenv(override=True)

    initialize_logs("Application")

    current_view = OpeningView("Welcome")
    error_count = 0

    while current_view:
        if error_count > 100:
            print("The program has encountered too many errors and will stop.")
            break
        try:
            current_view.display()
            current_view = current_view.choose_menu()
        except Exception as e:
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            error_count += 1
            current_view = OpeningView(
                "An error occurred, returning to the main menu.\nCheck the logs for more information."
            )

    print("----------------------------------")
    print("Goodbye")

    logging.info("End of application")

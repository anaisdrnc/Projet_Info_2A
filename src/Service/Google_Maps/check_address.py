import os
from typing import Dict, List, Tuple

import googlemaps
from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env")
load_dotenv("/PROJET_INFO_2A/.env")
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")
gmaps = googlemaps.Client(key=API_KEY)


def check_address(adresse: str) -> bool:
    """
    Checks if the address exists in Google Maps.
    ---------
    Parameters:
    adresse: str

    Returns:
    bool
    """
    if adresse is None:
        return False
    result = gmaps.geocode(adresse)
    return bool(result)


def is_address_sufficient_for_routing(adresse: str) -> Tuple[bool, str]:
    """
    Checks if the address is sufficient for computing an itinerary with it.
    It mainly checks the length of the address (>3).
    ------------
    Parameters:
    adresse: str

    Returns:
        Tuple[bool, str]: (Is address valid for itinerary, Complete address)
    """
    if not adresse or len(adresse.strip()) < 3:
        return False, ""

    results = gmaps.geocode(adresse)
    # Returns a list of GeocodeResult items that represents places that matched 'adresse'
    # Check https://developers.google.com/maps/documentation/geocoding/geocoding?hl=fr for more information
    # about the parameters in GeocodeResult
    if not results:
        return False, ""

    best_result = results[0]
    formatted_address = best_result.get("formatted_address", "")    # Formatted address obtained from Google Maps
    address_components = best_result.get("address_components", [])  # Components detected in the address (city, street...)
    best_result.get("types", [])

    # Checks if "locality" is in the address components
    has_city = any("locality" in comp.get("types", []) for comp in address_components)
    # Checks if "route" is in the address components
    has_street = any("route" in comp.get("types", []) for comp in address_components)
    # Checks if "postal_code" is in the address components
    any("postal_code" in comp.get("types", []) for comp in address_components)

    if has_city or has_street:
        return True, formatted_address
    else:
        return False, formatted_address


def get_address_suggestions(adresse: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Returns up to 5 complete address suggestions
    ---------
    Parameters:
    adress: str
    max_results: int

    Returns:
    suggestions: List[Dict[str, str]]
    """
    if not adresse:
        return []

    results = gmaps.geocode(adresse)
    # Returns a list of GeocodeResult items that represents places that matched 'adresse'
    suggestions = []

    for result in results[:max_results]:
        address_components = result.get("address_components", [])
        formatted_address = result.get("formatted_address", "")

        # Main components in the GeocodeResult class
        components = {
            "street_number": "",
            "street_name": "",
            "city": "",
            "postal_code": "",
            "full_address": formatted_address,
            "is_routable": False,
        }

    # Checking if the address has any component listed above
        for component in address_components:
            types = component.get("types", [])
            name = component.get("long_name", "")

            if "street_number" in types:
                components["street_number"] = name
            elif "route" in types:
                components["street_name"] = name
            elif "locality" in types:
                components["city"] = name
            elif "postal_code" in types:
                components["postal_code"] = name

        has_city = any(
            "locality" in comp.get("types", []) for comp in address_components
        )
        has_street = any(
            "route" in comp.get("types", []) for comp in address_components
        )
        components["is_routable"] = has_city or has_street
        # A component is considered as routable if the address has a city or a streer

        suggestions.append(components)

    return suggestions


def display_suggestions(adresse: str):
    """Displays address suggestion.
    ---------
    Parameters:
    adresse: str

    Returns:
    str
    """
    suggestions = get_address_suggestions(adresse)

    if not suggestions:
        print("No suggestions found for this address.")
        return

    print(f"\nSuggestions for '{adresse}':")
    print("=" * 60)

    # Displays the suggested address accoridng to its components
    for i, suggestion in enumerate(suggestions, 1):
        routable_indicator = "VALID" if suggestion["is_routable"] else "INVALID "
        print(f"{routable_indicator} {i}. {suggestion['full_address']}")

        details = []
        if suggestion["street_number"] and suggestion["street_name"]:
            details.append(f"{suggestion['street_number']} {suggestion['street_name']}")
        elif suggestion["street_name"]:
            details.append(f"{suggestion['street_name']}")

        if suggestion["city"]:
            details.append(f"{suggestion['city']}")

        if suggestion["postal_code"]:
            details.append(f"{suggestion['postal_code']}")

        if details:
            print("   " + " | ".join(details))

        if not suggestion["is_routable"]:
            print("This address is not precise enough for computing an itinerary")

        print()

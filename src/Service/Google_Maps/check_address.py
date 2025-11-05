import googlemaps
import config
from typing import List, Dict, Tuple

API_KEY = config.API_KEY_GOOGLE_MAPS
gmaps = googlemaps.Client(key=API_KEY)


def check_address(adresse: str) -> bool:
    """Vérifie si une adresse existe via Google Maps."""
    if adresse is None:
        return False
    result = gmaps.geocode(adresse)
    return bool(result)


def is_address_sufficient_for_routing(adresse: str) -> Tuple[bool, str]:
    """
    Vérifie si l'adresse est suffisamment précise pour le calcul d'itinéraire.

    Returns:
        Tuple[bool, str]: (Est_valide_pour_itineraire, Adresse_complete)
    """
    if not adresse or len(adresse.strip()) < 3:
        return False, ""

    results = gmaps.geocode(adresse)
    if not results:
        return False, ""

    # Prendre le premier résultat
    best_result = results[0]
    formatted_address = best_result.get("formatted_address", "")
    address_components = best_result.get("address_components", [])
    types = best_result.get("types", [])

    # Vérifier si l'adresse contient au moins une ville ou une rue
    has_city = any("locality" in comp.get("types", []) for comp in address_components)
    has_street = any("route" in comp.get("types", []) for comp in address_components)
    has_postal_code = any(
        "postal_code" in comp.get("types", []) for comp in address_components
    )

    # Pour le calcul d'itinéraire, on veut au minimum une ville ou une rue
    if has_city or has_street:
        return True, formatted_address
    else:
        return False, formatted_address


def get_address_suggestions(adresse: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Retourne des suggestions d'adresses complètes."""
    if not adresse:
        return []

    results = gmaps.geocode(adresse)
    suggestions = []

    for result in results[:max_results]:
        address_components = result.get("address_components", [])
        formatted_address = result.get("formatted_address", "")

        components = {
            "street_number": "",
            "street_name": "",
            "city": "",
            "postal_code": "",
            "full_address": formatted_address,
            "is_routable": False,
        }

        # Extraire les composants
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

        # Déterminer si l'adresse est utilisable pour l'itinéraire
        has_city = any(
            "locality" in comp.get("types", []) for comp in address_components
        )
        has_street = any(
            "route" in comp.get("types", []) for comp in address_components
        )
        components["is_routable"] = has_city or has_street

        suggestions.append(components)

    return suggestions


def display_suggestions(adresse: str):
    """Affiche les suggestions d'adresses de manière claire."""
    suggestions = get_address_suggestions(adresse)

    if not suggestions:
        print("Aucune suggestion trouvée pour cette adresse.")
        return

    print(f"\nSuggestions pour '{adresse}':")
    print("=" * 60)

    for i, suggestion in enumerate(suggestions, 1):
        routable_indicator = "✅" if suggestion["is_routable"] else "⚠️ "
        print(f"{routable_indicator} {i}. {suggestion['full_address']}")

        # Afficher les détails
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
            print("Cette adresse est trop imprécise pour calculer un itinéraire")

        print()


def validate_and_get_routable_address(prompt: str, max_attempts: int = 3) -> str:
    """
    Valide une adresse et s'assure qu'elle est utilisable pour le calcul d'itinéraire.

    Returns:
        str: Adresse complète validée ou None si échec
    """
    for attempt in range(max_attempts):
        # Saisie de l'adresse
        address_input = input(prompt).strip()

        if not address_input:
            print("Veuillez saisir une adresse.")
            continue

        if len(address_input) < 3:
            print("Adresse trop courte. Veuillez saisir au moins 3 caractères.")
            continue

        # Vérification si l'adresse est utilisable pour l'itinéraire
        is_routable, complete_address = is_address_sufficient_for_routing(address_input)

        if is_routable:
            print(f"Adresse valide pour l'itinéraire: {complete_address}")
            return complete_address
        else:
            print(
                f"❌ Adresse trop imprécise pour calculer un itinéraire (tentative {attempt + 1}/{max_attempts})"
            )

            # Afficher les suggestions
            display_suggestions(address_input)

            # Proposer des options
            print("\nOptions:")
            print("1. Choisir une adresse suggérée (utilisable pour itinéraire)")
            print("2. Saisir une nouvelle adresse")
            print("3. Quitter")

            choice = input("Votre choix (1-3): ").strip()

            if choice == "1":
                # Choix d'une adresse suggérée
                suggestions = get_address_suggestions(address_input)
                routable_suggestions = [s for s in suggestions if s["is_routable"]]

                if routable_suggestions:
                    print("\nSélectionnez une adresse utilisable:")
                    for i, suggestion in enumerate(routable_suggestions, 1):
                        print(f"{i}. {suggestion['full_address']}")

                    try:
                        selected = int(input("Numéro de l'adresse: ")) - 1
                        if 0 <= selected < len(routable_suggestions):
                            selected_address = routable_suggestions[selected][
                                "full_address"
                            ]
                            print(f"Adresse sélectionnée: {selected_address}")
                            return selected_address
                        else:
                            print("Sélection invalide.")
                    except ValueError:
                        print("Veuillez entrer un numéro valide.")
                else:
                    print("Aucune suggestion utilisable pour l'itinéraire.")

            elif choice == "2":
                # Continuer avec une nouvelle saisie
                continue

            elif choice == "3":
                print("Arrêt de la saisie.")
                return None

    print(f"Échec après {max_attempts} tentatives.")
    return None

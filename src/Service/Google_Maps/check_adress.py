import googlemaps
import config
from typing import List, Dict, Any

API_KEY = config.API_KEY_GOOGLE_MAPS
gmaps = googlemaps.Client(key=API_KEY)

def check_adress(adresse: str) -> bool:
    """Vérifie si une adresse existe via Google Maps."""
    if adresse == None:
        return "Please enter an adress"
    result = gmaps.geocode(adresse)
    if result:
        print(f"Adresse trouvée : {result[0]['formatted_address']}")
        return True
    else:
        print(f"Adresse introuvable : {adresse}")
        return False


def find_address_suggestions(adresse: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Trouve des suggestions d'adresses alternatives lorsque l'adresse est incomplète ou ambiguë.
    
    Args:
        adresse (str): L'adresse à vérifier
        max_results (int): Nombre maximum de suggestions à retourner
    
    Returns:
        List[Dict]: Liste des suggestions d'adresses avec détails
    """
    if not adresse:
        print("Veuillez entrer une adresse")
        return []
    
    # Utiliser l'API Geocoding de Google Maps
    results = gmaps.geocode(adresse)
    
    if not results:
        print(f"Aucune suggestion trouvée pour : {adresse}")
        return []
    
    suggestions = []
    
    for i, result in enumerate(results[:max_results]):
        address_data = result.get('address_components', [])
        formatted_address = result.get('formatted_address', 'N/A')
        location = result.get('geometry', {}).get('location', {})
        types = result.get('types', [])
        
        # Extraire les composants d'adresse
        address_components = {}
        for component in address_data:
            component_types = component.get('types', [])
            component_name = component.get('long_name', '')
            
            if 'street_number' in component_types:
                address_components['street_number'] = component_name
            elif 'route' in component_types:
                address_components['street_name'] = component_name
            elif 'locality' in component_types:
                address_components['city'] = component_name
            elif 'administrative_area_level_1' in component_types:
                address_components['state'] = component_name
            elif 'postal_code' in component_types:
                address_components['postal_code'] = component_name
            elif 'country' in component_types:
                address_components['country'] = component_name
        
        # Déterminer le type de résultat
        result_type = "Adresse complète"
        if 'street_address' in types:
            result_type = "Adresse précise"
        elif 'premise' in types:
            result_type = "Bâtiment/Établissement"
        elif 'route' in types:
            result_type = "Rue seulement"
        elif 'locality' in types:
            result_type = "Ville"
        elif 'administrative_area_level_1' in types:
            result_type = "Région/État"
        elif 'postal_code' in types:
            result_type = "Code postal"
        
        suggestion = {
            'rank': i + 1,
            'formatted_address': formatted_address,
            'type': result_type,
            'components': address_components,
            'location': location,
            'confidence': len(address_components)  # Estimation simple de la confiance
        }
        
        suggestions.append(suggestion)
    
    return suggestions

def display_address_suggestions(adresse: str, max_results: int = 5):
    """
    Affiche les suggestions d'adresses de manière lisible.
    """
    suggestions = find_address_suggestions(adresse, max_results)
    
    if not suggestions:
        print(f"Aucune suggestion trouvée pour : {adresse}")
        return
    
    print(f"\nSuggestions pour '{adresse}':")
    print("=" * 80)
    
    for suggestion in suggestions:
        print(f"\n#{suggestion['rank']} - [{suggestion['type']}]")
        print(f"{suggestion['formatted_address']}")
        
        components = suggestion['components']
        if components:
            print("   Composants:")
            if 'street_number' in components and 'street_name' in components:
                print(f"Rue: {components.get('street_number', '')} {components.get('street_name', '')}")
            if 'city' in components:
                print(f"Ville: {components['city']}")
            if 'state' in components:
                print(f"Région: {components['state']}")
            if 'postal_code' in components:
                print(f"Code postal: {components['postal_code']}")
            if 'country' in components:
                print(f"Pays: {components['country']}")
        
        location = suggestion['location']
        if location:
            print(f"Coordonnées: {location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}")
        
        #print(f"Confiance estimée: {suggestion['confidence']}/6")
        print("-" * 60)

# Fonction utilitaire pour analyser la qualité de l'adresse
def analyze_address_quality(adresse: str):
    """
    Analyse la qualité et la complétude d'une adresse.
    """
    suggestions = find_address_suggestions(adresse)
    
    if not suggestions:
        print("Adresse non reconnue")
        return
    
    best_match = suggestions[0]
    
    print(f"\n Analyse de l'adresse: '{adresse}'")
    print("=" * 50)
    print(f"Meilleure correspondance: {best_match['formatted_address']}")
    print(f"Type: {best_match['type']}")
    print(f"Score de confiance: {best_match['confidence']}/6")
    
    missing_components = []
    if 'street_number' not in best_match['components']:
        missing_components.append("numéro de rue")
    if 'street_name' not in best_match['components']:
        missing_components.append("nom de rue")
    if 'city' not in best_match['components']:
        missing_components.append("ville")
    if 'postal_code' not in best_match['components']:
        missing_components.append("code postal")
    
    if missing_components:
        print(f"Composants manquants: {', '.join(missing_components)}")
    else:
        print("Adresse complète détectée")
    
    if len(suggestions) > 1:
        print(f"{len(suggestions) - 1} autres suggestions disponibles")

# Exemples d'utilisation
if __name__ == "__main__":
    # Test avec différentes adresses incomplètes
    test_addresses = [
        "1600 Amphitheatre Parkway",  # Adresse complète
        "rue de rivoli paris",        # Rue + ville
        "new york",                   # Ville seulement
        "90210",                      # Code postal seulement
        "eiffel tower",               # Point de repère
        "starbucks san francisco"     # Commerce + ville
    ]
    
    for address in test_addresses:
        print("\n" + "="*100)
        display_address_suggestions(address, 3)
        
        # Vérifier aussi si l'adresse existe
        exists = check_adress(address)
        print(f"Adresse valide: {exists}")
        
        # Analyse de qualité
        #analyze_address_quality(address)
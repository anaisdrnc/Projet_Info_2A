import googlemaps

API_KEY = "AIzaSyAkDMMJJmp_xAwa_eBGB9VTCZrf-bCSyy0"
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
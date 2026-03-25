import requests


def get_morocco_tourist_sites():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:60];
    area["name:en"="Morocco"]->.searchArea;
    (
      nwr["tourism"="attraction"](area.searchArea);
      nwr["historic"="monument"](area.searchArea);
      nwr["heritage"](area.searchArea);
    );
    out center;
    """

    print("Recherche en cours dans tout le Maroc...")
    response = requests.get(overpass_url, params={'data': overpass_query})

    if response.status_code != 200:
        print(f"Erreur API : {response.status_code}")
        return []

    data = response.json()
    elements = data.get('elements', [])

    locations = []
    for element in elements:
        tags = element.get('tags', {})
        name = tags.get('name') or tags.get('name:fr') or tags.get('name:en')

        if name:
            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')

            locations.append({
                "name": name,
                "city": tags.get('addr:city', 'Inconnue'),
                "lat": lat,
                "lon": lon,
                "category": tags.get('tourism') or tags.get('historic') or "Monument"
            })

    return locations


# Exécution
all_sites = get_morocco_tourist_sites()
print(f"Succès ! {len(all_sites)} sites touristiques trouvés au Maroc.")

# Afficher les 5 premiers pour tester
for site in all_sites[:5]:
    print(f"- {site['name']} ({site['city']})")
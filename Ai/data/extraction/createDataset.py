from geodata import all_sites

import json

def save_as_json(data, filename="monuments_maroc.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Fichier JSON enregistré : {filename}")

save_as_json(all_sites)
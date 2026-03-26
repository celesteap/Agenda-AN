import requests
from ics import Calendar, Event
from datetime import datetime
import hashlib

def generate_ics():
    # On teste l'URL globale des réunions (plus de chances d'avoir du contenu)
    url = "https://data.assemblee-nationale.fr/backend/api/v1/agenda/reunions"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Erreur de connexion à l'API : {e}")
        return

    calendar = Calendar()
    calendar.creator = "Mon Agenda Assemblée"

    # On essaie de trouver les événements dans différentes clés possibles du JSON
    reunions = data.get('reunions', [])
    if not reunions:
        # Si 'reunions' est vide, on cherche dans le format 'getSeancesPubliquesResponse'
        reunions = data.get('getSeancesPubliquesResponse', {}).get('seances', [])

    if not reunions:
        print("Aucun événement trouvé dans l'API actuellement.")
        # On ajoute un événement informatif pour prouver que le script marche
        e = Event()
        e.name = "⚠️ Aucune séance publiée (MAJ: " + datetime.now().strftime("%H:%M") + ")"
        e.begin = datetime.now()
        e.uid = "status-empty-" + datetime.now().strftime("%Y%m%d")
        calendar.events.add(e)
    else:
        for item in reunions:
            try:
                e = Event()
                # On récupère le libellé ou le titre de la réunion
                e.name = item.get('libelle') or item.get('objet') or "Réunion Assemblée"
                
                # Gestion des dates (ISO 8601)
                start = item.get('dateDebut')
                if start:
                    e.begin = start
                    if item.get('dateFin'):
                        e.end = item.get('dateFin')
                    
                    e.location = item.get('lieu', 'Palais Bourbon')
                    e.description = f"Type: {item.get('type')}\nID: {item.get('id')}"
                    
                    # UID unique
                    uid_seed = f"an-{item.get('id')}-{start}"
                    e.uid = hashlib.md5(uid_seed.encode()).hexdigest() + "@assemblee"
                    
                    calendar.events.add(e)
            except Exception as err:
                print(f"Saut d'un événement suite à erreur : {err}")
                continue

    # Écriture du fichier
    with open('agenda.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())
    print(f"Succès : {len(calendar.events)} événements écrits.")

if __name__ == "__main__":
    generate_ics()

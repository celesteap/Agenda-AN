import requests
from ics import Calendar, Event
from datetime import datetime
import hashlib

def generate_ics():
    # Source officielle Open Data de l'Assemblée Nationale
    url = "https://data.assemblee-nationale.fr/backend/api/v1/agenda/seances-publiques"
    
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Erreur de récupération : {e}")
        return

    calendar = Calendar()
    calendar.creator = "Mon Agenda Assemblée"

    # Extraction des séances
    seances = data.get('getSeancesPubliquesResponse', {}).get('seances', [])
    
    for item in seances:
        try:
            e = Event()
            e.name = item.get('libelle', 'Séance Assemblée')
            e.begin = item.get('dateDebut')
            if item.get('dateFin'):
                e.end = item.get('dateFin')
            
            # On ajoute des détails dans la description
            e.description = f"Type : {item.get('type')}\nLieu : {item.get('lieu')}"
            e.location = item.get('lieu', 'Palais Bourbon')
            
            # UID unique pour éviter les doublons dans Google Calendar
            uid_seed = f"an-{item.get('id')}"
            e.uid = hashlib.md5(uid_seed.encode()).hexdigest() + "@assemblee-nationale.fr"

            calendar.events.add(e)
        except:
            continue

    with open('agenda.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    generate_ics()

import requests
from ics import Calendar
from datetime import datetime

def generate_ics():
    # URL des évènements journaliers d'aujourd'hui
    url = "https://www2.assemblee-nationale.fr/agendas/ics/" + datetime.today().strftime('%Y-%m-%d') + "/journalier"
    
    # Vérifie la connexion à l'URL
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"Erreur de connexion à l'API : {e}")
        return

    # Nettoyage du texte
    parsable = response.text.replace("\r", "") # retours chariots supprimés
    parsable = parsable.replace("\\n", "") # retours de ligne supprimés
    parsable = parsable.replace("&#039;", "'") # restauration des apostrophes

    # Création du calendrier depuis le fichier ICS
    calendar = Calendar(parsable)
    calendar.creator = "Mon Agenda Assemblée"

    # Écriture du fichier
    with open('agenda.ics', 'w', encoding="utf-8") as f:
        f.writelines(calendar.serialize_iter())
    reunions = [e for e in calendar.events if "réunion" in e.name.lower()]
    seances = [e for e in calendar.events if "séance" in e.name.lower()]

    # Message final : nombre d'évènements trouvés, nombre de réunions, nombre de séances
    if len(calendar.events) > 0:
        print(f"Succès : {len(calendar.events)} événements écrits : {len(reunions)} réunions, {len(seances)} séances")
    else:
        print("Aucun évènement trouvé pour le " + datetime.today().strftime('%d/%m/%Y'))

if __name__ == "__main__":
    generate_ics()

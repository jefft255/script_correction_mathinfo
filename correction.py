from pathlib import Path
import sys
import os

class NumberGrading:
    def __init__(self):
        self.team_number = -1
        self.number = -1
        self.grade = -1
        self.file_format_penalty = 0
        self.typo_penalty = 0
        self.other_comment = ""

    def to_text_file(self, path: Path):
        output_file = open(path, 'w')
        output_file.write(f"--- Équipe {self.team_number}, numéro {self.number} ---")
        output_file.write(f"Note: {self.grade}")
        output_file.write(f"Pénalité format de fichier: {self.file_format_penalty}")
        output_file.write(f"Pénalité fautes de français: {self.typo_penalty}")
        output_file.write(f"Autres commentaires: {self.other_comment}")
        output_file.close()


def ask_yesno(message: str, default: bool):
    while True:
        answer = input(f"{message} ---  O = oui, N = non (défaut: {'oui' if default else 'non'}).")
        if answer == "":
            return default
        elif answer.strip().lower in ["oui", "o"]:
            return true
        elif answer.strip().lower in ["non", "n"]:
            return false
        else:
            print("Réponse invalide, veuillez réessayer.")


def ask_grade(message: str, default: float):
    while True:
        answer = input(f"{message} --- (défaut: {default}).")
        if answer == "":
            return default
        try:
            return float(answer)
        except ValueError:
            print("Note invalide, veuillez réessayer.")


def open_in_default_application(path: Path):
    if sys.platform.startswith('darwin'):
        os.system('open', path)
    elif sys.platform.startswith('linux'):
        os.system('xdg-open', path)
    elif sys.platform.startswith('win32'):
        os.startfile(path)


number = sys.argv[1]
teams_path = Path(sys.argv[2])

for team_folder in teams_path.glob("Equipe *"):
    team_number = team_folder.name.split(" ")[-1]
    print(f"Correction de l'équipe {team_number}")
    correction = NumberGrading()
    correction.team_number = team_number
    correction.number = number

    if Path(team_folder / f"correction{number}.txt").exists():
        print(f"Correction pour l'équipe {team_number} déjà faite, on passe à la suivante.")
        continue

    files_for_number = team_folder.glob(f"**/*{number}.pdf")
    if len(files_for_number) > 1:  # TODO remises multiple, utiliser date modif
        print(f"""Erreur, plusieurs fichier correspondent au numéro {number}.
                  Manuellement trouver lequel est le bon.""")
    elif len(files_for_number) == 0:
        print(f"""Erreur, le fichier correspondant au numéro {number} pour l'équipe {team_number} est introuvable.
                  Veuillez le chercher manuellement.""")
        if ask_yesno("Est-ce que le fichier à été trouvé?", false):
            correction.file_format_penalty = ask_grade("Quelle pénalité donner à l'équipe?", 0)  # TODO quelle penalite donner?
        else:
            print("Le numéro n'a pas été fait, c'est donc 0.")
            correction.grade = 0
            correction.other_comment = "Numéro pas fait."
            correction.to_text_file(team_folder / f"correction{number}.txt")
            continue
    else:
        open_in_default_application(files_for_number[0])

    correction.grade = ask_grade("Après correction, quelle est la note?", 0)
    correction.other_comment = input("Écrire tout autre commentaire ici: ")
    correction.to_text_file(team_folder / f"correction{number}.txt")
    if ask_yesno("Voulez vous ouvrir le fichier de correction pour corriger vos erreurs?", false):
        open_in_default_application(team_folder / f"correction{numero}.txt")

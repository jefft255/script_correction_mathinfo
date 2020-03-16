from pathlib import Path
from utilitaires import NumberGrading, ask_grade, open_in_default_application
import sys


def ask_yesno(message: str, default: bool):
    while True:
        answer = input(f"{message} O = oui, N = non " +
                       f"(défaut: {'oui' if default else 'non'}): ")
        if answer == "":
            return default
        elif answer.strip().lower() in ["oui", "o"]:
            return True
        elif answer.strip().lower() in ["non", "n"]:
            return False
        else:
            print("Réponse invalide, veuillez réessayer.")


def correct_a_number(team_nb, nb, default):
    correction = NumberGrading(team_nb, nb)
    while correction.grade == -1:
        print_correction_choices(default)
        answer = input().strip().lower()
        if answer == "":
            correction.grade = int(default)
        elif answer.isnumeric():
            correction.grade = int(answer)
        elif answer == "f":
            correction.typo_penalty = ask_grade("Combien de fautes de français?", default="0")
        elif answer == "l":
            correction.readability_penalty = ask_grade("Quelle est la pénalité pour la lisibilité?", default="0")
        elif answer == "p":
            correction.other_penalty = ask_grade("Autre pénalité?", default="0")
        elif answer == "c":
            correction.other_comment = input("Écrire tout autre commentaire ici: ")
        elif answer == "x":
            return
        else:
            print("Choix invalide.")
    correction.to_text_file(team_folder / f"correction{number}.txt")


def print_correction_choices(default):
    print(f"\nEntrez la note (défaut: {default}) ou")
    print("autres choix: F -> entrer les fautes de français")
    print("              L -> pénalité de lisibilité")
    print("              P -> autre pénalité")
    print("              C -> autre commentaire")
    print("              X -> sauter cette équipe:")


def assert_number_of_arguments():
    if len(sys.argv) != 4:
        raise Exception("Utilisation: python correction.py numéro note_maximale dossier_équipes")


def collect_files_for_number(nb, folder):
    files = list(team_folder.glob(f"**/*{number}.pdf")) + \
            list(team_folder.glob(f"**/*{number}.PDF")) + \
            list(team_folder.glob(f"**/*{number}_retard.pdf")) + \
            list(team_folder.glob(f"**/*{number}_retard.PDF"))
    files_filtered = list(filter(lambda x: "__MACOSX" not in str(x), files))
    files_sorted = sorted(files_filtered, key=lambda x: x.stat().st_mtime, reverse=True)
    return files_sorted


if __name__ == "__main__":
    assert_number_of_arguments()
    number = sys.argv[1]
    max_grade = sys.argv[2]
    teams_path = Path(sys.argv[3])
    team_number_index = -1
    for team_folder in sorted(teams_path.glob("Equipe *"), key=lambda x: int(x.name.split(' ')[team_number_index])):
        team_number = team_folder.name.split(" ")[team_number_index]
        if Path(team_folder / f"correction{number}.txt").exists():
            print(f"Correction pour l'équipe {team_number} déjà faite, on passe à la suivante.")
        else:
            print(f"========================================\n--- Correction de l'équipe {team_number} ---")
            files_for_number = collect_files_for_number(number, team_folder)
            if len(files_for_number) == 0:
                print(f"!!Erreur!!, le fichier correspondant au numéro {number} " +
                      f"pour l'équipe {team_number} est introuvable. Normalement " +
                      "le professeur a reglé ce problème avec le script verification_arborescence.py.")
            else:
                open_in_default_application(files_for_number[0])
                correct_a_number(team_number, number, max_grade)

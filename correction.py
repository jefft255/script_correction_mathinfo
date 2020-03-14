from pathlib import Path
import os
import subprocess
import sys


class NumberGrading:
    def __init__(self):
        self.team_number = -1
        self.number = -1
        self.grade = -1
        self.typo_penalty = 0
        self.readability_penalty = 0
        self.other_penalty = 0
        self.other_comment = ""

    def to_text_file(self, path: Path):
        output_file = open(str(path), 'w')
        output_file.write(f"--- Équipe {self.team_number}, numéro {self.number} ---\n")
        output_file.write(f"Note: {self.grade}\n")
        output_file.write(f"Nombre de fautes de français: {self.typo_penalty}\n")
        output_file.write(f"Pénalité lisibilité: {self.readability_penalty}\n")
        output_file.write(f"Autre pénalité: {self.other_penalty}\n")
        output_file.write(f"Autres commentaires: {self.other_comment}")
        output_file.close()


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


def ask_grade(message: str, default=""):
    while True:
        answer = input(f"{message} {f'(défaut: {default})' if default != '' else ''}: ")
        if answer == "":
            return default
        else:
            try:
                answer = int(answer)
                assert(answer >= 0)
                return answer
            except ValueError:
                print("Note invalide, veuillez réessayer.")
            except AssertionError:
                print("La note ou la pénalité doit être positive.")


def open_in_default_application(path: Path):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', path))
    elif sys.platform.startswith('linux'):
        subprocess.call(('xdg-open', path))
    elif sys.platform.startswith('win32'):
        os.startfile(path)


def correction_choices(correction, number, default):
    while True:
        print(f"Entrez la note (défaut: {default}) ou")
        print("autres choix: F -> entrer les fautes de français")
        print("              L -> pénalité de lisibilité")
        print("              P -> autre pénalité")
        print("              C -> autre commentaire")
        print("              X -> sauter cette équipe:")
        answer = input()
        if answer == "":
            answer = default
        try:
            grade = int(answer)
            correction.grade = grade
            break
        except ValueError:
            answer = answer.strip().lower()
            if answer == "f":
                correction.typo_penalty = ask_grade("Combien de fautes de français?",
                                                    default="0")
            elif answer == "l":
                correction.readability_penalty = ask_grade("Quelle est la pénalité pour la " +
                                                           "lisibilité? Ne pas mettre de -.",
                                                           default="0")
            elif answer == "p":
                correction.other_penalty = ask_grade("Autre pénalité. Ne pas mettre de -.",
                                                     default="0")
            elif answer == "c":
                correction.other_comment = input("Écrire tout autre commentaire ici: ")
            elif answer == "x":
                print("On saute l'équipe.")
                return  # return skips the last saving line. Hacky but works
            else:
                print("Choix invalide.")
    correction.to_text_file(team_folder / f"correction{number}.txt")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Utilisation: python correction.py numéro note_maximale dossier_équipes")

    number = sys.argv[1]
    max_grade = sys.argv[2]
    teams_path = Path(sys.argv[3])

    for team_folder in sorted(teams_path.glob("Equipe *"),
                              key=lambda x: int(str(x.name).split(' ')[-1])):
        team_number = team_folder.name.split(" ")[-1]
        correction = NumberGrading()
        correction.team_number = team_number
        correction.number = number

        if Path(team_folder / f"correction{number}.txt").exists():
            print(f"Correction pour l'équipe {team_number} déjà faite, " +
                  "on passe à la suivante.")
            continue

        print("========================================")
        print(f"--- Correction de l'équipe {team_number} ---")

        files_for_number = list(team_folder.glob(f"**/*{number}.pdf")) + \
            list(team_folder.glob(f"**/*{number}.PDF")) + \
            list(team_folder.glob(f"**/*{number}_retard.pdf")) + \
            list(team_folder.glob(f"**/*{number}_retard.PDF"))
        files_for_number = list(filter(lambda x: "__MACOSX" not in str(x), files_for_number))
        if len(files_for_number) > 1:  # Grade the most recent homework
            print("Plusieurs remise, la plus récente va être ouverte.")
            print(list(map(lambda x: x.stat().st_mtime, files_for_number)))
            files_for_number.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if len(files_for_number) == 0:
            print(f"!!Erreur!!, le fichier correspondant au numéro {number} " +
                  f"pour l'équipe {team_number} est introuvable. Normalement " +
                  "le professeur a reglé ce problème avec le script " +
                  "verification_arborescence.py.")
            continue
        else:
            open_in_default_application(files_for_number[0])

        correction_choices(correction, number, max_grade)

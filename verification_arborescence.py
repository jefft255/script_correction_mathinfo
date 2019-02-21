from pathlib import Path
import sys
import os
import subprocess


class PathVerification:
    def __init__(self):
        self.team_number = -1
        self.invalid_numbers = []
        self.penalty = 0

    def to_text_file(self, path: Path):
        output_file = open(path, 'w')
        if len(self.invalid_numbers) == 0:
            output_file.write("Format des fichiers valide, pas de pénalité.")
        else:
            output_file.write(f"{self.penalty} points de pénalité car ")
            if len(self.invalid_numbers) > 1:
                output_file.write("les fichiers des numéros")
                for i, number in enumerate(self.invalid_numbers):
                    if i == len(self.invalid_numbers) - 1:
                        end_char = " "
                    elif i == len(self.invalid_numbers) - 2:
                        end_char = "et "
                    else:
                        end_char = ", "
                    output_file.write(f"{number}{end_char}")
                output_file.write("ont un nom invalide.")
            else:
                output_file.write("le fichier du numéros {self.invalid_numbers[0]} a un nom invalide.")



if sys.argc != 3:
    print("Utilisation: python3 verification_arborescence.py nombre_de_numero dossier_equipes")

numbers = sys.argv[1]
teams_path = Path(sys.argv[2])

for team_folder in sorted(teams_path.glob("Equipe *")):
    team_number = team_folder.name.split(" ")[-1]
    correction = NumberGrading()
    correction.team_number = team_number
    correction.number = number

    if Path(team_folder / f"penalite_globale.txt").exists():
        print(f"Verification pour l'équipe {team_number} déjà faite, on passe à la suivante.")
        continue

    print("========================================")
    print(f"--- Verification de l'équipe {team_number} ---")

    for number in range(1, numbers + 1):
        files_for_number = list(team_folder.glob(f"**/*{number}.pdf"))
        if len(files_for_number) > 1:  # Grade the most recent homework
            files_for_number.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if len(files_for_number) == 0:
            print(f"""Erreur, le fichier correspondant au numéro {number} pour l'équipe {team_number} est introuvable. Veuillez le chercher manuellement.""")
            if ask_yesno("Est-ce que le fichier à été trouvé?", False):
            else:
                print("Le numéro n'a pas été fait, c'est donc 0.")
                correction.grade = 0
                correction.other_comment = "Numéro pas fait."
                correction.to_text_file(team_folder / f"correction{number}.txt")
                continue
        else:
            open_in_default_application(files_for_number[0])

    correction.file_format_penalty = ask_grade("Quelle pénalité donner à l'équipe? Ne pas mettre de -.", 0)  # TODO quelle penalite donner?
    correction.to_text_file(team_folder / f"correction{number}.txt")
    if ask_yesno("Voulez vous ouvrir le fichier de correction pour corriger vos erreurs?", False):
        open_in_default_application(team_folder / f"correction{number}.txt")

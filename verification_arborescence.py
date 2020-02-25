from pathlib import Path
import sys
import os
import subprocess

from correction import NumberGrading, ask_yesno, ask_grade, open_in_default_application

class PathVerification:
    def __init__(self):
        self.team_number = -1
        self.invalid_numbers = []
        self.penalty = 0

    def to_text_file(self, path: Path):
        assert(self.team_number != -1)
        output_file = open(path, 'w')
        if len(self.invalid_numbers) == 0:
            output_file.write("Format des fichiers valide, pas de pénalité.")
        else:
            output_file.write(f"{self.penalty} points de pénalité car ")
            if len(self.invalid_numbers) > 1:
                output_file.write("les fichiers des numéros ")
                for i, number in enumerate(self.invalid_numbers):
                    if i == len(self.invalid_numbers) - 1:
                        end_char = " "
                    elif i == len(self.invalid_numbers) - 2:
                        end_char = " et "
                    else:
                        end_char = ", "
                    output_file.write(f"{number}{end_char}")
                output_file.write("ont un nom invalide.")
            else:
                output_file.write(f"le fichier du numéros {self.invalid_numbers[0]} " +
                                  "a un nom invalide.")
        output_file.close()



if len(sys.argv) != 3:
    print("Utilisation: python3 verification_arborescence.py nombre_de_numero dossier_equipes")

numbers = int(sys.argv[1])
teams_path = Path(sys.argv[2])
penalty_filename = "penalite_globale.txt"

for team_folder in sorted(teams_path.glob("Equipe *"),
                          key=lambda x: int(str(x.name).split(' ')[-1])):
    verif = PathVerification()
    verif.team_number = team_folder.name.split(" ")[-1]

    if Path(team_folder / f"penalite_globale.txt").exists():
        print(f"Verification pour l'équipe {verif.team_number} " +
              "déjà faite, on passe à la suivante.")
        continue

    print("========================================")
    print(f"--- Verification de l'équipe {verif.team_number} ---")

    # First pass, find problems
    for number in range(1, numbers + 1):
        files_for_number = list(team_folder.glob(f"**/*{number}.pdf")) + \
                           list(team_folder.glob(f"**/*{number}.PDF")) + \
                           list(team_folder.glob(f"**/*{number}_retard.pdf")) + \
                           list(team_folder.glob(f"**/*{number}_retard.PDF"))

        if len(files_for_number) == 0:
            print(f"Erreur, le fichier correspondant au numéro {number} " +
                  f"pour l'équipe {verif.team_number} est introuvable. " +
                  "Veuillez le chercher manuellement.")

            verif.invalid_numbers.append(number)

    if len(verif.invalid_numbers) > 0:
        open_in_default_application(team_folder)

        if not ask_yesno("Anomalies corrigées? O: Elles ont été corrigées, les numéros non-faits vont avoir 0; N: Non, je veux sauter cette équipe", True):
            continue

        # Second pass, find actual missing numbers
        for number in range(1, numbers + 1):
            files_for_number = list(team_folder.glob(f"**/*{number}.pdf")) + \
                               list(team_folder.glob(f"**/*{number}.PDF"))

            if len(files_for_number) == 0:
                print(f"Le numéro {number} n'a pas été fait, c'est donc 0.")
                correction = NumberGrading()
                correction.team_number = verif.team_number
                correction.number = number
                correction.grade = 0
                correction.other_comment = "Numéro pas fait."
                correction.to_text_file(team_folder / f"correction{number}.txt")
                verif.invalid_numbers.remove(number)
                continue

    if len(verif.invalid_numbers) > 0:
        print(f"Numéros invalides: {verif.invalid_numbers}")
        verif.penalty = ask_grade("Quelle pénalité donner à l'équipe? Ne pas mettre de -.")
    else:
        print("Tous les numéros qui ont été faits sont valides!")
    verif.to_text_file(team_folder / penalty_filename)

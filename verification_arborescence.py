from utilitaires import NumberGrading, ask_grade, open_in_default_application
from pathlib import Path

import re
import sys


class PathVerification:
    def __init__(self):
        self.team_number = -1
        self.invalid_numbers = []
        self.penalty = 0
        self.comment = ""

    def to_text_file(self, path):
        assert(self.team_number != -1)
        output_file = open(path, 'w')
        if len(self.invalid_numbers) == 0:
            output_file.write("Format des fichiers valide, pas de pénalité.")
        else:
            output_file.write(f"{self.penalty} points de pénalité car ")
            if len(self.invalid_numbers) > 1:
                output_file.write("les fichiers des numéros ")
                for i, exercise_number in enumerate(self.invalid_numbers):
                    if i == len(self.invalid_numbers) - 1:
                        end_char = " "
                    elif i == len(self.invalid_numbers) - 2:
                        end_char = " et "
                    else:
                        end_char = ", "
                    output_file.write(f"{exercise_number}{end_char}")
                output_file.write("ont un nom invalide.")
            else:
                output_file.write(f"le fichier du numéro {self.invalid_numbers[0]} a un nom invalide.")
            output_file.write(" " + self.comment)
        output_file.close()


def is_present(exercise_number_to_verify, folder):
    files = list(folder.glob(f"**/*{exercise_number_to_verify}.pdf")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}.PDF")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}_retard.pdf")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}_retard.PDF"))
    return len(files) > 0


def is_illformed(exercise_number_to_verify, folder):
    files = list(folder.glob(f"**/*{exercise_number_to_verify}*.pdf")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}*.PDF")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}*_retard.pdf")) + \
            list(folder.glob(f"**/*{exercise_number_to_verify}*_retard.PDF"))
    regex = r".*[a-zA-Z]\.(pdf|PDF)"
    regex_retard = r".*[a-zA-Z]_retard\.(pdf|PDF)"
    files = list(filter(lambda f: re.match(regex, str(f)) or re.match(regex_retard, str(f)), files))
    return len(files) > 0


def is_containing_enough_answers(number_of_exercises_in_tp, folder):
    files = list(folder.glob("**/*.pdf")) + list(folder.glob("**/*.PDF"))
    return len(files) >= number_of_exercises_in_tp


def find_problematic_exercises(folder):
    invalid_numbers = []
    for exercise_number_to_verify in range(1, number_of_exercises_in_TP + 1):
        if is_present(exercise_number_to_verify, folder):
            continue
        elif is_illformed(exercise_number_to_verify, folder):
            print(f"AVERTISSEMENT: le fichier correspondant au numéro {exercise_number_to_verify} est mal formé.")
            invalid_numbers.append(exercise_number_to_verify)
        elif not is_containing_enough_answers(number_of_exercises_in_TP, folder):
            mark_zero_for_an_exercise_not_done(exercise_number_to_verify)
        else:
            print(f"AVERTISSEMENT: le fichier correspondant au numéro {exercise_number_to_verify} " +
                  "échappe à nos règles. Est-il possible d'en créer une nouvelle pour éviter cette situation?")
            invalid_numbers.append(exercise_number_to_verify)
    return invalid_numbers


def mark_zero_for_an_exercise_not_done(number_of_the_exercise_not_done):
    print(f"AVERTISSEMENT: le numéro {number_of_the_exercise_not_done} n'a pas été fait, c'est donc 0.")
    mark_of_the_exercise = NumberGrading()
    mark_of_the_exercise.team_number = team_folder_to_verify.team_number
    mark_of_the_exercise.number = number_of_the_exercise_not_done
    mark_of_the_exercise.grade = 0
    mark_of_the_exercise.other_comment = "Numéro pas fait."
    mark_of_the_exercise.to_text_file(team_folder / f"correction{number_of_the_exercise_not_done}.txt")


def assert_number_of_arguments():
    if len(sys.argv) != 3:
        raise Exception("Utilisation: python3 verification_arborescence.py nombre_de_numero dossier_equipes")


def is_team_skipped():
    answer = input("\nAnomalies corrigées?\nO: Oui, elles sont corrigées. Les numéros non-faits vont avoir 0."
                   "\nX: Sauter cette équipe.\nVotre choix (défaut: oui): ")
    skipped = False
    if answer.strip().lower() == "x":
        skipped = True
    return skipped


if __name__ == '__main__':
    assert_number_of_arguments()

    number_of_exercises_in_TP = int(sys.argv[1])
    teams_path = Path(sys.argv[2])
    penalty_filename = "penalite_globale.txt"

    for team_folder in sorted(teams_path.glob("Equipe *"), key=lambda x: int(str(x.name).split(' ')[-1])):
        team_folder_to_verify = PathVerification()
        team_folder_to_verify.team_number = team_folder.name.split(" ")[-1]

        if Path(team_folder / f"{penalty_filename}").exists():
            print(f"Vérification pour l'équipe {team_folder_to_verify.team_number} déjà faite, on passe à la suivante.")
            continue

        print("========================================")
        print(f"--- Vérification de l'équipe {team_folder_to_verify.team_number} ---")

        # First pass, find problems
        team_folder_to_verify.invalid_numbers.extend(find_problematic_exercises(team_folder))

        if len(team_folder_to_verify.invalid_numbers) > 0:
            open_in_default_application(team_folder)

            if is_team_skipped():
                continue

        # Second pass, find actual missing numbers
        for number in range(1, number_of_exercises_in_TP + 1):
            files_for_number = list(team_folder.glob(f"**/*{number}.pdf")) + \
                               list(team_folder.glob(f"**/*{number}.PDF")) + \
                               list(team_folder.glob(f"**/*{number}_retard.pdf")) + \
                               list(team_folder.glob(f"**/*{number}_retard.PDF"))
            correction_files_for_number = list(team_folder.glob(f"**/correction{number}.txt"))
            if len(files_for_number) + len(correction_files_for_number) == 0:
                mark_zero_for_an_exercise_not_done(number)

        if len(team_folder_to_verify.invalid_numbers) > 0:
            print(f"Numéros invalides: {team_folder_to_verify.invalid_numbers}")
            team_folder_to_verify.penalty = ask_grade("Quelle pénalité donner à l'équipe? Ne pas mettre de -.")
            team_folder_to_verify.comment = input("Quel est votre commentaire par rapport à la pénalité? : ")
        else:
            print("Tous les numéros qui ont été faits sont valides!")
        team_folder_to_verify.to_text_file(team_folder / penalty_filename)

from utilitaires import NumberGrading, ask_grade, open_in_default_application
from pathlib import Path

import re
import sys


PENALTY_FILENAME = "penalite_globale.txt"
TEAM_NUMBER_INDEX = -1


class PathVerification:
    def __init__(self, team_number, invalid_numbers):
        self.team_number = team_number
        self.invalid_numbers = invalid_numbers
        self.penalty = 0
        self.comment = "Format des fichiers valide, pas de pénalité."

    def to_text_file(self, path):
        output_file = open(path, 'w')
        if len(self.invalid_numbers) > 0:
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


def is_present(exercise_number_to_verify, team_folder):
    files = list(team_folder.glob(f"**/*{exercise_number_to_verify}.pdf")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}.PDF")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}_retard.pdf")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}_retard.PDF"))
    return len(files) > 0


def is_illformed(exercise_number_to_verify, team_folder):
    files = list(team_folder.glob(f"**/*{exercise_number_to_verify}*.pdf")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}*.PDF")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}*_retard.pdf")) + \
            list(team_folder.glob(f"**/*{exercise_number_to_verify}*_retard.PDF"))
    regex = r".*[a-zA-Z]\.(pdf|PDF)"
    regex_retard = r".*[a-zA-Z]_retard\.(pdf|PDF)"
    files = list(filter(lambda f: re.match(regex, str(f)) or re.match(regex_retard, str(f)), files))
    return len(files) > 0


def is_containing_enough_answers(number_of_exercises_in_tp, team_folder):
    files = list(team_folder.glob("**/*.pdf")) + list(team_folder.glob("**/*.PDF"))
    return len(files) >= number_of_exercises_in_tp


def find_problematic_exercises(team_folder):
    invalid_numbers = []
    for exercise_number_to_verify in range(1, number_of_exercises_in_TP + 1):
        if is_present(exercise_number_to_verify, team_folder):
            continue
        elif is_illformed(exercise_number_to_verify, team_folder):
            print(f"AVERTISSEMENT: le fichier correspondant au numéro {exercise_number_to_verify} est mal formé.")
            invalid_numbers.append(exercise_number_to_verify)
        elif not is_containing_enough_answers(number_of_exercises_in_TP, team_folder):
            mark_zero_for_an_exercise_not_done(exercise_number_to_verify, team_folder)
        else:
            print(f"AVERTISSEMENT: le fichier correspondant au numéro {exercise_number_to_verify} " +
                  "échappe à nos règles. Est-il possible d'en créer une nouvelle pour éviter cette situation?")
            invalid_numbers.append(exercise_number_to_verify)
    return invalid_numbers


def mark_zero_for_an_exercise_not_done(number_of_the_exercise_not_done, team_folder):
    print(f"AVERTISSEMENT: le numéro {number_of_the_exercise_not_done} n'a pas été fait, c'est donc 0.")
    team_number = team_folder.name.split(" ")[TEAM_NUMBER_INDEX]
    mark_of_the_exercise = NumberGrading(team_number, number_of_the_exercise_not_done)
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


def verify_naming_of_files_for_a_team(team_folder, nb_of_exercises):
    team_number = team_folder.name.split(" ")[TEAM_NUMBER_INDEX]
    if team_number == 26:
        print("yolo")
    if Path(team_folder / f"{PENALTY_FILENAME}").exists():
        print(f"Vérification pour l'équipe {team_number} déjà faite, on passe à la suivante.")
    else:
        print(f"========================================\n--- Vérification de l'équipe {team_number} ---")
        invalid_numbers = find_problematic_exercises(team_folder)
        if len(invalid_numbers) == 0:
            print("Tous les numéros qui ont été faits sont valides!")
        else:
            treat_invalid_numbers(invalid_numbers, nb_of_exercises, team_folder)


def treat_invalid_numbers(invalid_numbers, nb_of_exercises, team_folder):
    open_in_default_application(team_folder)
    if not is_team_skipped():
        mark_zero_to_all_invalid_numbers(nb_of_exercises, team_folder)
        team_number = team_folder.name.split(" ")[TEAM_NUMBER_INDEX]
        verified_data = PathVerification(team_number, invalid_numbers)
        if len(invalid_numbers) > 0:
            print(f"Numéros invalides: {invalid_numbers}")
            verified_data.penalty = ask_grade("Quelle pénalité donner à l'équipe? Ne pas mettre de -.")
            verified_data.comment = input("Quel est votre commentaire par rapport à la pénalité? : ")
        verified_data.to_text_file(team_folder / PENALTY_FILENAME)


def mark_zero_to_all_invalid_numbers(nb_of_exercises, team_folder):
    for number in range(1, nb_of_exercises + 1):
        files_for_number = list(team_folder.glob(f"**/*{number}.pdf")) + \
                           list(team_folder.glob(f"**/*{number}.PDF")) + \
                           list(team_folder.glob(f"**/*{number}_retard.pdf")) + \
                           list(team_folder.glob(f"**/*{number}_retard.PDF"))
        correction_files_for_number = list(team_folder.glob(f"**/correction{number}.txt"))
        if len(files_for_number) + len(correction_files_for_number) == 0:
            mark_zero_for_an_exercise_not_done(number, team_folder)


if __name__ == '__main__':
    assert_number_of_arguments()
    number_of_exercises_in_TP = int(sys.argv[1])
    teams_path = Path(sys.argv[2])
    for folder in sorted(teams_path.glob("Equipe *"), key=lambda x: int(x.name.split(' ')[TEAM_NUMBER_INDEX])):
        verify_naming_of_files_for_a_team(folder, number_of_exercises_in_TP)

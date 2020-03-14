from pathlib import Path
from xlutils.copy import copy

import sys
import xlrd


class Result:
    def __init__(self, team_number):
        self.team_number = team_number
        self.grades = []
        self.global_penalty = 0
        self.nb_of_french_mistakes = 0
        self.readability_penalty = 0
        self.other_penalty = 0
        self.comment = ""

    def get_total_penalty(self):
        french_penalty_value = 0.5
        penalty = (french_penalty_value * self.nb_of_french_mistakes) + self.readability_penalty \
            + self.global_penalty + self.other_penalty
        max_penalty = 10
        return penalty if penalty <= max_penalty else max_penalty

    def get_comment(self):
        comment = ""
        if self.comment != "":
            comment += self.comment
        if self.global_penalty > 0:
            comment += "Pénalité globale: -" + str(self.global_penalty) + ".\n"
        if self.nb_of_french_mistakes > 0:
            french_penalty_value = 0.5
            comment += "Fautes fr: -" + str(french_penalty_value * self.nb_of_french_mistakes) + ".\n"
        if self.readability_penalty > 0:
            comment += "Lisibilité: -" + str(self.readability_penalty) + ".\n"
        if self.other_penalty > 0:
            comment += "Autre pénalité: -" + str(self.other_penalty) + ".\n"
        return comment


def collect_results_for_all_teams(nb_of_exercises, input_path):
    list_of_results = []
    for team_folder in sorted(input_path.glob("Equipe *"), key=lambda x: int(str(x.name).split(' ')[-1])):
        team_number = team_folder.name.split(" ")[-1]
        print_collecting_start(team_number)
        list_of_results.append(collect_result_for_a_team(team_number, nb_of_exercises, team_folder))
        print_collecting_end(team_number)
    return list_of_results


def print_collecting_start(team_number):
    print("---------------------------------------------------------------------------")
    print(f"--- Récupération des notes de l'équipe {team_number} commencée. ---")


def print_collecting_end(team_number):
    print(f"--- Récupération des notes de l'équipe {team_number} terminée. ---")
    print("---------------------------------------------------------------------------\n")


def collect_result_for_a_team(team_nb, nb_ex, team_dir):
    result = Result(team_nb)
    collect_global_penalty_for_a_team(team_nb, team_dir, result)
    for nb in range(1, nb_ex + 1):
        path = Path(team_dir / f"correction{nb}.txt")
        try:
            collect_result_from_file_with_unix_encoding(path, nb, result)
        except ValueError:
            collect_result_from_file_with_windows_encoding(path, nb, result)
        except Exception:
            raise Exception("Le fichier de correction du numéro " + str(nb) + " de l'équipe " + str(team_nb)
                            + " est manquant ou son encodage est invalide. Veuillez corriger ce problème et "
                            + "relancez le script.")
    return result


def collect_global_penalty_for_a_team(team_nb, team_folder, result):
    path = Path(team_folder / "penalite_globale.txt")
    try:
        penalty_file = open(path, encoding='utf-8')
        add_global_penalty_to_a_result(penalty_file, result)
        penalty_file.close()
    except Exception:
        raise Exception("Le fichier de pénalité globale de l'équipe " + str(team_nb)
                        + " est manquant ou son encodage est invalide. Veuillez corriger ce problème et "
                        + "relancez le script.")


def add_global_penalty_to_a_result(penalty_file, result):
    penalty_text = penalty_file.read().split(" ")
    penalty = -1
    try:
        data_index = 1
        penalty = float(penalty_text[data_index])
    except ValueError:
        penalty = 0
    finally:
        result.global_penalty = penalty


def collect_result_from_file_with_unix_encoding(path, number, result):
    exercise_file = open(path, encoding='utf-8')
    complete_result_from_file(exercise_file, number, result)
    exercise_file.close()


def collect_result_from_file_with_windows_encoding(path, number, result):
    exercise_file = open(path, encoding='iso-8859-1')
    complete_result_from_file(exercise_file, number, result)
    exercise_file.close()


def complete_result_from_file(file, number, result):
    for line in file.readlines():
        data_index = 1
        components = line.split(": ")
        if "Note" in line:
            result.grades.append(int(components[data_index]))
        elif "français" in line:
            result.nb_of_french_mistakes += int(components[data_index])
        elif "lisibilité" in line:
            result.readability_penalty += int(components[data_index])
        elif "Autre pénalité" in line:
            result.other_penalty += int(components[data_index])
        elif "Autres commentaires" in line and is_valid_comment(components[data_index]):
            result.comment += "No. " + str(number) + ": " + components[data_index] + "\n"


def is_valid_comment(comment):
    return comment != "" and comment != "\n"


def write_all_results_in_excel_grid(list_of_results, output_path):
    excel_grid = xlrd.open_workbook(output_path)
    excel_grid_copy = copy(excel_grid)
    grades_sheet = 0
    active_sheet_r_mode = excel_grid.sheet_by_index(grades_sheet)
    active_sheet_w_mode = excel_grid_copy.get_sheet(grades_sheet)
    for result in list_of_results:
        write_a_result_in_excel_grid(active_sheet_r_mode, active_sheet_w_mode, result)
        excel_grid_copy.save(output_path)


def write_a_result_in_excel_grid(active_sheet_r_mode, active_sheet_w_mode, result):
    writing = False
    reading = True
    row_index = 0
    team_index = 1
    first_grade_index = 6
    penalty_index = first_grade_index + len(result.grades) + 3
    comment_index = penalty_index + 1
    while row_index < active_sheet_r_mode.nrows and reading:
        cell_value = active_sheet_r_mode.cell_value(row_index, team_index)
        if f"Équipe {result.team_number}" in str(cell_value):
            writing = True
        elif ("Équipe " in str(cell_value) or "Moyenne " in str(cell_value)) and writing:
            reading = False
        elif "Abandon" not in str(cell_value) and writing:
            for number in range(0, len(result.grades)):
                active_sheet_w_mode.write(row_index, first_grade_index + number, result.grades[number])
            active_sheet_w_mode.write(row_index, penalty_index, result.get_total_penalty())
            active_sheet_w_mode.write(row_index, comment_index, result.get_comment())
        row_index += 1


if __name__ == '__main__':
    if len(sys.argv[1]) != 4:
        print("Utilisation: python compiler.py nombre_exercices dossier_équipes grille_des_résultats")
    number_of_exercises = int(sys.argv[1])
    team_path = Path(sys.argv[2])
    grade_sheet_path = Path(sys.argv[3])
    print("===========================================================================\n\n"
          "Début de la compilation des notes.\n\n")
    results = collect_results_for_all_teams(number_of_exercises, team_path)
    print("===========================================================================\n\n"
          "Tous les résultats ont été récupérés.\n\nDébut de l'écriture des notes dans la grille des résultats.\n\n")
    write_all_results_in_excel_grid(results, grade_sheet_path)
    print("===========================================================================\n\n"
          "L'écriture des notes est terminée. Vérifiez quelques équipes pour valider la sortie du script.")

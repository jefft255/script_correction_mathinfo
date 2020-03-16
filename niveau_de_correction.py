from pathlib import Path
import sys


def count_number_of_exercises_yet_to_correct():
    nbr_of_exercises_yet_to_correct = 0
    for team_folder in sorted(teams_path.glob("Equipe *"), key=lambda x: int(x.name.split(' ')[-1])):
        numbers_of_exercises_yet_to_correct = collect_numbers_of_exercises_yet_to_correct_for_a_team(team_folder)
        nbr_of_exercises_yet_to_correct += len(numbers_of_exercises_yet_to_correct)
        print_correction_message_for_a_team(numbers_of_exercises_yet_to_correct, team_folder.name.split(' ')[1])
    return nbr_of_exercises_yet_to_correct


def collect_numbers_of_exercises_yet_to_correct_for_a_team(team_folder):
    numbers_not_corrected_of_the_team = []
    for exercise_number in range(1, number_of_exercises + 1):
        if not Path(team_folder / f"correction{exercise_number}.txt").exists():
            numbers_not_corrected_of_the_team.append(exercise_number)
    return numbers_not_corrected_of_the_team


def print_correction_message_for_a_team(numbers_of_exercises_yet_to_correct_of_a_team, team_number):
    if numbers_of_exercises_yet_to_correct_of_a_team:
        print(f"Il manque la correction des numéros "
              f"{', '.join(map(str, numbers_of_exercises_yet_to_correct_of_a_team))} de l'équipe {team_number}.")


def assert_number_of_arguments():
    if len(sys.argv) != 3:
        raise Exception("Utilisation: python niveau_de_correction.py nbr_exercices dossier_équipes")


if __name__ == "__main__":
    assert_number_of_arguments()
    number_of_exercises = int(sys.argv[1])
    teams_path = Path(sys.argv[2])
    number_of_exercises_yet_to_correct = count_number_of_exercises_yet_to_correct()
    number_of_teams = len([team for team in teams_path.iterdir() if team.is_dir()])
    print(f"La correction est faite à "
          f"{100 * (1 - number_of_exercises_yet_to_correct / (number_of_exercises * number_of_teams))}%.")

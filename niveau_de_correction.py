from pathlib import Path
import sys


def count_number_of_exercises_yet_to_correct():
    nbr_of_exercises_yet_to_correct = 0
    for team_folder in sorted(teams_path.glob("Equipe *"),
                              key=lambda x: int(str(x.name).split(' ')[-1])):
        for exercise_number in range(1, number_of_exercises + 1):
            correction_file_path = Path(team_folder / f"correction{exercise_number}.txt")
            if not correction_file_path.exists():
                print(f"Le fichier {correction_file_path} est introuvable.")
                nbr_of_exercises_yet_to_correct += 1
    return nbr_of_exercises_yet_to_correct


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

from pathlib import Path
import sys


if __name__ == "__main__":
    if len(sys.argv[1]) != 3:
        print("Utilisation: python niveau_de_correction.py nbr_exercices dossier_équipes")
    number_of_exercises = int(sys.argv[1])
    teams_path = Path(sys.argv[2])
    number_of_exercises_not_corrected = 0
    for team_folder in sorted(teams_path.glob("Equipe *"),
                              key=lambda x: int(str(x.name).split(' ')[-1])):
        for exercise_number in range(1, number_of_exercises + 1):
            path = Path(team_folder / f"correction{exercise_number}.txt")
            try:
                exercise_file = open(path, encoding='utf-8')
                exercise_file.close()
            except OSError:
                print(f"ERREUR: Le fichier {path} est introuvable.")
                number_of_exercises_not_corrected += 1
            except ValueError:
                exercise_file = open(path, encoding='iso-8859-1')
                exercise_file.close()
    number_of_teams = len([team for team in teams_path.iterdir() if team.is_dir()])
    print(f"La correction est faite à "
          f"{100 * (1 - number_of_exercises_not_corrected / (number_of_exercises * number_of_teams))}%.")

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
import sys
import os
import subprocess

# Ajouter le chemin local des modules de Robot Framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dependance/robot-framework', 'bin/robot.exe'))

def run_robot(robot_file):
    try:
        # Commande pour exécuter le fichier .robot
        result = subprocess.run(['robot', robot_file], capture_output=True, text=True, shell=True)
        
        # Affichage de la sortie et des erreurs
        print("Output:\n", result.stdout)
        print("Errors:\n", result.stderr)
        
        # Vérifiez si le processus s'est terminé avec succès
        if result.returncode != 0:
            print(f"Robot Framework returned non-zero exit status {result.returncode}")
            sys.exit(result.returncode)
    except Exception as e:
        print(f"Exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_robot("tasks.robot")


# import subprocess
# import sys

# def run_robot(robot_file):
#     try:
#         # Commande pour exécuter le fichier .robot
#         result = subprocess.run(['robot', robot_file], capture_output=True, text=True, shell=True)
        
#         # Affichage de la sortie et des erreurs
#         print("Output:\n", result.stdout)
#         print("Errors:\n", result.stderr)
        
#         # Vérifiez si le processus s'est terminé avec succès
#         if result.returncode != 0:
#             print(f"Robot Framework returned non-zero exit status {result.returncode}")
#             sys.exit(result.returncode)
#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     run_robot("tasks.robot")


# import subprocess
# import sys
# import os

# def main():
#     try:
#         robot_file = sys.argv[1]
        
#         # Vérifier l'existence du fichier robot
#         if not os.path.isfile(robot_file):
#             raise FileNotFoundError(f"Le fichier spécifié est introuvable: {robot_file}")
        
#         # Définir le chemin vers l'exécutable Python dans l'environnement virtuel
#         venv_python = os.path.join('robot_env', 'Scripts', 'python.exe')
#         if not os.path.isfile(venv_python):
#             raise FileNotFoundError(f"Le fichier Python dans l'environnement virtuel est introuvable: {venv_python}")
        
#         # Commande pour exécuter le fichier .robot
#         cmd = [venv_python, '-m', 'robot', robot_file]
        
#         # Exécuter la commande et capturer la sortie
#         result = subprocess.run(cmd, capture_output=True, text=True)
        
#         print("Standard Output:", result.stdout)
#         print("Standard Error:", result.stderr)
#         print("Return Code:", result.returncode)
        
#         # Vérifier le code de retour
#         if result.returncode != 0:
#             raise Exception(f"Erreur lors de l'exécution de Robot Framework: {result.stderr}")
        
#     except Exception as e:
#         print(f"Exception occurred: {e}")

# if __name__ == "__main__":
#     main()


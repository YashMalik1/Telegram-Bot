import subprocess

# Path to your python in the env
pythonBinary = "python3"

# Path to your manage.py file
mainPy = "./main.py"

subprocess.Popen([pythonBinary, mainPy])

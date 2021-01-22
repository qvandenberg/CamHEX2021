# CamHEX2021
Repository for the Cambridge HEX event.

# Group members
<ul>
  <li>Raquel Manzano</li>
  <li>Quincy van den Berg</li>
  <li>torus403</li>
  <li>kitfunso</li>
  <li>gg1998</li>
</ul>

# Install instructions
This code runs in a virtual environment (venv or conda) that is described by the `requirements.txt` file. See https://docs.python.org/3/library/venv.html for details. Below instructions are for using pip on a Linux/OS X system. Use the link for a Windows system with conda.

<ol>
  <li>Create new (empty) Python 3 environment on your local system, e.g. `python3 -m venv /path/to/new/virtual/environment`</li>
</ol>
2.) Activate your environment: `source </path/to/new/virtual/environment>/bin/activate`
3.) Navigate to path where you want to clone this repository
4.) git clone <http link> to clone this repository to your system
5.) Enter root folder of repository
6.) Install all existing dependencies of the project into your venv: `pip install requirements.txt`
7.) If you add new packages/dependencies, install them the regular way while you are in your venv. Then to add them to the `requirements.txt` file, use a command like `pip freeze > requirements.txt` so that new packages are added. 
8.) Commit changes and push/pull request to remote repository


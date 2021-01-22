# CamHEX2021
Repository for the Cambridge HEX event for one of the finance/trading challenges.

## Install instructions
This code runs in a virtual environment (venv or conda) that is described by the `requirements.txt` file. See https://docs.python.org/3/library/venv.html for details. Below instructions are for using pip on a Linux/OS X system. Use the link for a Windows system with conda.

<ol>
  <li>Create new (empty) Python 3 environment on your local system, e.g. `python3 -m venv /path/to/new/virtual/environment` </li>
  <li>Activate your environment: `source </path/to/new/virtual/environment>/bin/activate` </li>
  <li>Navigate to path where you want to clone this repository </li>
  <li>git clone <http link> to clone this repository to your system</li>
  <li>Enter root folder of repository</li>
  <li>Install all existing dependencies of the project into your venv: `pip install requirements.txt`</li>
  <li>If you add new packages/dependencies, install them the regular way while you are in your venv. Then to add them to the `requirements.txt` file, use a command like `pip freeze > requirements.txt` so that new packages are added. </li>
  <li> Commit changes and push/pull request to remote repository</li>
</ol>

## Useful articles about technical indicators
Articles about implementing trading algorithms based on simple technical indicators.
<ul>
<li>https://medium.com/swlh/4-technical-indicators-i-use-in-technical-analysis-b065c8737823</li>
<li>https://medium.com/swlh/creating-a-contrarian-indicator-using-moving-averages-in-python-de898d9f29c2</li>
<li>https://kvbprime.medium.com/how-to-use-moving-averages-when-trading-61f2df9ed14f</li>
<li>https://towardsdatascience.com/how-to-create-a-fully-automated-ai-based-trading-system-with-python-708503c1a907</li>
</ul>

A possible 5th: Inbalance in the order book. I couldn't find an easy-to-read article so quickly, but generally the buy vs sell order volume says something about near-future price movements too.

## Group members
<ul>
  <li>Raquel Manzano</li>
  <li>Quincy van den Berg</li>
  <li>torus403</li>
  <li>kitfunso</li>
  <li>gg1998</li>
</ul>

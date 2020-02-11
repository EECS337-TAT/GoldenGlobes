Golden Globe Project
By Thomas Barnett, Alex Banta, and Titus Pahn
Github repository at https://github.com/EECS337-TAT/GoldenGlobes

Before running the project:

-Install requirements.txt (pip install -r requirements.txt)
-Download NLTK data:
	-Run the Python interpreter and type the commands:
	>>> import nltk
	>>> nltk.download()
	-The download program takes you through the rest
-Run pre_ceremony

To run:

All methods are in gg_api. To run the autograder, use
'python autograder.py gg_api.py year'. You can also
run 'gg_api.py' and it will return a dictionary of output
for the year 2013. For other years you can call individual
methods from the python interpreter.
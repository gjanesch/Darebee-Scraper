import pandas as pd
import sys
import darebee_scraper_constants as dsc
import subprocess
import re


# Opens a PDF file with the default viewing application.  Code will not work on
# Windows.
def open_workout_pdf(pdf_name, difficulty):
    path_to_pdf = "Workout PDFs/Difficulty " + str(difficulty) + "/" + pdf_name
    if sys.platform == 'darwin':
        subprocess.call(('open', path_to_pdf))
    else:
        subprocess.call(('xdg-open', path_to_pdf))


darebee = pd.read_csv(dsc.DAREBEE_FILE_NAME, sep = dsc.DAREBEE_FILE_SEP)

# Ask for difficulty level
difficulty_level = input("Specify difficulty level: ")
if difficulty_level.isdigit():
    if 1 <= int(difficulty_level) <= 5:
        difficulty_level = int(difficulty_level)
    else:
        sys.exit("Invalid difficulty (must be between 1 and 5).")
else:
    sys.exit("Non-numeric difficulty level given.  Exiting.")


# return three random workouts with that difficulty level
possible_workouts = darebee.loc[darebee["Difficulty"] == difficulty_level,]
possible_workouts = possible_workouts.sample(n=3)

print("The three selected workouts are:\n")
for _, row in possible_workouts.iterrows():
    pdf_file_name = re.search("workouts/(.*?)$", row["PDF_URL"]).group(1)
    print(pdf_file_name)
    open_workout_pdf(pdf_file_name, difficulty_level)

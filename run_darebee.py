#!/usr/bin/env python3

import darebee_scraper_constants as dsc
import darebee_scraping_functions as dsf
import argparse
import pandas as pd
import re
import sys
import subprocess

# Present options:
#  * Generate new files
#  * Select workouts
#  * Update workout list
#  * flag to skip file updates

def open_workout_pdf(pdf_name, difficulty):
    path_to_pdf = "Workout PDFs/Difficulty " + str(difficulty) + "/" + pdf_name
    if sys.platform == 'darwin':
        subprocess.call(('open', path_to_pdf))
    else:
        subprocess.call(('xdg-open', path_to_pdf))

parser = argparse.ArgumentParser()
parser.add_argument("operation", help = "Can be either 'update' to update workout listings" +
                    "or 'present' to show possible workouts.", type = str)
args = parser.parse_args()

if args.operation == "update":
    print("Updating pdfs and csv")
    dsf.create_update_workout_list()
elif args.operation == "present":
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

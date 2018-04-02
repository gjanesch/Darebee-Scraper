#!/usr/bin/env python3.6

import pandas as pd
import sys
import darebee_scraper_constants as dsc

darebee = pd.read_csv(dsc.DAREBEE_FILE_NAME, sep = dsc.DAREBEE_FILE_SEP)

# Ask for difficulty level
user_input = input("Specify difficulty level: ")
if user_input.isdigit():
    user_input = int(user_input)
else:
    sys.exit("Non-numeric difficulty level given.  Exiting.")

# return three random workouts with that difficulty level
possible_workouts = darebee.loc[darebee["Difficulty"] == user_input,]
# let user pick or just open the PDFs?

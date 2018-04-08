# Description

This is a small project designed to collect and maintain information on the exercise routines posted on the website [Darebee](http://darebee.com/).  Specifically, it is intended to:

1. Create and update a CSV file containing information on each workout.
2. Download the PDF files for each workout.
3. Upon running a specified script (currently <TT>command_line_top.py</TT>), the user will be prompted for a difficulty level, and the program will return three randomly selected workouts' PDFs.

This code is currently intended to be Mac/Linux only due how the of file paths are formed and shell commands for opening files.
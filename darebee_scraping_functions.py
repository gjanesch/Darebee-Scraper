import re
import os

from bs4 import BeautifulSoup
import pandas as pd
import requests
import darebee_scraper_constants as consts


# Shorthand for grabbing a web page
def get_page_html(url):
    return BeautifulSoup(requests.get(url).text, "lxml")


# Checks the main page and grabs all of the workout URLs
def get_darebee_links(darebee_url):
    darebee_html = get_page_html(darebee_url)
    javatext = darebee_html.findAll("script", attrs={'type':'text/javascript'})
    workout_links_text = str(javatext[-1])
    workout_links_text = re.findall("\{.*?\}", workout_links_text)
    workout_links_text = re.sub("\\\/", "/",workout_links_text[0])
    return [r for r in re.findall("\/workouts/.*?\.html",workout_links_text)]


# Acquires the infobox element from the workout page and extracts a specific
# part
def get_infobox(infobox, element):
    try:
        infobox = infobox.find('div', attrs={'class':element}).find('img')['src']
    except AttributeError:
        return "N/A"
    return re.search("/images/infobox/.*?-(.*)\.jpg", infobox).group(1).title()


# Gets the information for a single workout from a Darebee workout page
def get_workout_info(workout_link):
    print(workout_link)
    workout_name = re.search("/workouts/(.*)\.html", workout_link).group(1)
    workout_name = re.sub("-", " ", workout_name).title()

    workout_page = consts.DAREBEE_BASE_URL + workout_link

    workout_raw = requests.get(workout_page)
    workout_html = BeautifulSoup(workout_raw.text, "lxml")

    infobox_more = workout_html.find('div', attrs={'class':'infobox'})
    focus = get_infobox(infobox_more, 'infobox-focus')
    difficulty = get_infobox(infobox_more, 'infobox-difficulty')
    works = get_infobox(infobox_more, 'infobox-works')

    pdf_url = consts.DAREBEE_BASE_URL + "/pdf" + re.sub("\.html", ".pdf", workout_link)

    # Pages have (somewhat dramatic) descriptions of the workouts.  Could be
    # useful, though
    description = workout_html.find("div", attrs = {"class":"infomore"})
    if description.find("div", attrs = {"class":"infotext"}) is not None:
        description = description.find("div", attrs = {"class":"infotext"}).text
    else:
        description= workout_html.find("p").text
    description = re.sub("( )?\\xa0", "", description)

    # Most (but not all) workouts have extra credit, for doing exercises more
    # intensely; grab those.
    extra_credit = workout_html.find("div", attrs = {"class":"infoec"})
    extra_credit = extra_credit.text if extra_credit is not None else ""
    extra_credit = re.sub("Extra [Cc]redit:( )?|\\xa0", "", extra_credit)

    return (workout_name, workout_page, focus, difficulty, works, pdf_url,
            description, extra_credit)

# Either updates the workout list (if the darebee file exists) or downloads all
# of the existing workouts into a dataframe (if the file's not present).
def create_update_workout_list():
    workout_links = get_darebee_links(consts.DAREBEE_BASE_URL + "/wods.html")
    darebee_file_exists = os.path.isfile(consts.DAREBEE_FILE_NAME)
    headers = ["Workout_Name","Workout_Page_URL","Focus","Difficulty",
           "Works","PDF_URL","Description","Extra_Credit"]

    if darebee_file_exists:
        print("Darebee file found - checking for new workouts...")
        darebee = pd.read_csv(consts.DAREBEE_FILE_NAME, sep = consts.DAREBEE_FILE_SEP)
        workout_links_full = [consts.DAREBEE_BASE_URL + wl for wl in workout_links]
        not_in_df = pd.Series(workout_links_full).isin(darebee["Workout_Page_URL"])
        new_workouts = [wl for wl,nid in zip(workout_links, list(~not_in_df)) if nid]
        print(str(len(new_workouts)) + " new workouts found.")
        # If new workouts were found, download them and append them to the df
        if len(new_workouts) != 0:
            print("Gathering info...")
            new_workout_tuples = [get_workout_info(nw) for nw in new_workouts]
            new_workout_df = pd.DataFrame(new_workout_tuples, columns = headers)
            darebee = new_workout_df.append(darebee)
            update_pdf_collection(new_workout_df)

    else:
        print("No Darebee file found - creating new file...")
        workout_tuples = [get_workout_info(wl) for wl in workout_links]
        darebee = pd.DataFrame(workout_tuples, columns = headers)
        set_up_workout_folders()
        update_pdf_collection(darebee)

    darebee.to_csv(consts.DAREBEE_FILE_NAME, sep = consts.DAREBEE_FILE_SEP,
                   index = False)
    print("Done.")


# Downloads a workout PDF to the specified directory.
def download_workout_pdf(pdf_url, file_destination):
    response = requests.get(pdf_url)
    with open(file_destination,'wb') as f:
        f.write(response.content)

# Sets up the workout folders; they're only divided by difficulty.
def set_up_workout_folders():
    if not os.path.exists("./Workout PDFs"):
        os.mkdir("./Workout PDFs")

    for x in range(5):
        dir_name = "Difficulty " + str(x+1)
        if not os.path.exists("./Workout PDFs/" + dir_name):
            os.mkdir("./Workout PDFs/" + dir_name)


def update_pdf_collection(df):
    for _, row in df.iterrows():
        pdf_name = re.search("workouts/(.*?)$", row["PDF_URL"]).group(1)
        workout_file_path = "Workout PDFs/Difficulty " + str(row["Difficulty"]) + "/" + pdf_name
        if not os.path.isfile(workout_file_path):
            download_workout_pdf(row["PDF_URL"], workout_file_path)

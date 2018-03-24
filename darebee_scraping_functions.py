import re
import os

from bs4 import BeautifulSoup
import pandas as pd
import requests

DAREBEE_BASE_URL = "https://darebee.com"
DAREBEE_FILE_NAME = "darebee.csv"
SEP = "\t"

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
    
    workout_page = DAREBEE_BASE_URL + workout_link
    
    workout_raw = requests.get(workout_page)
    workout_html = BeautifulSoup(workout_raw.text, "lxml")
    
    infobox_more = workout_html.find('div', attrs={'class':'infobox'})
    focus = get_infobox(infobox_more, 'infobox-focus')
    difficulty = get_infobox(infobox_more, 'infobox-difficulty')
    works = get_infobox(infobox_more, 'infobox-works')
    
    pdf_url = DAREBEE_BASE_URL + "/pdf" + re.sub("\.html", ".pdf", workout_link)
    
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

def create_update_workout_list():
    workout_links = get_darebee_links(DAREBEE_BASE_URL + "/wods.html")
    darebee_file_exists = os.path.isfile(DAREBEE_FILE_NAME)
    headers = ["Workout Name","Workout Page URL","Focus","Difficulty",
           "Works","PDF URL","Description","Extra Credit"]
    
    if darebee_file_exists:
        print("Darebee file found - checking for new workouts...")
        darebee = pd.read_csv(DAREBEE_FILE_NAME, sep = "\t")
        print(darebee.head())
        workout_links_full = [DAREBEE_BASE_URL + wl for wl in workout_links]
        not_in_df = pd.Series(workout_links_full).isin(darebee["Workout Page URL"])
        new_workouts = [wl for wl,nid in zip(workout_links, list(~not_in_df)) if nid]
        print(len(new_workouts))
        if len(new_workouts) != 0:
            print(str(len(new_workouts)) + " new workouts found; gathering info...")
            new_workout_tuples = [get_workout_info(nw) for nw in new_workouts]
            new_workout_df = pd.DataFrame(new_workout_tuples, columns = headers)
            print(new_workout_df)
            darebee = new_workout_df.append(darebee)
        else:
            print("No new workouts found.")
    else:
        print("No Darebee file found - creating new file...")
        workout_tuples = [get_workout_info(wl) for wl in workout_links]
        darebee = pd.DataFrame(workout_tuples, columns = headers)
    
    darebee.to_csv(DAREBEE_FILE_NAME, sep = "\t", index = False)
    print("Done.")

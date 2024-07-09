from bs4 import BeautifulSoup
import urllib3
import json
from os import path
from time import sleep
import sys

http = urllib3.PoolManager()

URL = "http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx"
DROPDOWN_KEY = "ctl00$ContentPlaceHolderBody$DropDownList2"

request_headers = urllib3.HTTPHeaderDict()
request_headers.add("Accept", "text/html")

metadata_neeeded_for_page = {}
page_metadata = {}
students_by_page = {}


def parse_page_metadata(idx, soup):
    global page_metadata
    global metadata_neeeded_for_page

    viewstate = soup.find(id="__VIEWSTATE").attrs.get("value")
    viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR").attrs.get("value")
    eventvalidation = soup.find(id="__EVENTVALIDATION").attrs.get("value")
    selection = [
        *map(
            lambda o: o.attrs.get("value"),
            soup.find("select", {"name": DROPDOWN_KEY}).find_all("option"),
        )
    ]

    assert (
        viewstate and viewstategenerator and eventvalidation and selection
    ), "Invalid page metadata"

    data = {
        "viewstate": viewstate,
        "viewstategenerator": viewstategenerator,
        "eventvalidation": eventvalidation,
        "selection": selection,
    }

    for option in selection:
        if not option in metadata_neeeded_for_page:
            metadata_neeeded_for_page[option] = data

    page_metadata[idx] = data


def get_page_by_number(idx, context):
    # print(f"Getting page {idx}")

    if idx == "1":
        resp = http.request("GET", URL, headers=request_headers)
    else:
        resp = http.request(
            "POST",
            URL,
            headers=request_headers,
            fields={
                "__VIEWSTATE": context["viewstate"],
                "__VIEWSTATEGENERATOR": context["viewstategenerator"],
                "__EVENTVALIDATION": context["eventvalidation"],
                DROPDOWN_KEY: idx,
                "__EVENTTARGET": DROPDOWN_KEY,
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
            },
        )
    assert resp.status == 200, f"Couldn't get page {idx}"
    return resp.data


def maybe_float(x):
    if x.strip() == "":
        return None
    try:
        return float(x)
    except ValueError:
        return x


def parse_page(idx, html):
    soup = BeautifulSoup(html, features="html.parser")
    try:
        table = (
            soup.find(id="ContentPlaceHolderBody_FinalDiv").find("table").find_all("tr")
        )
    except AttributeError:
        print(f"Couldn't get the table for {idx}")
        return None
    parse_page_metadata(idx, soup)

    page_students = []
    for i in range(2, len(table) - 1, 2):
        td_top = list(table[i].find_all("td"))
        td_bottom = list(table[i + 1].find_all("td"))

        judet_anchor = td_top[3].find("a")
        judet_href = judet_anchor.attrs.get("href")
        judet_cod = int("".join(char for char in judet_href if char.isdigit()))

        student_data = {
            "nr": int(td_top[0].text),
            "cod_candidat": td_top[1].text,
            "unitate_invatamant": td_top[2].text.strip(),
            "judet_cod": judet_cod,
            "judet_nume": judet_anchor.text.strip(),
            "promotie_anterioara": True if td_top[4].text == "DA" else False,
            "forma_invatamant": td_top[5].text,
            "specializare": td_top[6].text,
            "limba_romana_competente": td_top[7].text.strip() or None,
            "limba_romana_scris": maybe_float(td_top[8].text),
            "limba_romana_contestatie": maybe_float(td_top[9].text),
            "limba_romana_nota_finala": maybe_float(td_top[10].text),
            "limba_materna": td_top[11].text.strip() or None,
            "limba_materna_competente": td_bottom[0].text.strip() or None,
            "limba_materna_scris": maybe_float(td_bottom[1].text),
            "limba_materna_contestatie": maybe_float(td_bottom[2].text),
            "limba_materna_nota_finala": maybe_float(td_bottom[3].text),
            "limba_moderna": td_top[12].text,
            "limba_moderna_nota": td_top[13].text.strip() or None,
            "disciplina_obligatorie": td_top[14].text,
            "disciplina_obligatorie_scris": maybe_float(td_bottom[4].text),
            "disciplina_obligatorie_contestatie": maybe_float(td_bottom[5].text),
            "disciplina_obligatorie_nota_finala": maybe_float(td_bottom[6].text),
            "disciplina_aleasa": td_top[15].text,
            "disciplina_aleasa_scris": maybe_float(td_bottom[7].text),
            "disciplina_aleasa_contestatie": maybe_float(td_bottom[8].text),
            "disciplina_aleasa_nota_finala": maybe_float(td_bottom[9].text),
            "competente_digitale": td_top[16].text.strip() or None,
            "media": maybe_float(td_top[17].text),
            "rezultat_final": maybe_float(td_top[18].text),
        }
        page_students.append(student_data)
    return page_students


first_page_metadata_path = path.join("data", "bac_2024_page_metadata.json")


def load_cache():
    global page_metadata

    if path.isfile(first_page_metadata_path):
        with open(first_page_metadata_path, "r") as f:
            page_metadata["1"] = json.load(f)
    else:
        print("Not loading files")


def try_save_page(i, retries=0):
    global students_by_page
    idx = f"{i}"

    if idx in students_by_page:
        print(f"Skipping {idx}")
        return

    metadata = {}
    if i == 1:
        metadata = {}
    elif i % 10 == 0:
        metadata = page_metadata["1"]
    else:
        metadata = metadata_neeeded_for_page[idx]

    html = get_page_by_number(idx, metadata)
    students = parse_page(idx, html)

    if not students:
        retries += 1

        if retries < 3:
            sleep(0.5)
            print(f"Retrying {i}")
            return try_save_page(i, retries)
        else:
            print(f"Got stuck at {i} after {retries} retries. Cancelling!")
            with open(
                path.join("data", "batch", f"bac_2024_batch_{start_idx}.failed"), "w"
            ) as f:
                f.write(f"Got stuck at {i} after {retries} retries. Cancelling!")
            exit(-1)

    students_by_page[idx] = students
    print(f"New students for {idx}")


print("Loading data")
load_cache()


if len(sys.argv) != 4:
    print("Need an argument for batch size and another argument for page number")

print(sys.argv)

batch_size = int(sys.argv[1])
start_idx = int(sys.argv[2])
last_page = int(sys.argv[3])
if start_idx == 1:
    try_save_page(1)
    pages_count = int(page_metadata["1"]["selection"][-1])
    print(f"There are {pages_count} pages")

for i in range(start_idx, start_idx + batch_size):
    if last_page > 0 and i > last_page:
        break
    try_save_page(i)
    sleep(0.3)


print("Saving...")
if start_idx == 1:
    with open(first_page_metadata_path, "w") as f:
        json.dump(page_metadata["1"], f)
batch_data = {}
for i in range(start_idx, start_idx + batch_size):
    idx = f"{i}"
    batch_data[idx] = students_by_page[idx]
    with open(path.join("data", "batch", f"bac_2024_batch_{start_idx}.json"), "w") as f:
        json.dump(batch_data, f)

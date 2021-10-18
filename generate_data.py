import re
import requests
from bs4 import BeautifulSoup

# All of the Byzantine Emperor names live here
url = 'https://en.wikipedia.org/w/index.php?title=List_of_Byzantine_emperors&oldid=1007718930'

# Pull the raw html from this page
with requests.Session() as s:
    response = s.get(url, timeout=5).text

# Use BeautifulSoup to interpret it
soup = BeautifulSoup(response, 'html.parser')
table = soup.find_all('table')[1]

# Let's pull all the names into a dictionary of lists
names = []
greek = []
latin = []


def name_parser(wiki_text: str) -> dict:
    """
    This function will try to be a catch all for the text we expect in a name cell.

    Hopefully it doesn't change any time soon...
    :param wiki_text: str, the text in the name cell
    :return: dict, with key names, greek, latin, alt, alt_greek, alt_latin
    """
    # init
    text, _, alt = wiki_text.lower().rstrip().partition('formally')
    pattern = r'([^\(\)\,]+)\(?([^\(\)\,]+)?,?([^\(\)\,]+)?\)?'
    fields = ['name', 'greek', 'latin']
    alt_fields = ['alt_name', 'alt_greek', 'alt_latin']

    # parse cell structure
    matches = [item.strip()+"." for item in re.findall(pattern, text)[0] if item != '']
    alt_matches = [item.strip()+"." for item in re.findall(pattern, alt)[0] if item != ''] if alt else []

    # add to dictionary
    d1, d2 = dict(zip(fields, matches)), dict(zip(alt_fields, alt_matches))

    return {**d1, **d2}


greek_char_map = {
    'ὴ': 'η',
    'ή': 'η',
    'ἡ': 'η',
    'ὸ': 'ο',
    'ό': 'ο',
    'ὁ': 'ο',
    'ἴ': 'ι',
    'ἰ': 'ι',
    'ί': 'ι',
    'ῖ': 'ι',
    'ῶ': 'ω',
    'ώ': 'ω',
    'ὐ': 'υ',
    'ύ': 'υ',
    'a': 'α',
    'ἄ': 'α',
    'ᾷ': 'α',
    'ἀ': 'α',
    'ά': 'α',
    'ᾶ': 'α',
    'έ': 'ε',
    'ἐ': 'ε',
    'b': 'β',
    'ῥ': 'ρ',
    'ʹ': '',
    '/': '',
}

for row in table.find_all('tr'):
    cells = row.find_all('td')
    if len(cells) == 4:
        d = name_parser(cells[1].text)
        # Of course there is one exception that breaks everything
        names.append(d['name'].replace('-', ' '))
        temp_s = d['greek'].replace('greek: ', '').replace('[', '').replace(']', '')
        for key in greek_char_map:
            temp_s = temp_s.replace(key, greek_char_map[key])
        greek.append(d['name'].replace('-', ' ') + temp_s)

        # These may not appear in the cell
        try:
            latin.append(d['latin'].replace('latin: ', ''))
        except KeyError:
            pass
        try:
            names.append(d['alt_name'])
        except KeyError:
            pass
        try:
            temp_s = d['alt_greek'].replace('greek: ', '').replace('[', '').replace(']', '')
            for key in greek_char_map:
                temp_s = temp_s.replace(key, greek_char_map[key])
            greek.append(d['name'].replace('-', ' ') + temp_s)
        except KeyError:
            pass
        try:
            latin.append(d['alt_latin'])
        except KeyError:
            pass

if __name__ == "__main__":

    print(names)
    print("*"*10)
    print(greek)
    print("*" * 10)
    print(latin)
    print("*" * 10)

    s = set()
    for t in greek:
        s |= set(t)

    print(s)

    print(len(max(greek, key=len)))

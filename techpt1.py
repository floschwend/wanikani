import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class CharInfo:
    x: int
    y: int
    char: str

def get_td(tr, index: int) -> str:
    return tr.findChildren("td")[index].getText()

def fetch_and_parse_url(url: str):

    try:
        resp = requests.get(url=url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        chars = []
        for tr in soup.table.findChildren("tr")[1:]:
            x, char, y = int(get_td(tr, 0)), get_td(tr, 1), int(get_td(tr, 2))
            chars.append(CharInfo(x, y, char))

        max_x = max(c.x for c in chars)
        max_y = max(c.y for c in chars)

        matrix = [[" "] * (max_x + 1) for _ in range(max_y + 1)]
        for c in chars:
            matrix[max_y - c.y][c.x] = c.char

        print("\n".join("".join(row) for row in matrix))
        return

    except Exception as inst:
        print("Exception in fetch_and_parse_url: {msg}".format(msg = inst))

    return

test_url = "https://docs.google.com/document/d/e/2PACX-1vSZ1vDD85PCR1d5QC2XwbXClC1Kuh3a4u0y3VbTvTFQI53erafhUkGot24ulET8ZRqFSzYoi3pLTGwM/pub"
fetch_and_parse_url(test_url)
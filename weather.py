import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Literal

days = {
    "today": 3,
    "tomorrow": 4,
    "after_tomorrow": 5}

URL = "https://www.meteo22.ru/"


def get_weather(day: Literal["today", "tomorrow", "after_tomorrow"]):
    current_day = days[day]

    agent = UserAgent().random

    headers = {
        "User-Agent": agent
    }

    response = requests.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    if response.status_code == 200:
        try:
            data = []
            for row in soup.find("div", {"class": "table table6"}).children:
                try:
                    data.append(list(row.find_all("div", {"class": "td1"}))[current_day].text)
                except AttributeError:
                    pass
                except IndexError:
                    pass

            wthr = {
                "date": data[0],
                "night": {
                    "temp": data[1].replace("Температура", "").strip(),
                    "weather": data[2],
                    "wind": data[3].replace("Ветер", "").strip()
                },
                "day": {
                    "temp": data[4].replace("Температура", "").strip(),
                    "weather": data[5],
                    "wind": data[6].replace("Ветер", "").strip()
                }
            }

            return ["Success", wthr]
        except AttributeError as e:
            return ["Err", "BeautifulSoup Error"]

    else:
        return ["Err", f"Responce Error: {response.status_code}"]


if __name__ == "__main__":
    print(get_weather("today")[1])

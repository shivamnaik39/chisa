import httpx
from selectolax.parser import HTMLParser
import urllib.parse
from dataclasses import dataclass, asdict
from typing import List
import json


@dataclass
class Anime():
    title: str
    info_link: str
    no_of_comments: int
    comments_link: str
    torrent_link: str
    magnet_link: str
    size: str
    upload_timestamp: str
    seeders: int
    leechers: int
    total_downloads: int


BASE_URL = "https://nyaa.si"


def get_html(name):
    URL = f"{BASE_URL}/?f=0&c=0_0&q={urllib.parse.quote(name)}&s=seeders&o=desc"
    res = httpx.get(URL)
    # Test parsing the data with local html data
    # with open("test.html", "w") as file:
    #     file.write(res.text)
    print(f"Fetched data for {name} ")
    return HTMLParser(res.text)


def parse_anime_data(html, limit: int = 10) -> List[Anime]:
    # HTML for all anime torrent downlaod data (raw format)
    # limit is to get only limited number of anime torrents (default = 10)
    raw_anime_list = html.css("tbody > tr")
    # if items are less than limit then consider whole list
    raw_anime_list = raw_anime_list[: min(limit, len(raw_anime_list))]
    anime_list: List[Anime] = []
    for anime in raw_anime_list:
        anime_data = get_anime_torrent_data(anime)
        anime_list.append(anime_data)

    print("Parsing Done..")
    return anime_list


def get_anime_torrent_data(anime) -> Anime:
    # ignore first td as it is not relevant
    # get data fro tds
    fields = anime.css("td")

    # size of the anime torrent download
    size = fields[3].text(strip=True)

    # upload date of anime torrent
    upload_timestamp = fields[4].attrs.get("data-timestamp")

    # number of seeders
    seeders = fields[5].text(strip=True)

    # number of leechers
    leechers = fields[6].text(strip=True)

    # total number of downloads
    total_downloads = fields[7].text(strip=True)

    #  Check if comments exists on torrent
    is_comment_exists = len(fields[1].css("a")) == 2

    # If comment exists then extract the comment data
    if is_comment_exists:
        # Extracting the nested comments and title data from anchor tags
        comments_fields, title_fields = fields[1].css(
            "a")[0], fields[1].css("a")[1]

        # Numbre of comments on torrent
        no_of_comments = comments_fields.attrs.get("title")

        # Link to the comment section of anime torrent
        comments_link = BASE_URL + comments_fields.attrs.get("href")
    else:
        title_fields = fields[1].css_first("a")
        no_of_comments = "0 comments"
        comments_link = None

     # Title of anime torrent
    title = title_fields.attrs.get("title")

    # Link to the Anime torrent page to get basic info about torrent
    info_link = BASE_URL + title_fields.attrs.get("href")

    # Extracting the nested magent link and torrent file download from anchor tags
    torrent_link, magent_fields = fields[2].css("a")[0], fields[2].css("a")[1]

    # torrent file download link
    torrent_link = BASE_URL + torrent_link.attrs.get("href")

    # Magnet link
    magnet_link = magent_fields.attrs.get("href")

    d = {
        "title": title,
        "info_link": info_link,
        "no_of_comments": int(no_of_comments.split(" ")[0]),
        "comments_link": comments_link,
        "torrent_link": torrent_link,
        "magnet_link": magnet_link,
        "size": size,
        "upload_timestamp": upload_timestamp,
        "seeders": int(seeders),
        "leechers": int(leechers),
        "total_downloads": int(total_downloads)
    }

    return Anime(**d)


def save_data(data, filename="anime_data.json"):
    if filename.split(".")[1] == "json":
        with open(filename, "w")as file:
            data_json = json.dumps([val.__dict__ for val in data], indent=4)
            file.write(data_json)

        print(f"Data saved successfully in file {filename} !")

    else:
        return print("Invalid file type! Expected json")


def main():
    try:
        # Name of the anime to search
        anime_name = input("Enter the anime name: ")

        # Fetch the result page for that anime
        html = get_html(anime_name)

        # Parse the fetched data and only get top 10 torrents (can be changed via parmeter)
        data = parse_anime_data(html, 10)

        # Save the result in json format default filname: anime_data.json (can be changed)
        save_data(data)

    except Exception as e:
        print("Caught exception:", e)


if __name__ == '__main__':
    main()

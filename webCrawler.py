#!/usr/bin/env python3

import requests
from resources import colors
from bs4 import BeautifulSoup as BS
import pprint
import traceback

# get user requested url
def curlURL(url):
    # beautify with BS
    soup = BS(requests.get(url).text, "html.parser")
    return soup

# get user requested tags
def requestSearchTags(soup):
    end = ""
    tags = []
    while end != "END":
        # ask user for classname
        userTag = input("Enter a class tag (type END when complete): ")

        #verify classname exists
        if userTag.upper() == "END":
            # user 'END' case sensitive
            end = "END"
        elif userTag == "":
            print(f"{colors.red}{colors.bad}Invalid tag.{colors.end}")
        elif not soup.select("." + userTag):
            print(f"{colors.red}{colors.bad}Invalid tag.{colors.end}")
        else:
                tags.append(userTag)

    return tags

# pull data
def retrieveTags(searchTags, soup):
    tags = {}
    for idx, tag in enumerate(searchTags):
        tags[tag] = soup.select("." + tag)

    return tags

# save
def saveFile(file, filteredHTML, style):
    file = open(file, style)
    for key, value in filteredHTML.items():
        file.write(f"{key}: {value}")
        file.write("\n")
    file.close()
    # CSV or JSON

# MAIN
def main():
    url = ""
    while True:
        while True:
            try:
                if not url:
                    url = input("Enter URL: ")
                else:
                    newURL = input("Use same URL (y/n): ")
                    if newURL in "nN":
                        url = input("Enter URL: ")
                soup = curlURL(url)
                break
            except:
                print(f"{colors.red}{colors.bad}Error in URL{colors.end}")
                url = ""

        searchTags = requestSearchTags(soup)
        filteredHTML = retrieveTags(searchTags, soup)
        # filteredHTML = searchTags

        # print to console
        preview = input("Preview data (y/n): ")
        if preview in "yY":
            pprint.pprint(filteredHTML)

        while True:
            save = input("Save to file ([W]rite/[A]ppend): ")[0]
            if save in "aAwW":
                saveasfilename = input('Enter filename (directory listing is valid): ')
                # fileType = input("Filetype (csv or JSON): ")
                saveFile(saveasfilename, filteredHTML, save)
                print(f"{colors.green}{colors.good}Save complete.{colors.end}")
                break
            else:
                print(f"{colors.red}{colors.bad}Invalid Choice{colors.end}")


if __name__ == "__main__":
    main()

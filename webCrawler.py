#!/usr/bin/env python3

import requests
from resources import colors
from bs4 import BeautifulSoup
import pprint


# get user requested url
def curlURL(url):
    # beautify with BS
    soup = BeautifulSoup(requests.get(url, timeout=3).text, "html.parser")
    return soup


def recursiveLinkSearch(soup, url, layer, depth):
    results = []
    # for each 'href' found on the page, check if it is a URL
    for a in soup.find_all(href=True):
        try:
            # for every href found, check if contains http or https
            if any(stringStartsWith in a.get('href')[0:4] for stringStartsWith in ["http", "https", "HTTP", "HTTPS"]) \
                    and a.get('href') != url and layer < depth:

                print(f"Found URL: {a.get('href')}")
                print(f"LOG: {colors.yellow}Current Layer: {layer}{colors.end}")
                # print(f"{colors.green}Finding all anchor HTML links.{colors.end}")
                results.append(a.get('href'))
                results.append(recursiveLinkSearch(curlURL(a.get('href')), a.get('href'), layer+1, depth))
        # Exceptions Stack
        except requests.exceptions.InvalidSchema:
            print(f"{a.get('href')}")
            print(f"{colors.bad}Invalid Url Detected{colors.end}")
        except requests.exceptions.ConnectTimeout:
            print(f"{a.get('href')}")
            print(f"{colors.bad}Connection Timeout. Passing...")
        except requests.exceptions.SSLError:
            print(f"{a.get('href')}")
            print(f"{colors.bad}SSL Certificate Error.  Passing...")
        except requests.exceptions.ReadTimeout:
            print(f"{a.get('href')}")
            print(f"{colors.bad}Read Timeout.  Passing...")
    # exit recursion
    # if results != []:
    # print(f"LOG: {results[-1]}")
    return results

def deleteNestedEmptyLists(nestedList):
    for idx, item in enumerate(nestedList):
        if item == []:
            nestedList.pop(idx)
        elif type(item) == list:
            deleteNestedEmptyLists(item)
    return nestedList

# get user requested tags
def requestSearchTags(soup, url, layer):
    end = ""
    tags = {}
    while end != "END":
        # ask user for classname
        userTag = input("Enter a class name, i.e. class='<name>' (type END when complete): ")

        if userTag.upper() == "END":
            # user 'END' case sensitive
            end = "END"
        # not blank, and user did not enter css style classname
        elif userTag == "" or userTag[0] == ".":
            print(f"{colors.red}{colors.bad}Invalid tag.{colors.end}")
        # check for href, begin recursive link search
        elif userTag == "href":
            depth = int(input("Layers before abort (0 indexed, anything over 2 will likely take 10+ minutes): "))
            print(f"{colors.green}Finding all anchor HTML links...{colors.end}")
            tags[userTag] = recursiveLinkSearch(soup, url, layer, depth)
            # check for "None"s and delete
            tags[userTag] = deleteNestedEmptyLists(tags[userTag])
            # for idx, item in enumerate(tags[userTag]):
            #     if type(item) == list:
            #         for idx2, i in enumerate(item):
            #             if i == []:
            #                 item.pop(idx2)
        # verify classname exists on URL
        elif not soup.select("." + userTag):
            print(f"{colors.red}{colors.bad}Invalid tag.{colors.end}")
        else:
            # user entered valid tag which is not href
            tags[userTag] = retrieveTags(userTag, soup)

    return tags


# pull data
def retrieveTags(searchTags, soup):
    # tags = {}
    # for idx, tag in enumerate(searchTags):
        #tags[tag] = soup.select("." + tag)

    return soup.select("." + searchTags)


# save
def saveFile(file, filteredHTML, style):
    file = open(file, style)
    for key, value in filteredHTML.items():
        file.write(f"{key}: {value}")
        file.write("\n")
    file.close()
    # CSV or JSON


# TODO: get scrape statistics
'''
def getStats():
    itemsDiscovered = 0
    for i in searchTags:
        if isinstance(searchTags[i], list):
            itemsDiscovered += len(i)

    # print to console
    print(f"""Stats:
    {colors.info} Keys searched: {len(searchTags)}
    {colors.info} Items found: {itemsDiscovered}
    """)
'''


# MAIN
def main():
    url = ""
    layer = 0
    run = True
    while run:
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

        searchTags = requestSearchTags(soup, url, layer)

        preview = input("Preview data (y/n): ")
        if preview in "yY":
            pprint.pprint(searchTags)

        while True:
            save = input("Save to file ([W]rite/[A]ppend/No): ")[0]
            if save in "aAwW":
                saveasfilename = input('Enter filename (directory listing is valid): ')
                # fileType = input("Filetype (csv or JSON): ")
                saveFile(saveasfilename, searchTags, save)
                print(f"{colors.green}{colors.good}Save complete.{colors.end}")
                break
            elif save in "noNONo":
                break
            else:
                print(f"{colors.red}{colors.bad}Invalid Choice{colors.end}")


if __name__ == "__main__":
    main()

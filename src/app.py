import os
import time
import re
import requests
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

from bs4 import BeautifulSoup

def get_data_from_url(resource_url: str) -> str:
    """
    Get the data (HTML) from an URL using the requests package.

    Ags:
        resource_url (str): url to find the data

    Returns:
        The HTML as a string.

    Raises:
        RuntimeError: If request finish with status code diferent than 200.
    """

    # get the data from the URL
    response = requests.get(resource_url, timeout=time.sleep(10))

    # ff the request was executed correctly (code 200), then the file could be downloaded
    if response:
        # return the data
        return response.content
    else:
        raise RuntimeError("Response did not finish with status 200.")


def get_soup_from_html(html_data: str):
    """
    Get a BeautifulSoup object from the data.

    Ags:
        html_data (str): data as text of HTML

    Returns:
        The BeautifulSoup object
    """

    # get the data as a soup
    soup = BeautifulSoup(html_data, features="html.parser")

    return soup


def get_n_table_from_soup(soup, n: int):
    """
    Get the n table from the soup.

    Ags:
        soup (str): a BeautifulSoup object
        n (int): index of the table to get

    Returns:
        The n table in the soup

    Raises:
        IndexError: If the idnex does not exist
    """

    # get the tables
    tables = soup.find_all("table")

    # return the n table
    return tables[n]
    

def get_html_as_list(table_0):
    """
    Get the n table from the soup.

    Ags:
        table_0 (_OneElement): a BeautifulSoup OneElement object

    Returns:
        The dict with the values
    """

    data_as_list = []

    for row in table_0.find_all("tr")[1:]:
        # get all the tds
        tds = row.find_all("td")
        #print(tds)
        value_to_save = {}

        # get the year
        year = tds[0].span.text
        value_to_save['year'] = int(year if year else 0)

        # get the value in dollars
        cost = re.sub(" |B|\$", "", str(tds[1].text))
        value_to_save['value'] = float(cost if cost else 0)

        # get the percent
        percentage = re.sub("%", "", str(tds[2].text))
        value_to_save['percentage'] = float(percentage if percentage else 0)

        data_as_list.append(value_to_save)

    return data_as_list

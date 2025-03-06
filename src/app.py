import re
import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup


def parse_revenue(revenue_str: str):
    """
    Parses a revenue string like "$8.73 B" and returns the numerical value as a float.

    Args:
        revenue_str (str): The revenue string to parse.

    Returns:
        The numerical value as a float.
    """

    # verify if the string is empty
    if not revenue_str:
        return 0

    # remove '$' and leading/trailing spaces
    revenue_str = revenue_str.replace('$', '').strip()

    # split into value and unit
    value, unit = revenue_str.split()  

    # verify if empty
    if not value:
        return 0
    
    # convert value to float
    value = float(value)  

    if unit == 'B' or unit == 'Billion':
        return value * 10**9  # Billion
    elif unit == 'M' or unit == 'Million':
        return value * 10**6  # Million
    elif unit == 'K':
        return value * 10**3  # Thousand
    else:
        return value  # if no unit, assume it's already in base units


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
    response = requests.get(resource_url, timeout=5)

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
        IndexError: If the index does not exist
    """

    # get the tables
    tables = soup.find_all("table")

    # return the n table
    return tables[n]
    

def get_html_as_list(table_0, elements_to_sub: 'list[str]'):
    """
    Get the n table from the soup.

    Ags:
        table_0 (_OneElement): a BeautifulSoup OneElement object

    Returns:
        The list with the values
    """

    # data tog et from the html
    data_as_list = []

    # regex to use in the substitute
    regex = '|'.join(elements_to_sub)

    for row in table_0.find_all("tr")[1:]:
        # get all the tds
        tds = row.find_all("td")
        #print(tds)
        value_to_save = {}

        # get the year
        year = tds[0].span.text
        value_to_save['year'] = int(year if year else 0)

        # get the value in dollars
        revenue = parse_revenue(str(tds[1].text))
        value_to_save['revenue'] = revenue

        # get the percent
        change = re.sub("%", "", str(tds[2].text))
        value_to_save['change'] = float(change if change else 0)

        data_as_list.append(value_to_save)

    return data_as_list


def save_df_to_db(df: pd.DataFrame, db_name: str, table_name: str) -> None:
    """
    Save the df to the database

    Ags:
        df (DataFrame): dataframe to save
        db_name (str): name of the db to save
        table_name (str): name of the table to save teh df

    Returns:
        None
    """

    # connect to the data base (create the db) if it does not exist
    conn = sqlite3.connect(f'{db_name}.db')

    # save the df to the data base
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # close the connection
    conn.close()


def get_df_from_db(db_name: str, table_name: str) -> pd.DataFrame:
    """
    Get the value of a table as a df

    Ags:
        db_name (str): database name
        table_name (str): table name to get the data

    Returns:
        Df with the values
    """

    # connect to the data base (create the db) if it does not exist
    conn = sqlite3.connect(f'{db_name}.db')

    # get the data
    df_read = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    # close the connection
    conn.close()

    return df_read

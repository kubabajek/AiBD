import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

from typing import Union, List, Tuple

connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

def film_in_category(category_id:int)->pd.DataFrame: 
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego id kategorii.
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(category_id, int) and category_id>0):
        return None
    df = pd.read_sql('\
    SELECT f.title, l.name "languge", c.name category FROM film f\
    INNER JOIN film_category fc ON f.film_id = fc.film_id\
    INNER JOIN category c ON fc.category_id = c.category_id\
    INNER JOIN language l ON l.language_id = f.language_id\
    WHERE c.category_id = {}\
    ORDER BY f.title,l.name\
    '.format(category_id),con=connection)
    return df
#W POWYŻSZEJ FUNKCJI KOLUMNA Z JĘZYKIEM MA ALIAS "languge" ZAMIAST "language" ZGODNIE Z WYMAGANIAMI!
    
def number_films_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów w zadanej kategori przez id kategorii.
    Przykład wynikowej tabeli:
    |   |category   |count|
    |0	|Action 	|64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(category_id, int) and category_id>0):
        return None
    df = pd.read_sql('\
    SELECT c.name category, COUNT(fc.film_id) count FROM film_category fc\
    INNER JOIN category c ON c.category_id = fc.category_id\
    WHERE c.category_id = {}\
    GROUP BY category\
    '.format(category_id),con=connection)
    return df

def number_film_by_length(min_length: Union[int,float] = 0, max_length: Union[int,float] = 1e6 ) :
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów o dla poszczegulnych długości pomiędzy wartościami min_length a max_length.
    Przykład wynikowej tabeli:
    |   |length     |count|
    |0	|46 	    |64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    min_length (int,float): wartość minimalnej długości filmu
    max_length (int,float): wartość maksymalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not (isinstance(min_length,(int,float)) and isinstance(max_length,(int,float)) and
            min_length >= 0 and max_length >=0 and max_length >= min_length):
        return None
    df = pd.read_sql('\
    SELECT length, COUNT(film_id) FROM film\
    WHERE length BETWEEN {minl} AND {maxl}\
    GROUP BY length\
    ORDER BY length\
    '.format(minl=min_length,maxl=max_length),con=connection)
    return df

def client_from_city(city:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o listę klientów z zadanego miasta przez wartość city.
    Przykład wynikowej tabeli:
    |   |city	    |first_name	|last_name
    |0	|Athenai	|Linda	    |Williams
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    city (str): nazwa miaste dla którego mamy sporządzić listę klientów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(city,str)):
        return None
    df = pd.read_sql("\
    SELECT city.city, c.first_name, c.last_name FROM customer c\
    INNER JOIN address ON address.address_id = c.address_id\
    INNER JOIN city ON city.city_id = address.city_id\
    WHERE city.city = '{}'\
    ORDER BY c.last_name, c.first_name\
    ".format(city),con=connection)
    return df    

def avg_amount_by_length(length:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o średnią wartość wypożyczenia filmów dla zadanej długości length.
    Przykład wynikowej tabeli:
    |   |length |avg
    |0	|48	    |4.295389
    
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    length (int,float): długość filmu dla którego mamy pożyczyć średnią wartość wypożyczonych filmów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(length,(int,float)) and length>=0):
        return None
    df = pd.read_sql("\
    SELECT f.length, AVG(p.amount) FROM rental r\
    INNER JOIN inventory i ON i.inventory_id = r.inventory_id\
    INNER JOIN film f ON f.film_id = i.film_id\
    INNER JOIN payment p ON p.rental_id = r.rental_id\
    WHERE f.length = {}\
    GROUP BY f.length\
    ".format(length),con=connection)
    return df      

def client_by_sum_length(sum_min:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o sumaryczny czas wypożyczonych filmów przez klientów powyżej zadanej wartości .
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |sum
    |0  |Brian	    |Wyman  	|1265
    
    Tabela wynikowa powinna być posortowane według sumy, imienia i nazwiska klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    sum_min (int,float): minimalna wartość sumy długości wypożyczonych filmów którą musi spełniać klient
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(sum_min,(int,float)) and sum_min >= 0):
        return None
    df = pd.read_sql("\
    SELECT c.first_name, c.last_name, SUM(f.length) FROM customer c\
    INNER JOIN rental r ON r.customer_id = c.customer_id\
    INNER JOIN inventory i ON i.inventory_id = r.inventory_id\
    INNER JOIN film f ON f.film_id = i.film_id\
    GROUP BY c.first_name, c.last_name\
    HAVING SUM(f.length) >= {}\
    ORDER BY SUM(f.length),c.last_name, c.first_name\
    ".format(sum_min),con=connection)
    return df   

def category_statistic_length(name:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o statystykę długości filmów w kategorii o zadanej nazwie.
    Przykład wynikowej tabeli:
    |   |category   |avg    |sum    |min    |max
    |0	|Action 	|111.60 |7143   |47 	|185
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    name (str): Nazwa kategorii dla której ma zostać wypisana statystyka
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not(isinstance(name,str)):
        return None
    df = pd.read_sql("\
    SELECT c.name category, AVG(f.length), SUM(f.length), MIN(f.length), MAX(f.length) FROM category c\
    INNER JOIN film_category fc ON fc.category_id = c.category_id\
    INNER JOIN film f ON f.film_id = fc.film_id\
    WHERE c.name = '{}'\
    GROUP BY category\
    ".format(name),con=connection)
    return df  

# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(number_film_by_length())
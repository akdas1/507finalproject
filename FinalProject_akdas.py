import pandas as pd
import numpy as np
import requests
import webbrowser
import time
import json
import os
from bs4 import BeautifulSoup

api_key = 'Enter API Key Here'  # you do not need an API key since we are caching
# please input either Detroit or Ann Arbor in the command to get the cached data

class Food:
    '''Gets food data from the API and assigns attributes
    like name, latitude, longitude, address, price, yelp rating,
    and url.

    Instance Attributes
    -------------------
    name: string
        the name of the restaurant
    latitude: float
        the latitude location of the restaurant
    longitude: float
        the longitude location of the restaurant
    address: string
        the address of the restaurant
    price: string
        the price of the restaurant (1-4 dollar signs)
    rating: float
        the average rating of the restaurant
    type: string
        the type of restaurant
    url: string
        the yelp url of the restaurant
    json: string
        filepath to a json file'''
    def __init__(self, name="No Name", latitude="No Latitude",
                 longitude="No Longitude", address="No Address",
                 price="No Price", rating="No Rating", type="No Type",
                 url="No URL", json=None):
        if json == None:
            self.name = name
            self.latitude = latitude
            self.longitude = longitude
            self.address = address
            self.price = price
            self.rating = float(rating)
            self.type = type
            self.url = url
        else:
            self.name = json.get("name", "No Name")
            if isinstance(json["coordinates"], dict):
                self.latitude = json["coordinates"].get("latitude", "No Latitude")
                self.longitude = json["coordinates"].get("longitude", "No Longitude")
            else:
                self.latitude = "No Latitude"
                self.longitude = "No Longitude"
            self.address = json["location"].get("display_address", "No Address")
            self.price = json.get("price", "No Price")
            self.rating = float(json.get("rating", "No Rating"))
            if json["categories"]:
                self.type = json["categories"][0].get("title", "No Type")
            else:
                self.type = "No Type"
            self.url = json.get("url", "No URL")
    def info(self):
        '''
        Returns a string with the name, type, rating,
        and price of the restaurant'''
        return f"{self.name}, {self.type}, {self.rating}, {self.price}"

def get_map(latitude, longitude):
    '''
    Opens a web browser link to the input Google Maps location.

    Parameters
    ----------
    latitude: float
        The latitude location of the restaurant
    longitude: float
        The longitude location of the restaurant
    '''
    ## google maps uses latitude and longitude to search
    url = "https://www.google.com/maps/search/?api=1&query={},{}".format(latitude, longitude)
    webbrowser.open(url) # opens your web browser to the url

def get_api(term):
    '''
    Gets data from the Yelp API and returns a list of Restaurant
    data. Initially, it looks for a cache file. If it finds one,
    it'll load from that file. If not, it'll make a request to
    the API and save the data to a cache file. It'll also return
    50 restaurants at a time. Note, the API only allows 1000 search
    results, so this function will take a while to run. Caching
    should be faster.

    Parameters
    ----------
    term: string
        The city term for the API

    Returns
    -------
    restaurants: list
        A list of 50 Restaurants
    '''
    restaurants = []
    cache = f'{term}.json'
    filepath = os.getcwd() + '/' + cache
    ## check if cache file exists to load
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)['businesses']
        return [Food(json=r) for r in data] # returns a list of Food objects
    ## if cache file doesn't exist, make a request to the API
    else:
        headers = {
            "accept": "application/json",
            'Authorization': 'Bearer %s' % api_key}
        url = 'https://api.yelp.com/v3/businesses/search'
        for offset in range(0, 1000, 50):
            params = {'term': 'food', 'location': term, 'limit': 50, 'offset': offset}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            businesses = data['businesses']
            restaurants += businesses  # Appending new restaurants to the list
            with open(cache, 'w') as f:
                json.dump({'businesses': restaurants}, f)
        return [Food(json=r) for r in restaurants] # returns a list of Food objects

def get_top(cache, final1):
    '''
    Checks if the input restaurant is in the top scraped restaurants.
    If it is, the users will be asked if they want to learn more. If
    not, it'll print that it wasn't found.If so, it'll print the
    restaurant's name, description, address, phone number, and url.

    Parameters
    ----------
    cache: list
        A list of dictionaries of the top scraped restaurants
    final1: Food
        A Food object of the input restaurant
    '''
    found = False
    for c in cache:
        if c['name'] == final1.name:
            found = True
            print('Found in Top Restaurants!')
            while True:
                answer = input('Do you want to learn more? (yes/no): ')
                if answer.lower() == 'yes':
                    print(c['name'])
                    print(c['description'])
                    print(c['address'])
                    print(c['phone'])
                    print(c['url'])
                    break
                elif answer.lower() == 'no':
                    print('Okay!')
                    break
                else:
                    print('Try again!')
                    continue
    if not found:
        print('Not Found in Top Restaurants')

def get_types(restaurants):
    '''
    Gets a list of restaurants matching the input type.
    Appends the restaurants to a new list and returns it.
    If the list is too large, it'll only print the first 50.
    Will check if the input type is valid and in the list of
    restaurants.

    Parameters
    ----------
    restaurants: list
        a list of dictionaries of restaurants

    Returns
    -------
    new_restaurants: list
        a list of dictionaries of restaurants matching
        the input type
    '''
    new_restaurants = []
    while True:
        next = input("Do you want to filter the type of food? (yes/no): ")
        ## keeps running until user inputs yes or no
        if next.lower() == 'yes':
            valid_input = False
            while not valid_input:
                food_type = input("Enter a food type: ")
                for r in restaurants:
                    if food_type.lower() in r.type.lower():
                        new_restaurants.append(r)
                        valid_input = True
                    else:
                        continue
                if not valid_input:
                    print("No restaurants found. Try again.")
                    continue
            return new_restaurants
        elif next.lower() == 'no':
            return restaurants
        else:
            print("Invalid input. Please enter yes or no.")
            continue


def get_rating(restaurants):
    '''
    Gets a list of restaurants matching the input rating.
    Appends the restaurants to a new list and returns it.
    If the list is too large, it'll only print the first 50.

    Parameters
    ----------
    restaurants: list
        a list of dictionaries of restaurants

    Returns
    -------
    new_restaurants: list
        a list of dictionaries of restaurants matching
        the input ratng
    '''
    new_restaurants = []
    next = input("Do you want to filter the rating? (yes/no): ")
    if next.lower() == 'yes':
        ## only takes specific floats, will keep asking until valid input
        while True:
            try:
                rating = float(input("Enter a rating: "))
                if rating >= 1 and rating <= 5:
                    for r in restaurants:
                        if r.rating >= float(rating):
                            new_restaurants.append(r)
                    return new_restaurants
                else:
                    print("Invalid input. Please enter a rating between 1 and 5. Decimals must be .0 or .5.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a float.")
                continue
    elif next.lower() == 'no':
        return restaurants
    ## keeps running until user inputs yes or no
    else:
        print("Invalid input. Please enter yes or no.")
        get_rating(restaurants)

def get_price(restaurants):
    '''
    Gets a list of restaurants matching the input price.
    Also checks if the input is valid and made of dollar signs.
    Appends the restaurants to a new list and returns it.
    If the list is too large, it'll only print the first 50.

    Parameters
    ----------
    restaurants: list
        a list of dictionaries of restaurants

    Returns
    -------
    new_restaurants: list
        a list of dictionaries of restaurants matching the input price'''
    new_restaurants = []
    next = input("Do you want to filter the price? (yes/no): ")
    if next.lower() == 'yes':
        while True:
            price = input("Enter a price: ")
            ## takes specific dollar sign amounts, will keep asking until valid input
            if price == '$' or price == '$$' or price == '$$$' or price == '$$$$':
                for i in restaurants:
                    if i.price == price:
                        new_restaurants.append(i)
                return new_restaurants
            else:
                print("Invalid price. Please enter 1-4 dollar signs.")
                continue
    elif next.lower() == 'no':
        return restaurants
    ## keeps running until user inputs yes or no
    else:
        print("Invalid input. Please enter yes or no.")
        get_price(restaurants)

def final_step(final, cache):
    '''
    Takes in a list and checks if it contains one or more restaurants.
    If the list contains one restaurant, it will print the final
    results and asks the user if they want to get directions to the
    restaurant. If it contains more than one restaurant, the user can
    choose which restaurant to get directions to. If the user enters yes,
    it'll call the get_map function to open a Google Maps link to the
    restaurant's location. If the user enters no, it'll end the session.
    If the user inputs a wrong value, it'll ask them to enter yes or no
    again.

    Will also ask the user if they want to check if the restaurant is
    included within a top restaurant webpage. If the user enters yes,
    and it is included they can learn more about the restaurant. If
    the user enters no, or the restaurant is not included, it'll end.

    Parameters
    ----------
    final: list
        a list of dictionaries of restaurants

    cache: list
        a list of dictionaries of restaurants and their information

    Returns
    -------
    None
    '''
    print(' ')
    print('Final Results')
    print('---------------------------')
    ## prints the first 50 results
    for i, r in enumerate(final[:50]):
        print(f"{i}. {r.info()}")
    ## if 1, asks if user wants directions to the restaurant
    if len(final) == 1:
        while True:
            print(' ')
            ans = input("Would you like to see if your restaurant is part of Eater's Top Restaurants? (yes/no): ")
            if ans.lower() == 'yes':
                final1 = r
                get_top(cache, final1)
                break
            elif ans.lower() == 'no':
                print(' ')
                print('Understood.')
            else:
                # only accepts yes or no
                print('Invalid input. Please enter yes or no.')
                continue
            answer = input("Would you like to get directions to this restaurant? (yes/no): ")
            if answer.lower() == 'yes':
                get_map(r.latitude, r.longitude)
                break
            elif answer.lower() == 'no':
                print(' ')
                print('Session Ended')
                break
            else:
                # only accepts yes or no
                print('Invalid input. Please enter yes or no.')
                continue
    ## if multiple, asks which restaurant they want directions to
    elif len(final) > 1:
        print(' ')
        ans = input("Please pick a number of a restaurant: ")
        while True:
            if ans.isdigit():
                if int(ans) < len(final) and int(ans) >= 0:
                    ans1 = input("Would you like to see if your restaurant is part of Eater's Top Restaurants? (yes/no): ")
                    while True:
                        if ans1.lower() == 'yes':
                            final1 = final[int(ans)]
                            get_top(cache, final1)
                            break
                        elif ans1.lower() == 'no':
                            print(' ')
                            print('Understood.')
                            break
                        else:
                            # only accepts yes or no
                            print('Invalid input. Please enter yes or no.')
                            continue
                else:
                    print('Invalid input. Please enter a valid number.')
                    continue
            answer = input("Would you like to get directions to this restaurant? (yes/no): ")
            while True:
                if answer.lower() == 'yes':
                    get_map(final[int(ans)].latitude, final[int(ans)].longitude)
                    break
                elif answer.lower() == 'no':
                    print(' ')
                    print('Thanks for playing!')
                    break
                else:
                    # only accepts yes or no
                    print('Invalid input. Please enter yes or no.')
                    continue
            break
def webscrape(term):
    '''
    Takes in a city and scrapes a website for a list of top restaurants
    and their descriptions. It then returns a list of dictionaries
    containing the restaurant names and descriptions.

    Parameters
    ----------
    city: string
        a string of the city name

    Returns
    -------
    complete: list
        a list of dictionaries of top restaurants and their information
    '''
    restaurants = []
    descriptions = []
    addresses = []
    phone_num = []
    website = []
    if term.lower() == 'Detroit'.lower():
        cache = f'{term}_webscrape.json'
        filepath = os.getcwd() + '/' + cache
        ## check if cache file exists to load
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data # returns a list of dictionaries
        url = 'https://detroit.eater.com/maps/best-restaurants-detroit-38'
        result = requests.get(url)
        doc = BeautifulSoup(result.text, 'html.parser')
        rest = doc.find_all('div', {'class': 'c-mapstack__card-hed'})
        rest1 = doc.find_all('div', {'class': 'c-entry-content venu-card'})
        rest2 = doc.find_all('div', {'class': 'c-mapstack__address'})
        rest3 = doc.find_all('div', {'class': 'c-mapstack__phone desktop-only'})
        rest4 = doc.find_all('div', {'class': 'info'})
        for div in rest:
            restaurant = {}
            d = div.find('div')
            h1 = d.find('h1')
            if h1:
                restaurant['name'] = h1.text.strip()
                restaurants.append(restaurant)
        for div in rest1:
            desc = {}
            p = div.find('p')
            if p:
                ul = p.find_next_sibling('ul', {'class': 'services'})
                if ul:
                    desc['description'] = p.text[:p.text.index(ul.text)]
                else:
                    desc['description'] = p.text
                if desc not in descriptions:
                    descriptions.append(desc)
        for div in rest2:
            address = {}
            a = div.find('a')
            if a:
                address['address'] = a.text
                addresses.append(address)
        for div in rest3:
            phone = {}
            a = div.find('a')
            if a:
                phone['phone'] = a.text
                phone_num.append(phone)
        for div in rest4:
            web = {}
            d = div.find_all('div')[1]
            a = d.find('a', {'data-analytics-link': 'link-icon'})
            if a:
                web['url'] = a['href']
                website.append(web)
    elif term.lower() == 'Ann Arbor'.lower() or term.lower() == 'Ann_Arbor'.lower():
        cache = '/Ann_Arbor_webscrape.json' # wasn't reading term
        filepath = os.getcwd() + cache
        ## check if cache file exists to load
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data # returns a list of dictionaries
        url = 'https://detroit.eater.com/maps/best-ann-arbor-restaurants'
        result = requests.get(url)
        doc = BeautifulSoup(result.text, 'html.parser')
        rest = doc.find_all('div', {'class': 'c-mapstack__card-hed'})
        rest1 = doc.find_all('div', {'class': 'c-entry-content venu-card'})
        rest2 = doc.find_all('div', {'class': 'c-mapstack__address'})
        rest3 = doc.find_all('div', {'class': 'c-mapstack__phone desktop-only'})
        rest4 = doc.find_all('div', {'class': 'info'})
        ## storing restaurant names and descriptions separately
        for div in rest:
            restaurant = {}
            d = div.find('div')
            h1 = d.find('h1')
            if h1:
                restaurant['name'] = h1.text.strip()
                restaurants.append(restaurant)
        for div in rest1:
            desc = {}
            p = div.find('p')
            if p:
                desc['description'] = p.text
                descriptions.append(desc)
        for div in rest2:
            address = {}
            a = div.find('a')
            if a:
                address['address'] = a.text
                addresses.append(address)
        for div in rest3:
            phone = {}
            a = div.find('a')
            if a:
                phone['phone'] = a.text
                phone_num.append(phone)
        for div in rest4:
            web = {}
            d = div.find_all('div')[1]
            a = d.find('a', {'data-analytics-link': 'link-icon'})
            if a:
                web['url'] = a['href']
                website.append(web)
    ## the lists originally stored like name, name, description, description
    # reordering the list of dictionaries
    for i in range(len(restaurants)):
        restaurants[i].update(descriptions[i])
        restaurants[i].update(addresses[i])
        restaurants[i].update(phone_num[i])
        restaurants[i].update(website[i])
        cache_webscrape(cache, restaurants)
    return restaurants

def cache_webscrape(cache, restaurant):
    '''
    Caches the data from the websites into a JSON file.

    Parameters
    ----------
    restaurant: list
        a list of dictionaries of restaurants and their information

    Returns
    -------
    None
    '''
    with open(cache, 'w') as f:
        json.dump(restaurant, f)

def main():
    '''
    Main function that runs the program.

    Parameters
    ----------
    None
    '''
    ## the cache file is named 'Ann_Arbor.json'
    # removes chance for error if user inputs Ann Arbor
    term = input("Enter a city: ")
    if term.lower() == 'Ann Arbor'.lower():
        term = 'Ann_Arbor'
    cache = webscrape(term)
    res = get_api(term)
    restaurants = []
    while True:
        ## if there are no city results or a typo, ask for input again
        if len(res) == 0:
            term = input("No results. Enter a city: ")
            res = get_api(term)
            continue
        ## user can choose to exit
        elif term.lower() == 'exit':
            print('Session Ended')
            time.sleep(1)
            quit()
        else:
            for r in res:
                restaurants.append(r)
            print(' ')
            print('Printing the first 50 of 1000 results')
            print('---------------------------')
            for r in restaurants[:50]:
                print(r.info())
        break
    while True:
        new_restaurants = get_types(restaurants)
        ## if there are no results or a typo, ask for input again
        if new_restaurants == None:
            print(' ')
            print('No results found. Please try again.')
            continue
        elif len(new_restaurants) == 1:
            ## if only one restaurant, jumps to final step
            final_step(new_restaurants, cache=cache)
            print('Session Ended')
            break
        else:
            ## ignores if the user doesn't want to filter by type
            if new_restaurants != restaurants:
                print(' ')
                print('Previewing up to 50 results')
                print('---------------------------')
                for r in new_restaurants[:50]:
                    print(r.info())
            break
    while True:
        new_restaurants1 = get_rating(new_restaurants)
        ## if there are no results or a typo, ask for input again
        if new_restaurants1 == None:
            print(' ')
            print('No results found. Please try again.')
            continue
        elif len(new_restaurants1) == 1:
            ## if only one restaurant, jumps to final step
            final_step(new_restaurants1, cache=cache)
            print('Session Ended')
            time.sleep(1)
            quit()
        else:
            ## ignores if the user doesn't want to filter by rating
            if new_restaurants1 != new_restaurants:
                print(' ')
                print('Previewing up to 50 results')
                print('---------------------------')
                for r in new_restaurants1[:50]:
                    print(r.info())
            break
    while True:
        ## if there are no results or a typo, ask for input again
        final = get_price(new_restaurants1)
        if final == None:
            print(' ')
            print('No results found. Please try again.')
            continue
        else:
            break

    ## adding to json file
    final_dict = {}
    rests = []
    for r in restaurants:
        rests.append(r.info())
    final_dict['initial results'] = rests
    rests1 = []
    for r in new_restaurants:
        if r is None:
            rests1.append('No results')
        else:
            rests1.append(r.info())
    final_dict['type results'] = rests1
    rests2 = []
    for r in new_restaurants1:
        if r is None:
            rests2.append('No results')
        else:
            rests2.append(r.info())
    final_dict['rating results'] = rests2
    rests3 = []
    for r in final:
        if r is None:
            rests3.append('No results')
        else:
            rests3.append(r.info())
    final_dict['price results'] = rests3
    with open('tree.json', 'w') as f:
        json.dump(final_dict, f)
    ## runs the final step
    final_step(final, cache=cache)
if __name__ == "__main__":
    main()

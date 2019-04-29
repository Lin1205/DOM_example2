#
#   Simple little project to compile and analyze real estate data
#
#   http://predictablynoisy.com/querying-craigslist-with-python/
#
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bsoup


def find_size_and_brs(size):
    split = size.strip('/-\n ').split(' -\n ')
    split = [ x.strip() for x in split]
    if len(split) == 2:
        n_brs = split[0].replace('br', '')
        this_size = split[1].replace('ft2', '')
    elif 'br' in split[0]:
        # It's the n_bedrooms
        n_brs = split[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in split[0]:
        # It's the size
        this_size = split[0].replace('ft2', '')
        n_brs = np.nan
    return float(this_size), float(n_brs)


def find_prices(results):
    prices = []
    for rw in results:
        price = rw.find('span', {'class': 'price'})
        if price is not None:
            price = float(price.text.strip('$'))
        else:
            price = np.nan
        prices.append(price)
    return prices


def find_times(results):
    times = []
    for rw in apts:
        if time is not None:
            time = time['datetime']
            time = pd.to_datetime(time)
        else:
            time = np.nan
        times.append(time)
    return times


# Query Craigslist

loc = 'eby'
neighborhood = 65 # Richmond
min_rent = 3000
min_beds = 2
url_base = 'http://sfbay.craigslist.org/search/{0}/apa'.format(loc)
params = dict(bedrooms = min_beds,
              query= 'house',
              nh = neighborhood,
              min_price = min_rent)
              # parking = 1,
              # parking = 2,
              # parking = 3,
              # parking = 4)

rsp = requests.get(url_base, params=params)

print(rsp.text[:500])

# BS4 can quickly parse our text, make sure to tell it that you're giving html
html = bsoup(rsp.text, 'html.parser')

# BS makes it easy to look through a document
print(html.prettify()[:1000])

# find_all will pull entries that fit your search criteria.
# Note that we have to use brackets to define the `attrs` dictionary
# Because "class" is a special word in python, so we need to give a string.
props = html.find_all('p', attrs={'class': 'row'})
print(len(props))

# We can see that there's a consistent structure to a listing.
# There is a 'time', a 'name', a 'housing' field with size/n_brs, etc.
this_prop = props[0]
print(this_prop.prettify())

# So now we'll pull out a couple of things we might be interested in:
# It looks like "housing" contains size information. We'll pull that.
# Note that `findAll` returns a list, since there's only one entry in
# this HTML, we'll just pull the first item.
size = this_prop.findAll(attrs={'class': 'housing'})[0].text
print(size)

this_size, n_brs = find_size_and_brs(size)

# Now we'll also pull a few other things:
this_time = this_prop.find('time')['datetime']
this_time = pd.to_datetime(this_time)
this_price = float(this_prop.find('span', {'class': 'price'}).text.strip('$'))
this_title = this_prop.find('a', attrs={'class': 'hdrlnk'}).text

# Now we've got the n_bedrooms, size, price, and time of listing
print('\n'.join([str(i) for i in [this_size, n_brs, this_time, this_price, this_title]]))

# Iterate over listings

# Now loop through all of this and store.py the results
results = []  # We'll store.py the data here
# Careful with this...too many queries == your IP gets banned temporarily
search_indices = np.arange(0, 300, 100)



for i in search_indices:
    url = 'http://sfbay.craigslist.org/search/{0}/apa'.format(loc)
    resp = requests.get(url, params={'bedrooms': 1, 's': i})
    txt = bs4(resp.text, 'html.parser')
    apts = txt.findAll(attrs={'class': "row"})

    # Find the size of all entries
    size_text = [rw.findAll(attrs={'class': 'housing'})[0].text
                 for rw in apts]
    sizes_brs = [find_size_and_brs(stxt) for stxt in size_text]
    sizes, n_brs = zip(*sizes_brs)  # This unzips into 2 vectors

    # Find the title and link
    title = [rw.find('a', attrs={'class': 'hdrlnk'}).text
             for rw in apts]
    links = [rw.find('a', attrs={'class': 'hdrlnk'})['href']
             for rw in apts]

    # Find the time
    time = [pd.to_datetime(rw.find('time')['datetime']) for rw in apts]
    price = find_prices(apts)

    # We'll create a dataframe to store.py all the data
    data = np.array([time, price, sizes, n_brs, title, links])
    col_names = ['time', 'price', 'size', 'brs', 'title', 'link']
    df = pd.DataFrame(data.T, columns=col_names)
    df = df.set_index('time')

    # Add the location variable to all entries
    df['loc'] = loc
    results.append(df)

# Finally, concatenate all the results
results = pd.concat(results, axis=0)


### Top level CL housing search
#
## Search for houses in SF Bay Area
#
# Apartment => housing_type=1
# House => housing_type=6
# In law => housing_type=7
# townhouse => housing_type=9
# Duplex => housing_type=4
#
###
#   Houses in Richmond
#   https://sfbay.craigslist.org/search/eby/apa?nh=65&availabilityMode=0&housing_type=6&sale_date=all+dates
#
# nh=#
# 46 "alameda"
# 47 "albany / el cerrito"
# 48 "berkeley"
# 49 "berkeley north / hills"
# 51 "concord / pleasant hill / martinez"
# 52 "danville / san ramon"
# 53 "dublin / pleasanton / livermore"
# 55 "hayward / castro valley"
# 56 "hercules, pinole, san pablo, el sob"
# 62 "oakland north / temescal"
# 64 "oakland west"
# 65 "richmond"
# 67 "san leandro"
# 112 "emeryville"
# 113 "pittsburg / antioch"
# 154 "fairfield / vacaville"
#
#
# Retrieve CL data for specified neighborhood
# payload = {'nh':67, 'availabilityMode':0, 'housing_type':6, 'sale_date': 'all+dates'}
payload = {'availabilityMode':0, 'housing_type':6, 'sale_date': 'all+dates'}
resp = requests.get('https://sfbay.craigslist.org/search/eby/apa', params=payload)

txt = bsoup(resp.text, 'html.parser')

# Determine total number of results
num_listings = int(txt.find('span', class_="totalcount").text)

if num_listings < 120:
    # If this number is < 120, one page, else need to work through pages with query param
    #
    #   Initial get https://sfbay.craigslist.org/search/apa?availabilityMode=0&housing_type=6&sale_date=all+dates
    #   Second page https://sfbay.craigslist.org/search/apa?s=120&availabilityMode=0&housing_type=6
    #   Third page  https://sfbay.craigslist.org/search/apa?s=240&availabilityMode=0&housing_type=6


    # Create a list of results objects
    li = txt.find_all('li', class_='result-row')

    # For each object extract elements of interest
    for ind in len(li):

        li_data_id = li[ind].find(class_="result-title hdrlnk").get("data-id")
        li_title = li[ind].find(class_="result-title hdrlnk").text
        li_price = li[ind].find(class_='result-price').text
        li_href = li[ind].find(class_="result-title hdrlnk").get('href')

        # Details link
        resp_li = requests.get(li_href)
        txt_li = bsoup(resp_li.text, 'html.parser')

        txt_li.find('div', class_='viewposting').get("data-latitude")
        txt_li.find('div', class_='viewposting').get("data-longitude")
        txt_li.find('section', id="postingbody")   # Text description of listing

        # Find structured property attributes
        txt_attrib = txt_li.find_all('p', class_="attrgroup")

        # Clean up and tokenize attributes
        txt_li_attribs = []
        for attribs in txt_attrib:

            raw_attribs = attribs.text.split('\n')
            keepers = [ x for x in raw_attribs if x != '']
            txt_li_attribs += keepers

        # TODO: Collect images

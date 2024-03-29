#-----------------------------------------------------------------------------------------------------------------------------------------------
#  NLAddressLocator.py
#  Author: Egge-Jan Pollé
#  Date: 10 February 2024
#  Version: 0.2
#-----------------------------------------------------------------------------------------------------------------------------------------------
#  With this little python (3.x) script you can retrieve full address details (including X and Y coordinates) for addresses in the Netherlands.
#  You can start by entering only part of the address, e.g. only Street and Town, or Postal Code and House Number. The script will return
#  up to 15 suggestions to choose from. The output will be written to a csv file in the same directory as the script.
#
#  The script uses the API of the Locatieserver (v3_1), the geocoding service for the Netherlands, offered by PDOK (https://www.pdok.nl/)   
#-----------------------------------------------------------------------------------------------------------------------------------------------

import urllib.parse, json, re, csv, os.path
from urllib.request import urlopen

def file_len(fname):
    count = 0
    with open(fname) as f:
        for line in f:
            count += 1
    return count
    
# Empty dictionary to store the details of an address
address = {}
options = []

# The entries for the address dictionary
fieldnames = ['Description','Street','House_number','Postal_code','Place_name','Municipality','Province', 'RD_X_coord','RD_Y_coord']

# Step 1: retrieve suggestions (up to 15)
search_string = input('Please enter (a part of) the address you are looking for: ')
search_string = search_string + ' and type:adres'

url_suggest = 'https://api.pdok.nl/bzk/locatieserver/search/v3_1/suggest?'
url_suggest_params = {'rows': 15, 'q':  search_string}
url_suggest = url_suggest + urllib.parse.urlencode(url_suggest_params)

response1 = urlopen(url_suggest)
suggestions = json.loads(response1.read())

if suggestions['response']['numFound'] == 0:
    print('No results found. (You can restart the script to search again.)')
else:
    if suggestions['response']['numFound'] == 1:
        print('A single address was found:')
        print(suggestions['response']['docs'][0]['weergavenaam'])
        address_id = suggestions['response']['docs'][0]['id']
    else:
        print('Multiple options were found:')
        j = 0
        for suggestion in suggestions['response']['docs']:
            j += 1
            print(str(j)+': '+suggestion['weergavenaam'])
        options.extend(range(1, j+1))
        number_chosen = input('Please select an entry (1-%s) from the list, or press 0 to quit: ' % str(j))
        if int(number_chosen) in options:
            print('You hhave chosen the following address:')
            print(suggestions['response']['docs'][int(number_chosen) - 1]['weergavenaam'])
            address_id = suggestions['response']['docs'][int(number_chosen) - 1]['id']
        else:
            print()
            print('You can restart the script to search again.')
            quit()

# Step 2: lookup the full address details based on the address_id found or chosen

    url_lookup = 'https://api.pdok.nl/bzk/locatieserver/search/v3_1/lookup?id=%s' % address_id
    response2 = urlopen(url_lookup)
    address_details = json.loads(response2.read())

    # Populate the dictionary
    for detail in address_details['response']['docs']:
        address['Street'] = (detail['straatnaam'])
        address['House_number'] = (detail['huis_nlt'])
        if 'postcode' in detail: # Somehow, don't know why, the Locatieserver sometimes returns addresses without a postal code...
            address['Postal_code'] = (detail['postcode'])
        address['Place_name'] = (detail['woonplaatsnaam'])
        address['Municipality'] = (detail['gemeentenaam'])
        address['Province'] = (detail['provincienaam'])
        # use a regular expression to extract the X and Y coordinates (in RD/EPSG:28992) from the value 'centroide_rd'
        coords = re.findall('\d+[.]?\d+', detail['centroide_rd'])
        address['RD_X_coord'] = (coords[0])
        address['RD_Y_coord'] = (coords[1])

# Step 3: add a little description
    print()
    address['Description'] = input('Optionally: add a description to the address (press enter to leave it blank): ')
    
# Step 4: print output to a file
    fname = 'addresses.csv'
    outfile = open(fname, 'a', encoding = 'utf-8') # To write data encoded as UTF-8, make sure to open/create your .csv files with UTF-8 encoding
    writer = csv.DictWriter(outfile, delimiter = ';', lineterminator='\n', fieldnames=fieldnames)
    if file_len(fname) == 0: 
        writer.writeheader()
    writer.writerow(address)
    
    print()
    print('The address details (including x and y coordinates) have been written to the following file:')
    print(os.path.abspath(fname))
    print()
    print('You can restart the script to search again.')
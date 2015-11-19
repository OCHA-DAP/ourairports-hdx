#!/usr/bin/python3
"""Create per-country datasets for OurAirports airport lists

http://ourairports.com

See README.md for more details.

Started 2015-11-18 by David Megginson
"""

import ckanapi
import hxl
import urllib

# read configuration values from config.py
import config

#
# Constants
#

INPUTS_URL = 'https://docs.google.com/spreadsheets/d/1CuecXwSYOeW1fa7bqs00H3unprRCAxsYFB94a3O0-Ag/edit#gid=0'
RESOURCE_URL_TEMPLATE = 'http://ourairports.com/countries/{code}/airports.{format}'


#
# Create the CKAN API object
#
ckan = ckanapi.RemoteCKAN(config.CONFIG['ckanurl'], apikey=config.CONFIG['apikey'], user_agent=config.CONFIG.get('user_agent', None))

#
# Loop through every HXL data row in the source spreadsheet (INPUTS_URL)
#

for row in hxl.data(INPUTS_URL, True):

    # Skip if there's no M49 code for HDX
    hdx_code = row.get('country+code+m49')
    if not hdx_code:
        continue

    country = row.get('country+name+en')
    ourairports_code = row.get('country+code+iso2')
    stub = 'ourairports-{code}'.format(code=hdx_code.lower())


    # Create the basic dataset object, with an empty list of resources
    dataset = {
        'name': stub,
        'title': 'Airports in {country}'.format(country=country),
        'notes': 'List of airports in {country}, with latitude and longitude. '
                 'Unverified community data from http://ourairports.com/countries/{code}/'.format(
                     country=country,
                     code=ourairports_code
                 ),
        'dataset_source': 'OurAirports.com community web site.',
        'private': False,
        'subnational': True,
        'owner_org': 'ourairports',
        'package_creator': 'script',
        'license_id': 'Public Domain',
        'methodology': 'Other',
        'caveats': 'Unverified live data. May change at any time.',
        'groups': [{'id': hdx_code.lower()}],
        'tags': [
            {'name': 'aviation'}, 
            {'name': 'geodata'},
            {'name': 'airports'},
            {'name': 'transportation'},
            {'name': 'facilities'},
            {'name': 'hxl'}
        ],
        'resources': []
    }

    # Add resources to the dataset
    for format in ['hxl', 'csv']:
        dataset['resources'].append({
            'name': 'List of airports in {country} ({notes})'.format(
                country=country,
                notes='HXL tags' if format == 'hxl' else 'no HXL tags'
            ),
            'description': 'Spreadsheet listing airports in {country}. '
                           'Unverified member-uploaded data. '
                           'Note that this data comes live from the web site, and can change at any time.'.format(country=country),
            'url': RESOURCE_URL_TEMPLATE.format(format=format, code=ourairports_code, filename='airports-{code}.{format}'.format(
                code=ourairports_code.lower(),
                format=format
            )),
            'format': 'csv'
        })

    # Try creating the dataset on CKAN, and if that fails, update instead
    try:
        ckan.call_action('package_create', dataset)
        print("Created {stub}...".format(stub=stub))
    except:
        ckan.call_action('package_update', dataset)
        print("Updated {stub}...".format(stub=stub))

exit(0)

# end

"""
A command line utility for creating OAI harvesters for scrapi.

Creates new files in a scrapi repo that is hosted one directory up from this one.

  -h, --help            show this help message and exit
  -b BASEURL, --baseurl BASEURL
                        The base url for the OAI provider, everything before
                        the ?
  -s SHORTNAME, --shortname SHORTNAME
                        The shortname of the provider
  -f, --favicon         flag to signal saving favicon
  -d DAYS_BACK, --days_back DAYS_BACK
                        Number of days back to make the properties request

example usage: python main.py -b http://udspace.udel.edu/dspace-oai/request -s udel -f -d 30

"""

import shutil
import argparse
import requests
from lxml import etree
from datetime import date, timedelta


NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/',
              'oai_dc': 'http://www.openarchives.org/OAI/2.0/',
              'ns0': 'http://www.openarchives.org/OAI/2.0/'}
BASE_SCHEMA = ['title', 'contributor', 'creator', 'subject', 'description']


def get_oai_properties(base_url, days_back):
    """ Makes 2 requests to the provided base URL:
        1 for the sets available
        1 for the list of properties

        returns a dict with list of properties, and set_groups.

        Set groups is a list of tuples - first element is short name,
        second element is the long descriptive name.

        The sets available are added as multiple selections for the next form,
        the properties are pre-loaded into the properties field.
    """
    try:
        # request for records 30 days back just in case
        start_date = str(date.today() - timedelta(days_back))
        prop_url = base_url + '?verb=ListRecords&metadataPrefix=oai_dc&from={}T00:00:00Z'.format(start_date)
        print('requesting {}'.format(prop_url))
        prop_data_request = requests.get(prop_url)
        all_prop_content = etree.XML(prop_data_request.content)
        try:
            pre_names = all_prop_content.xpath('//ns0:metadata', namespaces=NAMESPACES)[0].getchildren()[0].getchildren()
        except IndexError:
            prop_url = base_url + '?verb=ListRecords&metadataPrefix=oai_dc&from={}'.format(start_date)
            prop_data_request = requests.get(prop_url)
            all_prop_content = etree.XML(prop_data_request.content)
            pre_names = all_prop_content.xpath('//ns0:metadata', namespaces=NAMESPACES)[0].getchildren()[0].getchildren()

        all_names = [name.tag.replace('{' + NAMESPACES['dc'] + '}', '') for name in pre_names]
        return list({name for name in all_names if name not in BASE_SCHEMA})

    # If anything at all goes wrong, just render a blank form...
    except Exception as e:
        raise ValueError('OAI Processing Error - {}'.format(e))


def formatted_oai(ex_call, class_name, shortname, longname, normal_url, oai_url, prop_list, tz_gran):

    return """'''
Harvester for the ASU Digital Repository for the SHARE project

Example API call: {0}
'''

from __future__ import unicode_literals
from scrapi.base import OAIHarvester


class {1}Harvester(OAIHarvester):
    short_name = '{2}'
    long_name = '{3}'
    url = '{4}'

    base_url = '{5}'
    property_list = {6}
    timezone_granularity = {7}
""".format(ex_call, class_name, shortname, longname, normal_url, oai_url, prop_list, tz_gran)


def get_id_props(baseurl):
    identify_url = baseurl + '?verb=Identify'
    id_data_request = requests.get(identify_url)
    id_content = etree.XML(id_data_request.content)
    return id_content.xpath('//ns0:repositoryName/node()', namespaces=NAMESPACES)[0], id_content.xpath('//ns0:granularity/node()', namespaces=NAMESPACES)[0]


def get_favicon(baseurl, shortname):
    r = requests.get('http://grabicon.com/icon?domain={}&origin=cos.io&size=16'.format(baseurl), stream=True)
    if r.status_code == 200:
        with open('../scrapi/img/favicons/{}_favicon.ico'.format(shortname), 'w') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface to create and commit a new harvester")

    parser.add_argument('-b', '--baseurl', dest='baseurl', type=str, required=True, help='The base url for the OAI provider, everything before the ?')
    parser.add_argument('-s', '--shortname', dest='shortname', type=str, required=True, help='The shortname of the  provider')
    parser.add_argument('-f', '--favicon', dest='favicon', help='flag to signal saving favicon', action='store_true')
    parser.add_argument('-d', '--days_back', dest='days_back', type=int, required=False, help='Number of days back to make the properties request')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.days_back:
        days_back = args.days_back
    else:
        days_back = 30

    prop_list = get_oai_properties(args.baseurl, days_back)
    ex_call = args.baseurl + '?verb=ListRecords&metadataPrefix=oai_dc'
    class_name = args.shortname.capitalize()
    longname, tz_gran = get_id_props(args.baseurl)

    if 'hh:mm:ss' in tz_gran:
        tz_gran = True
    else:
        tz_gran = False

    text = formatted_oai(ex_call, class_name, args.shortname, longname, args.baseurl, args.baseurl, prop_list, tz_gran)

    with open('../scrapi/scrapi/harvesters/{}.py'.format(args.shortname), 'w') as outfile:
        outfile.write(text)

    if args.favicon:
        get_favicon(args.baseurl, args.shortname)


if __name__ == '__main__':
    main()

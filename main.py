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

import vcr
import shutil
import argparse
import requests
import tldextract
from lxml import etree
from datetime import date
from datetime import datetime


NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/',
              'oai_dc': 'http://www.openarchives.org/OAI/2.0/',
              'ns0': 'http://www.openarchives.org/OAI/2.0/'}
BASE_SCHEMA = ['title', 'contributor', 'creator', 'subject', 'description', 'language', 'publisher']


def get_oai_properties(base_url, shortname):
    """ Makes a request to the provided base URL for the list of properties

        returns a dict with list of properties
    """

    try:
        start_date = date.today().isoformat() - datetime.timedelta(1)
        end_date = date.today().isoformat()
        with vcr.use_cassette('../scrapi/tests/vcr/{}.yaml'.format(shortname)):
            prop_url = base_url + '?verb=ListRecords&metadataPrefix=oai_dc&from={}&until={}'.format(start_date, end_date)
        print('requesting {}'.format(prop_url))
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
Harvester for the {0} for the SHARE project

Example API call: {1}
'''
from __future__ import unicode_literals

from scrapi.base import OAIHarvester


class {2}Harvester(OAIHarvester):
    short_name = '{3}'
    long_name = '{4}'
    url = '{5}'

    base_url = '{6}'
    property_list = {7}
    timezone_granularity = {8}
""".format(longname, ex_call, class_name, shortname, longname, normal_url, oai_url, prop_list, tz_gran)


def simple_oai(class_name, shortname, longname, baseurl, prop_list, tz_gran):

    return """

class {class_name}Harvester(OAIHarvester):
    '''Harvester for {longname}
    Sample API Call = {baseurl}?verb=ListRecords&metadataPrefix=oai_dc
    '''

    short_name = '{shortname}'
    long_name = '{longname}'
    url = '{baseurl}'

    base_url = '{baseurl}'
    property_list = {prop_list}
    timezone_granularity = {tz_gran}
""".format(class_name=class_name, shortname=shortname, longname=longname, baseurl=baseurl, prop_list=prop_list, tz_gran=tz_gran)


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


def get_bepress():
    site = requests.get('http://digitalcommons.bepress.com/subscriber_gallery/')
    elements = etree.HTML(site.text).xpath('//div[@id ="gallery"]/div/ul/li/a')

    return [item.values()[0] for item in elements]


def generate_bepress():
    bepress_sites = get_bepress()
    for link in bepress_sites:
        shortname = ''
        x = tldextract.extract(link)
        if x.subdomain and x.subdomain != 'www':
            shortname = shortname + x.subdomain + '_'
        shortname += x.domain
        baseurl = link + '/do/oai/'
        text = generate_bepress_text(baseurl, shortname)

        with open('../scrapi/scrapi/harvesters/bepress.py', 'a') as outfile:
            outfile.write(text)


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface to create and commit a new harvester")

    parser.add_argument('-b', '--baseurl', dest='baseurl', type=str, help='The base url for the OAI provider, everything before the ?')
    parser.add_argument('-s', '--shortname', dest='shortname', type=str, help='The shortname of the  provider')
    parser.add_argument('-f', '--favicon', dest='favicon', help='flag to signal saving favicon', action='store_true')
    parser.add_argument('-bp', '--bepress', dest='bepress', help='flag to signal generating bepress list', action='store_true')

    return parser.parse_args()


def generate_bepress_text(baseurl, shortname):
    prop_list = get_oai_properties(baseurl, shortname)

    parts = shortname.replace('.', '').replace('-', '').split('_')
    class_name = ''
    for part in parts:
        class_name += part.capitalize()

    longname, tz_gran = get_id_props(baseurl)

    if 'hh:mm:ss' in tz_gran:
        tz_gran = True
    else:
        tz_gran = False

    return simple_oai(class_name, shortname, longname, baseurl, prop_list, tz_gran)


def generate_oai(baseurl, shortname):
    prop_list = get_oai_properties(baseurl, shortname)
    ex_call = baseurl + '?verb=ListRecords&metadataPrefix=oai_dc'
    class_name = shortname.capitalize()
    longname, tz_gran = get_id_props(baseurl)

    if 'hh:mm:ss' in tz_gran:
        tz_gran = True
    else:
        tz_gran = False

    return formatted_oai(ex_call, class_name, shortname, longname, baseurl, baseurl, prop_list, tz_gran)


def main():
    args = parse_args()

    if args.baseurl:
        text = generate_oai(args.baseurl, args.shortname)

        with open('../scrapi/scrapi/harvesters/{}.py'.format(args.shortname), 'w') as outfile:
            outfile.write(text)

    if args.favicon:
        get_favicon(args.baseurl, args.shortname)

    if args.bepress:
        generate_bepress()


if __name__ == '__main__':
    main()

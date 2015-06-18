# autooai

Automatically create an OAI harvester for the [SHARE Project](https://osf.io/wur56/wiki/home/).

In order to automatically generate a harvester, it's assumed you'll have an API endpoint that will return xml in standard OAI-PMH format. This will be your base URL!

For example, mit has an OAI PMH endpoint, and one of the ways to access it is:
http://dspace.mit.edu/oai/request?verb=Identify

Since this tool is specfically for the SHARE project, you should be running commands from a directory that is inside a directory on the same level as your [scrapi](http://github.com/fabianvf/scrapi) (or SHARE core) directory.

Your directory structure should be something like this:

```
code
├── autooai
├── scrapi
```

That way, your newly generated OAI harvesters will be generated in the correct folder within your scrapi instance - namely within

```
scrapi/scrapi/harvesters
```

---
## Setup

From within the autooai directory...

Install requirements using [pip](https://pypi.python.org/pypi/pip) inside a [virtual enviornment](https://virtualenv.pypa.io/en/latest/) by running 

```pip install -r requirements.txt```

Once you've installed all the requirements, you're ready to get started generating OAI-PMH harvesters for SHARE!

----

## Generating a Harvester

Autooai is a command line tool that takes a few arguments and will generate a SHARE harvester based on those arguments. 

Here's an example of how to use this tool to generate a SHARE OAI harvester for the MIT repository:

```
python main.py -b http://dspace.mit.edu/oai/request -s mit -f
```

This will do a few things:
- Use the baseurl of http://dspace.mit.edu/oai/request to generate a harvester
    + This baseurl is the begning of the oai endpoint, and includes everything before the ? in the oai pmh request url
    + Example: http://repository.stcloudstate.edu/do/oai/
    + Not:  http://repository.stcloudstate.edu/do/oai/?verb=Identify
- Use mit as the shortname when generating the harvester
- save the MIT favicon to the proper directory within scrapi (scrapi/img/favicons)

Here's the main usage:

```
usage: main.py [-h] -b BASEURL -s SHORTNAME [-f]

A command line interface to create and commit a new harvester

required arguments:
  -b BASEURL, --baseurl BASEURL
                        The base url for the OAI provider, everything before
                        the ?
  -s SHORTNAME, --shortname SHORTNAME
                        The shortname of the provider

optional arguments:
  -f, --favicon         flag to signal saving favicon

  -h, --help            show this help message and exit
```

## Running your new harvester

Assuming you've already done all of the setup for [scrapi](https://github.com/fabianvf/scrapi), you're ready to run the harvester you've just generated, and try to gather some data into scrapi.

Enter the scrapi directory, one up from your current autooai directory ```cd ../scrapi```

Run the harvester using invoke and the shortname you created the harvester with

```invoke harvester insert-shortname-here```

You can then check out the results on your local elasticsearch instance running on http://localhost:9200/share_v2/_search

If you're running the [OSF](https://github.com/CenterForOpenScience/osf.io) locally, you can explore search results on localhost:5000/share after running 
```invoke provider_map```

Run tests on scrapi, including your newly created harvester test, with ```invoke test```

## Potential Pitfalls

### elasticsearch index errors

On a new scrapi setup, you may have to alias the share index to the most current version:

```invoke alias share share_v2```

### Failing tests

There is a chance that your automatically created test will fail when run for the first time. If that's the case, you can create a new vcr file that will hopefully work.

- Delete the old vcr file inside ```scrapi/tests/vcr/shortname.py```
- Change the date within the "freeze time" decorator on line 14 to a date where you know the harvester had results. For example:

```@freeze_time("2014-03-15```

- Inside of ```scrapi/tests/test_harvesters.py``` change the 'record_mode' on line 22 to 'once.' It should now read:
    
```with vcr.use_cassette('tests/vcr/{}.yaml'.format(harvester_name), match_on=['host'], record_mode='once'):```

- Re-run the tests with ```invoke test```

# autooai

Automatically create an OAI harvester for the [SHARE Project](https://osf.io/wur56/wiki/home/).

In order to automatically generate a harvester, it's assumed you'll have an API endpoint that will return xml in standard OAI-PMH format.

Since this is specfically for the SHARE project, it's assumed that you'll be running this tool from a directory that is one directory up from your [scrapi](http://github.com/fabianvf/scrapi) (or SHARE core) directory.

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

From within the autooai directory...

Install requirements using [pip](https://pypi.python.org/pypi/pip) inside a [virtual enviornment](https://virtualenv.pypa.io/en/latest/) by running 

```pip install -r requirements.txt```

Once you've installed all the requirements, you're ready to get started generating OAI-PMH harvesters for SHARE!

----

Here's an example of how to use this tool to generate a SHARE OAI harvester for the MIT repository:

```
python main.py -b http://dspace.mit.edu/oai/request -s mit -f
```

This will do a few things:
- create a harvester called mit.py in the proper directory within scrapi
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


Example usage

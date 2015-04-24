# autooai

Automatically create an OAI harvester for the SHARE Project

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

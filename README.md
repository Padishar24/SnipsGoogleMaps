# Google Maps (Direction) Snips Skill

This is a skill for the voice assistent 'Snips'. It allows to qurey the
traffic information for your daily commute route (atm. only by car) and
to query the distance between two cities (atm. only by car aswell).

## Setup

This app requires some python dependencies to work properly, these are
listed in the `requirements.txt`. You can use the `setup.sh` script to
create a python virtualenv that will be recognized by the skill server
and install them in it.

The setup will query a few informations:

- key = The Google Maps Direction API key
- home = Your home address
- work = Your work address
- proxy = A proxy to use, leave empty if you don't have one.

## Google Maps Direction API key

Here is a rough description to obtain the required key. Please use
your favorite search engine to get more informations on this topic.

1. Select or create a GCP project. [link](https://console.cloud.google.com/apis/dashboard)
2. Make sure that billing is enabled for your project. [link](https://cloud.google.com/billing/docs/how-to/modify-project)
3. Enable the Google Maps Direction API. [link](https://console.cloud.google.com/apis/dashboard)
4. Retrieve the key

As long as you only query the API a few times a day, it's completly free to use. (State on 30.10.2019)

## Executables

This dir contains a number of python executables named `action-*.py`.
One such file is generated per intent supported. These are standalone
executables and will perform a connection to MQTT and register on the
given intent using the `hermes-python` helper lib.

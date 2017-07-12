# tellmefacts-dummybot

This bot emulates a tellmefacts-client supported bot, returning a random
unicode string response on each recieved request on its `/ask` endpoint.

Only the HTTP GET and HEAD requests are supported on this endpoint.

The server will mount itself on port 80 by default.

This can be used as follows:

```bash
curl http://localhost/ask?q=<question here>
```

The response body will be of type `application/json` and is JSON encoded.

## How it works

The bot's server is constructed using the [cherrypy](https://github.com/cherrypy/cherrypy) library. A random response controller is mounted at the `/ask` endpoint of
the server that handles HTTP GET requests.

When a request with the `q` parameter is made, a random response from the
available responses is returned in a JSON object.

Example response:
```json
    {
        "response": "Banging your head against a wall burns 150 calories an hour."
    }
```

## Launcher

A launcher script is provided as `run_dummybot.py` that can be used to
launch the server. Several command line options are built in as follows:

```
    usage: run_dummybot.py [-h] [--config-dir CONFIG_DIR]

    Launches the dummybot server.

    optional arguments:
    -h, --help            show this help message and exit
    --config-dir CONFIG_DIR
                            changes the config directory
```

## Configuration

The server reads a configuration file located in the server's `config` folder,
which sets the available responses. The config folder can be changed easily with
a command line flag using the launcher.

**responses.json** - a list of strings to be used as potential responses to a question.

```json
    [
        "Banging your head against a wall burns 150 calories an hour.",
        "In the UK, it is illegal to eat mince pies on Christmas Day.",
        "'Facebook Addiction Disorder' is a mental disorder identified by Psychologists.",
        "If you lift a kangaroo's tail off the ground it can't hop.",
        "Bananas are curved because they grow towards the sun.",
        "If Pinokio says 'My Nose Will Grow Now', it would cause a paradox.",
        "Heart attacks are more likely to happen on a Monday.",
        "In 2015, more people were killed from injuries caused by taking a selfie than by shark attacks."
    ]
```

## Running tests

Tests for the client are written in pytest and use pytest-cov features.
The easiest way to run tests is to open a shell at the app directory and run:

```bash
    # Linux
    python3 -m pytest tests

    # Windows
    py -3 -m pytest tests
```

Note: Tests are run with the pytest -s flag, which means output is not buffered
until the end of test. Failing tests will prompt for interaction as the cherrypy
[testing](http://docs.cherrypy.org/en/latest/advanced.html#testing-your-application)
framework was used to write the tests.
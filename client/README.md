# tellmefacts Slack Bot Client

The tellmefacts client was created to multiplex chat conversations between multiple
fact bots that use a supported API. Slack users are able to pick between
configured bots by issuing commands to the bot, and subsequently chat with a
connected bot. Essentially, the client acts as a relay client to connected bots.

The client must be mentioned via its bot user name as set in your Slack team, and
moved into the channel that it is intended to be used in.

An example of typical conversation would look like this:

```
   user: @tellmefacts list
   bot:  1. Interesting Facts
         2. Strange Facts
         3. Unusual Facts
   user: @tellmefacts start_session Strange Facts
   bot:  You are now chatting with Strange Facts.
   user: @tellmefacts Give me a fact.
   bot:  Strange Facts: #1 Banging your head against a wall burns 150 calories an hour.
   user: @tellmefacts end_session
   bot:  Chat session with Strange Facts ended.
```

## How it works

The Slack bot client was built with the python [ChatterBot](https://github.com/gunthercox/ChatterBot)chatbot framework for processing chat messages. Custom input, output, and logic
adapters were built to interact with chat messages from the Slack RTM API, using 
[python-slackclient](https://github.com/slackapi/python-slackclient).

The client reads the input from the Slack RTM stream and processes any text that's
associated with a bot mention. If this text is a recognised command, some change
is made to the client's state (connecting/disconnecting to a bot). If not, it is
interpreted as a question to a connected bot, and a request for a response is
made to the selected bot. The response is sent back to Slack via either RTM or
Web API.

These adapters are suitable for use in any other chatterbot project as they
inherit from the base chatterbot adapter classes.

## Client keyword commands

The client accepts the following commands:

**list**

Usage: `@tellmefacts list`

Lists the currently available bots the client can connect to as set in the
configuration.

**start_session**

Usage: `@tellmefacts start_session <bot_name>`

Start a session with one of the available bots on the list. Invalid names will
produce an error message. Cannot start another session if currently in a
session.

**end_session**

Usage: `@tellmefacts end_session`

Ends the current bot session. If not in an active session, an error is produced.

## Launcher

A launcher script is provided as `run_client.py` that can be used to
launch the application. Several command line options are built in as follows:

```
   This is the launcher for the multibot-client application.

    usage: run_client.py [-h] [--with-tests] [--only-tests]
                        [--config-dir CONFIG_DIR] [--api-hostname API_HOSTNAME]
                        [--terminal] [--verbose]

    Launches the slackbot client.

    optional arguments:
    -h, --help            show this help message and exit
    --config-dir CONFIG_DIR
                            changes the config directory
    --api-hostname API_HOSTNAME
                            sets a hostname other than slack.com
    --terminal            set bot to run in terminal mode
    --verbose             display all logging information on terminal
```

## Configuration

Configuration of Slack tokens and bot connections are done externally in a
config folder. By default this is located in the client's directory under the
folder `config`. This can be changed easily through a launcher switch.

The following config files are needed to run this client:

**bots.json** - configures bot urls and names.

```json
    [
        {
            "name": "Interesting Facts",
            "url": "http://dummybot_1"
        },
        {
            "name": "Strange Facts",
            "url": "http://dummybot_2"
        },
        {
            "name": "Unusual Facts",
            "url": "http://dummybot_3"
        }
    ]
```

**slack_api.json** - configures the client's bot tokens and bot name.

```json
    {
        "bot_name": "tellmefacts",
        "bot_user_token": "xoxp-1234123412341234-12341234-1234"
    }
```

## Running tests

Tests for the client are written in pytest and use pytest-cov and pytest-mock
features. The easiest way to run tests is to open a shell at the app directory
and run:

```bash
    # Linux
    python3 -m pytest tests

    # Windows
    py -3 -m pytest tests
```

The client integration tests contain three test cases that will be skipped by
default. These test cases make real requests to a bot server, and require
configuration. The config folder is located at `tests/integration_tests/config`
and should contain a `bots.json` file along with a `slack_api.json` file.

When the configuration is ready, start the tests with an additional `--dummybot`
flag. The servers will be sent HTTP HEAD requests to verify that they are actually 
online, before tests begin.

It is recommended to use the [dummybot](https://github.com/TheGuardianWolf/tellmefacts/tree/master/dummybot) server 
included in this project for these tests.

## Documentation

Documentation uses [Sphinx](http://www.sphinx-doc.org). This can be compiled
from the source code using:

```bash
    sphinx-build -b html docs/ build/
```

NOTE: The `sphinx` and `sphinx_rtd_theme` packages must be installed on the
machine building the docs.

## Report an issue

Please direct all bug reports and feature requests to the project's issue
tracker on [GitHub](https://github.com/TheGuardianWolf/tellmefacts/issues/).

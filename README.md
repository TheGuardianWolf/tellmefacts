# tellmefacts

This project contains two packages, *Client* and *Dummybot*, intended to be
used in the running of a multiplexing Slack bot client.

Each package is self contained and has its own documentation.

By default, the setup will produce three identical factbots, which will provide
random facts when a question is asked, hence the name @tellmefacts.

Visit the project folders here:

[Client](https://github.com/TheGuardianWolf/tellmefacts/tree/master/client)

[Dummybot](https://github.com/TheGuardianWolf/tellmefacts/tree/master/dummybot)

## Purpose

### Client

This is the client application that is required to run on the machine that is
hosting the bot. This is not a server application so no specialised network
configuration should be required.

The client can be configured to connect to multiple supported bots so that
Slack users are able to select one and chat with it.

### Dummybot

This is a dummy server used to test the application. It will give a random fact
as a response if its `/ask` endpoint is queried with a `q` parameter containing
any string.

## Setup Instructions

It is assumed that the `docker` and `docker-compose` commands are available on
the machine hosting the bot.

Each project directory contains its own `Dockerfile` for building containers.
The build for the container fetches a Python 3.6 image and installs the
required dependencies automatically. Code testing is performed automatically as
the last step of the build.

The project root contains two `docker-compose.yml` files that will be used for 
the setups below.

### Running the Client with Dummybots

This is the default setup of the `docker-compose.yml` config.

Before proceeding with the below, ensure the configuration instructions have
been followed from the client [README](https://github.com/TheGuardianWolf/tellmefacts/blob/master/client/README.md#configuration).

Then run the following command in a shell from the project root to get started:

```bash
docker-compose --scale dummybot=3
```

That's it!

### Full Integration Test

By default some integration test cases in the client are skipped during
container building (more details in the client README). To run them fully, the `docker-compose.test.yml` config is provided for testing.

Use the following command to start the tests:

```bash
docker-compose --file docker-compose.test.yml --scale dummybot=3
```

The dummybot services will need to be manually closed after testing with `CTRL-C`.

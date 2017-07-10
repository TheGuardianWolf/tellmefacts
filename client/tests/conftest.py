def pytest_addoption(parser):
    parser.addoption(
        '--dummybot',
        action='store_true',
        default=False,
        help='run dummybot integration tests')

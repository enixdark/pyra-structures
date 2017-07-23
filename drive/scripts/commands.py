from subparse import command

@command('.shell')
def shell(parser):
    """ Launch a python interpreter."""
    parser.add_argument(
        '-p', '--python-shell',
        default='',
        help='ipython | python',
    )

@command('.migratedb', 'db:migrate')
def migratedb(parser):
    """ Perform database migrations."""
    parser.add_argument('--rev', default='head')

@command('.serve', 'http:serve')
def serve(parser):
    """ Launch the web server."""
    parser.add_argument('--reload', action='store_true', default=False)

@command('.add_user')
def add_user(parser):
    """ Add a new user account to the system."""

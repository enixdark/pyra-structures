from pyramid.scripts import pserve

log = __import__('logging').getLogger(__name__)

def main(cli, args):
    opts = ['pserve', cli.config_file]
    pserve.main(opts)

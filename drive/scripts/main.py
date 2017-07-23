from getpass import getpass
import hupper
import logging
import logging.config
import os
import pkg_resources
from pyramid.decorator import reify
import sys
from subparse import CLI

from drive.utils.settings import load_settings_from_file
from .validation import ValidationError

CONFIG_ENVIRON_KEY = 'DRIVE_CONFIG'

class MyApp(object):
    stdout = sys.stdout
    stderr = sys.stderr

    def __init__(self, args):
        self.args = args
        self.config_file = args.config_file
        if (
            not os.path.exists(self.config_file) and
            getattr(args, 'require_config_file', True)
        ):
            self.abort('Invalid config file, does not exist.')

    def setup_logging(self):
        if self.args.quiet:
            root_logger = logging.getLogger('')
            root_logger.setLevel(logging.CRITICAL)
        else:
            path = self.config_file
            here = os.path.abspath(os.path.dirname(path))
            logging.config.fileConfig(path, defaults={'here': here})

    def out(self, msg):
        self.stdout.write(msg)
        if not msg.endswith('\n'):
            self.stdout.write('\n')

    def error(self, msg):
        self.stderr.write(msg)
        if not msg.endswith('\n'):
            self.stderr.write('\n')

    def abort(self, error, code=1):
        self.error(error)
        raise AbortCLI(error, code)

    @reify
    def settings(self):
        return load_settings_from_file(self.config_file)

    @reify
    def dbengine(self):
        from drive.model.meta.engine import get_engine
        return get_engine(
            self.settings,
            check_version=not self.args.ignore_schema,
        )

    @reify
    def dbmaker(self):
        from drive.model.meta.session import get_session_factory
        session_factory = get_session_factory(self.dbengine)
        return session_factory

    def prompt(self,
               prompt,
               validator=None,
               attempts=3,
               confirm=False,
               secure=False,
               default=None,
               ):
        if default is None:
            default = ''
        while attempts > 0:
            value = _get_input(prompt, secure=secure)
            if not value:
                value = default
            try:
                if validator is not None:
                    value = validator(value)
            except ValidationError as ex:
                self.error(ex.message)
            else:
                if confirm:
                    confirm_value = _get_input(confirm, secure=secure)
                    if not confirm_value:
                        confirm_value = default
                    if confirm_value == value:
                        return value
                    self.error('Values do not match.')
                else:
                    return value
            attempts -= 1
        self.abort('Too many attempts, aborting.')

def _get_input(prompt, secure=False):
    if secure:
        value = getpass(prompt)
    else:
        value = input(prompt)
    value = value.strip()
    return value

class AbortCLI(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code

def context_factory(cli, args):
    app = MyApp(args)
    if getattr(args, 'reload', False):
        reloader = hupper.start_reloader(__name__ + '.main')
        reloader.watch_files([app.config_file])
    app.setup_logging()
    return app

def generic_options(parser):
    default_config = os.environ.get(CONFIG_ENVIRON_KEY, 'site.ini')
    parser.add_argument(
        '-c', '--config-file',
        default=default_config,
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
    )
    parser.add_argument(
        '--ignore-schema', action='store_const', const=True,
        default=False,
    )

def main():
    cli = CLI(
        version=pkg_resources.get_distribution('drive').version,
        context_factory=context_factory,
    )
    cli.add_generic_options(generic_options)
    cli.load_commands('.commands')
    # cli.load_commands('journimap.mq.commands')
    # import ipdb;ipdb.set_trace()

    try:
        return cli.run()
    except AbortCLI as ex:
        return ex.code

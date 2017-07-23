from code import interact
import sys
import textwrap

log = __import__('logging').getLogger(__name__)

def make_default_shell(interact=interact):
    def shell(env, help):
        cprt = 'Type "help" for more information.'
        banner = 'Python %s on %s\n%s' % (sys.version, sys.platform, cprt)
        banner += '\n\n' + help + '\n'
        interact(banner, local=env)
    return shell

def make_ipython_shell(IPShellFactory=None):
    try:
        import IPython
        IPShellFactory = IPython.start_ipython
    except ImportError:
        return None

    def shell(env, help):
        from traitlets.config import Config
        c = Config()
        c.TerminalInteractiveShell.banner2 = help + '\n'
        IPShellFactory(argv=[], user_ns=env, config=c)
    return shell

def main(cli, args):
    import sqlalchemy
    import transaction
    from drive import model
    from drive.model.meta.session import get_tm_session

    tm = transaction.TransactionManager(explicit=True)
    dbmaker = cli.dbmaker

    env = {
        'cli': cli,
        'sa': sqlalchemy,
        'tm': tm,
        'model': model,
        'dbmaker': dbmaker,
        'db': get_tm_session(dbmaker, transaction_manager=tm),
    }

    help = textwrap.dedent(
        """
        Environment:
          model           drive.model    (import drive.model as model)
          sa              sqlalchemy         (import sqlalchemy as sa)
          cli             The CLI application.
          dbmaker         database session maker (unbound)
          db              database session (bound to tm)
          tm              transaction manager
        """).strip()

    shell = None
    user_shell = args.python_shell.lower()

    if not user_shell:
        shell = make_ipython_shell()
        if shell is None:
            shell = make_default_shell()

    elif user_shell == 'ipython':
        shell = make_ipython_shell()

    elif user_shell == 'python':
        shell = make_default_shell()

    if shell is None:
        log.warn('failed to find requested shell "%s", using default',
                 user_shell)
        shell = make_default_shell()

    with tm:
        shell(env, help)

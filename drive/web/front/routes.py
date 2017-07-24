log = __import__('logging').getLogger(__name__)

def includeme(config):
    config.include('drive.utils.static')

    # config.add_route('index', '/', static=True)
    config.add_route('home', '/', permission = True)

    # config.add_route('user', '/user')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('forgot.password', '/forgot_password')
    config.add_route('account', '/account')
    config.add_route('account.changepassword', '/change-password')
    config.add_route('account.profile', '/account')
    config.add_route('notification', '/notifications')

  
log = __import__('logging').getLogger(__name__)

def includeme(config):
    config.include('drive.utils.static')

    config.add_route('index', '/', static=True)
    config.add_route('home', '/')

    config.add_route('user', '/user')
    # config.add_route('logout', '/logout')
    # config.add_route('register', '/register')
    # config.add_route('organization', '/organization')
    # config.add_route('forgot.password', '/forgot_password')
    # # config.add_route('account', '/account')
    # config.add_route('account.changepassword', '/change-password')
    # config.add_route('account.profile', '/account')
    # config.add_route('account.organization', '/change-organization')
    # config.add_route('notification', '/notifications')

    # config.add_route('project', '/project/{action}*id')
    # config.add_route('active.project', '/active-project/{action}/{id}')
    # config.add_route('add.comment.empathy', '/add-comment-empathy')

    # config.add_route('terms-of-service', '/terms-of-service')
    # config.add_route('privacy-policy', '/privacy-policy')

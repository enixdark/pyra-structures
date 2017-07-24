from pyramid.httpexceptions import (
    HTTPSeeOther,
)
from pyramid.security import (
    remember,
    forget,
)
from pyramid.view import view_config

from drive import services as S
from drive.utils.came_from import (
    set_came_from,
    get_came_from,
    reset_came_from,
)

from drive.web.front.forms import (
    SignupForm,
    LoginForm,
    ForgotPasswordForm,
)

log = __import__('logging').getLogger(__name__)


@view_config(route_name='register',
             renderer='auth/register.jinja2')
def register_view(request):
    # import ipdb;ipdb.set_trace()not
    came_from = set_came_from(request, 'register', preferred_route='home')
    form = SignupForm(request.POST)

    if request.method == 'POST' and form.validate():

        svc = request.find_service(S.AccountService)
        user = svc.find_user_by_email(form.value('email'))

        if user is not None:
            request.session.status_code = 400
            form.add_error('email', 'Email address is already taken.')
            return {'form': form}

        user = svc.create_user(
            form.value('first_name'),
            form.value('last_name'),
            form.value('email')
        )
        svc.attach_account(user, form.value('password'))

        request.session.flash(
            f'Created a new account for {user.email}, you may now login.',
            'success',
        )

        if user is not None:
            svc = request.find_service(S.LoginService)
            token = svc.make_token_for_user(user)
            log.debug('user found=%s, token=%s', user.id, token)

            headers = remember(request, token)
            request.bind_session_to_user(user)

            # reset_came_from(request, 'organization')
            return HTTPSeeOther(came_from, headers=headers)

    return {'form': form}



@view_config(
    route_name='login',
    renderer='auth/login.jinja2',
)
def login_view(request):
    came_from = set_came_from(request, 'login', preferred_route='home')
    form = LoginForm(request.POST)

    if request.user is not None:
        # already logged in but kill came_from so that we don't get stuck in
        # a redirect loop when it sends us back here again
        reset_came_from(request, 'login')
        return HTTPSeeOther(came_from)

    email = ''
    if 'prepopulate_email' in request.session:
        email = request.session['prepopulate_email']
        del(request.session['prepopulate_email'])

    if request.method == 'POST' and form.validate():
        email = request.params['email']
        password = request.params['password']

        svc = request.find_service(S.LoginService)
        user = svc.find_user_from_credentials(email, password)

        if user is not None:
            token = svc.make_token_for_user(user)
            log.debug('user found=%s, token=%s', user.id, token)

            # allow a user-specific came_from in an anonymous session
            override_came_from = get_came_from(
                request, 'login.{}'.format(user.id), search=False)
            if override_came_from:
                came_from = override_came_from

            headers = remember(request, token)
            request.bind_session_to_user(user)

            return HTTPSeeOther(came_from, headers=headers)

        else:
            request.response.status_code = 400
            form.add_error('error', 'Email or password was incorrect. Please try again.')

    return {
        'email': email,
        'came_from': came_from,
        'form': form
    }


@view_config(route_name='forgot.password',
             renderer='auth/forgot_password.jinja2')
def forgot_password_view(request):
    # import ipdb; ipdb.set_trace()
    form = ForgotPasswordForm(request.POST)

    if request.method == 'POST' and form.validate():
        came_from = set_came_from(request, 'login', preferred_route='home')

        return HTTPSeeOther(came_from)

    return {'form': form}

@view_config(
    route_name='logout',
    request_method='GET',
    renderer='auth/logout.jinja2',
)
def get_logout_view(request):
    came_from = set_came_from(request, 'logout', preferred_route='home')
    if not request.user:
        return HTTPSeeOther(came_from)
    return {}


@view_config(
    route_name='logout',
    request_method='POST',
)
def logout_view(request):
    came_from = set_came_from(request, 'logout', preferred_route='home')
    headers = forget(request)
    request.session.invalidate()
    request.session.flash('You have been logged out. Come again!')
    return HTTPSeeOther(came_from, headers=headers)

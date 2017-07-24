from pyramid.view import view_config
import os
from pathlib import Path
from time import time
from pyramid.httpexceptions import (
    HTTPSeeOther,
)

from drive import services as S
from drive.web.front.forms import (
    ChangePasswordForm,
    UserForm,
)
from drive.utils.came_from import (
    set_came_from,
    get_came_from,
    reset_came_from,
)

from ....utils.auth import login_required

log = __import__('logging').getLogger(__name__)


@view_config(
    route_name='home',
    renderer='home.jinja2',
    # permission='auth'
)
@login_required
def home(request):
    return {}



@view_config(
    route_name='account.profile',
    renderer='account/profile.jinja2',
)
def profile_view(request):
    form = UserForm(request.POST)
    svc_account = request.find_service(S.AccountService)
    user = svc_account.find_user_by_id(request.user.id)
    notify = None
    file_name_avatar = str(user.id) + '.png'
    avatar_path = os.getcwd() + '/drive/web/static/avatar/' + file_name_avatar
    if Path(avatar_path).is_file():
        user.avatar = file_name_avatar
    else:
        user.avatar = 'default-avatar.png'

    if request.method == 'POST' and form.validate():
        first_name = request.params['first_name']
        last_name = request.params['last_name']
        email = request.params['email']
        avatar = request.params['file']

        # Update new avatar for user
        if avatar is not None and hasattr(avatar, 'filename'):
            try:
                open(avatar_path, 'wb').write(avatar.file.read())
                log.debug('Upload avatar successfully.')
            except:
                form.add_error('error', 'Have an error when upload avatar.')
                log.debug('Error when upload avatar.')

        # Check email is exist
        user_check = svc_account.find_user_by_email(email)
        if user_check is None:
            user = svc_account.update_profile(user.id, first_name, last_name, email)
            notify = 'Update profile successfully.'
            log.debug('Update profile successfully.')
        else:
            if user_check.id == user.id:
                user = svc_account.update_profile(user.id, first_name, last_name, email)
                notify = 'Update profile successfully.'
                log.debug('Update profile successfully.')
            else:
                log.debug('Email address is already taken.')
                form.add_error('error', 'Email address is already taken.')

    return {
        'time': str(time()),
        'user': user,
        'notify': notify,
        'form': form
    }

@view_config(
    route_name='account.changepassword',
    renderer='account/change_password.jinja2'
)
def change_password_view(request):
    form = ChangePasswordForm(request.POST)
    notify = ''

    if request.method == 'POST' and form.validate():
        old_password = request.params['old_password']
        new_password = request.params['new_password']
        confirm_password = request.params['confirm_password']
        if new_password != confirm_password:
            log.debug('Your password and confirmation password do not match.')
            form.add_error('error', 'Your password and confirmation password do not match.')
        else:
            email = request.user.email
            svc_login = request.find_service(S.LoginService)
            user = svc_login.find_user_from_credentials(email, old_password)
            if user is not None:
                # Update password for user
                svc_account = request.find_service(S.AccountService)
                svc_account.update_password(request.user, new_password)
                log.debug('Update password successfully.')
                notify = 'Update password successfully'
            else:
                log.debug('Old password is incorrect.')
                form.add_error('error', 'Old password is incorrect.')

    return {
        'notify': notify,
        'form': form
    }

# from pyramid.exceptions import BadCSRFToken
# from pyramid.httpexceptions import (
#     HTTPSeeOther,
# )
# from pyramid.view import forbidden_view_config
# from pyramid.view import notfound_view_config
# from pyramid.view import view_config

# from drive.utils.came_from import check_came_from
# from drive.utils.notfound import RemoveSlashNotFoundViewFactory
# from drive.utils.static import RemoveCacheBustTokenNotFoundViewFactory

# log = __import__('logging').getLogger(__name__)

# @view_config(
#     route_name='user',
#     renderer='users/index.jinja2',
# )
# def user_view(request):
#     return {}
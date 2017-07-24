from functools import wraps
from pyramid.httpexceptions import HTTPFound

# def login_required(view_callable):
#     def wrapper(context, request):
#         if request.unauthenticated_userid is None:
#             return HTTPFound(location=request.route_url("login"))
#         return view_callable(context, request)
#     return wrapper

# def decorator(view_callable):
#     @wraps(view_callable)
#     def inner(context, request):
#         return view_callable(context, request)
#     return inner

def login_required(func):    
    @wraps(func)
    def wrapper(request):
        if request.unauthenticated_userid is None:
            return HTTPFound(location=request.route_url("login"))
        return func(request)
        # return Response('not authirised')
    return wrapper
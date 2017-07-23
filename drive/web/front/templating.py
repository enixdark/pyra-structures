import datetime
from dateutil.parser import parse as parse_date
import jinja2
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from translationstring import TranslationString
import uuid

from drive.utils.i18n import DEFAULT_DOMAIN

log = __import__('logging').getLogger(__name__)

def includeme(config):
    config.include('pyramid_jinja2')

    config.add_jinja2_search_path('drive.web.front:templates')
    config.add_settings({
        'jinja2.i18n.domain': DEFAULT_DOMAIN,
        'jinja2.filters': {
            'tojson': tojson_filter,
            'required': required_filter,
            'todate': todate_filter,
            'len': len_filter
        },
        'jinja2.tests': {
            'true': true_test,
            'false': false_test,
        },
        'jinja2.globals': {
            'uuid4': uuid.uuid4,
        },
        'jinja2.finalize': translate_value,
    })

    config.add_subscriber(renderer_globals, 'pyramid.interfaces.IBeforeRender')


def renderer_globals(event):
    request = event['request']
    event['url'] = request.route_url
    event['csrf_token'] = request.session.get_csrf_token()
    # event['active_projects'] = active_projects(),
    # event['completed_projects'] = completed_projects()


@jinja2.contextfilter
def tojson_filter(context, value):
    request = context.get('request') or get_current_request()
    return jinja2.Markup(render('json', value, request=request))



def len_filter(value):
    return len([v for v in value if v is not None])

def todate_filter(value, fmt):
    if not isinstance(value, (datetime.date, datetime.datetime)):
        value = parse_date(value)
    return value.strftime(fmt)


def required_filter(value):
    if not value:
        raise RuntimeError('value is required')
    return value


def false_test(value):
    return value is False

def true_test(value):
    return value is True


@jinja2.contextfunction
def translate_value(ctx, value):
    if isinstance(value, TranslationString):
        request = ctx.get('request') or get_current_request()
        return request.localizer.translate(value)
    return value

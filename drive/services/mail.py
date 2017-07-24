from jinja2 import (
    Environment, PackageLoader, select_autoescape, StrictUndefined
)
from pyramid_mailer.exceptions import InvalidMessage
from pyramid_mailer.message import Message


class MailService:
    def __init__(self, settings, mailer):
        self.context = {}
        self.mailer = mailer
        self.jinja2_env = Environment(
            loader=PackageLoader('journimap.web.front', 'templates'),
            autoescape=select_autoescape(default=False),
            undefined=StrictUndefined,
        )

    def str(self, template_string, kw=None):
        if kw is None:
            kw = {}
        template = self.jinja2_env.from_string(template_string)
        return template.render(**self.context, **kw)

    def tmpl(self, path, kw=None):
        if kw is None:
            kw = {}
        template = self.jinja2_env.get_template(path)
        return template.render(**self.context, **kw)

    def send_mail(self, subject, recipients=None, body='', context=None, tmpl=''):
        self.context = context
        if body != '':
            body = self.str(template_string=body)

        if tmpl != '':
            tmpl = self.tmpl(path=tmpl)

        message = Message(subject=subject,
                          recipients=recipients,
                          body=body,
                          html=tmpl)
        try:
            self.mailer.send(message)
            return True
        except InvalidMessage as e:
            # print("Error: {0}".format(e))
            return False

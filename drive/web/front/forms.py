from marshmallow import (
    fields,
    pre_load,
    Schema,
    validate,
    validates,
    validates_schema,
    ValidationError,
)
import re
from drive.utils.email_address import EmailAddress
from drive.utils.i18n import _
from datetime import date
from drive.model.projects import ProjectVisibility

def IsText(field):
    def text_validator(value):
        if re.search(r'[\x00-\x1f\x7f-\x9f]', value):
            raise ValidationError(
                _(
                    'Invalid character(s) in ${field}.',
                    mapping={'field': field},
                )
            )
    return text_validator

def IsMultiLineText(field):
    def text_validator(value):
        if re.search(r'[\x00-\x09\x0b-\x0c\x0e-\x1f\x7f-\x9f]', value):
            raise ValidationError(
                _(
                    'Invalid character(s) in ${field}.',
                    mapping={'field': field},
                )
            )
    return text_validator

def IsIdentifier(field):
    def text_validator(value):
        if re.search(r'[^A-Za-z0-9_-]', value):
            raise ValidationError(
                _(
                    'Invalid character(s) in ${field}.',
                    mapping={'field': field},
                )
            )
    return text_validator


def my_required(value, field_name=''):
    if len(value) > 0:
        raise ValidationError(
            _(
                '${field} is required.',
                mapping={'field': field_name}
            )
        )


class Form(Schema):

    def __init__(self, data, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.data = data
        self.has_error = False
        self.errors = {}

    def validate(self):
        errors = super().validate(data=self.data)

        if bool(errors):
            self.has_error = True
            self.errors = errors
            return False

        return True

    def value(self, name):
        if self.data[name] is not None:
            return self.data[name]

    def add_error(self, name='', message=""):
        self.has_error = True

        if self.errors and self.errors[name] is not None:
            self.errors[name].append(message)
        else:
            self.errors[name] = [message]

        return self.errors

    def error_message(self):
        for key, val in self.errors.items():
            if len(val) > 0:
                return val[0]
            break
        return ''


class CreateUserForm(Form):

    first_name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=255)],
        error_messages={'required': 'user first name is required'},
    )

    last_name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=255)],
        error_messages={'required': 'user last name is required'},
    )

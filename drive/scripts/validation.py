from datetime import datetime

class ValidationError(ValueError):
    def __init__(self, message, invalid_value):
        super().__init__(message)
        self.message = message
        self.invalid_value = invalid_value

def validate_text(min=1, max=None, field='Value', next_validator=None):
    if min is not None and max is not None:
        assert 0 < min <= max
        if min == max:
            if min == 1:
                msg = f'{field} must be exactly {min} characters.'
            else:
                msg = f'{field} must be exactly 1 character.'
        else:
            msg = f'{field} must be between {min} and {max} characters.'
    elif min is not None:
        assert min > 0
        if min > 1:
            msg = f'{field} must be at least {min} characters.'
        else:
            msg = f'{field} must not be empty.'
    elif max is not None:
        assert max > 0
        if max == 1:
            msg = f'{field} must be at most 1 character.'
        else:
            msg = f'{field} cannot be longer than {max} characters.'
    def validator(value):
        if min is not None and len(value) < min:
            raise ValidationError(msg, value)
        if max is not None and len(value) > max:
            raise ValidationError(msg, value)

        if next_validator is not None:
            return next_validator(value)
        return value
    return validator

validate_email = validate_text(min=1, max=255, field='Email')
validate_password = validate_text(min=8, field='Password')

def validate_bool(value):
    value = value.lower()
    if value == 'y':
        return True
    if value == 'n':
        return False

    raise ValidationError('Please answer "y" or "n".', value)

def validate_choice(choices):
    choices_str = ', '.join(f'"{x}"' for x in sorted(choices))
    def validator(value):
        if value not in choices:
            raise ValidationError(f'Value must be one of {choices_str}', value)
        return value
    return validator

def validate_user(account_svc):
    def validator(value):
        user = account_svc.find_user_by_email(value)
        if user is None:
            raise ValidationError('Could not find user.', value)
        return user
    return validator

def validate_date(value):
    try:
        dt = datetime.strptime(value, '%Y-%m-%d')
    except Exception:
        raise ValidationError('Invalid date format, must be YYYY-MM-DD.')
    return dt.date()

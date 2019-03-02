from djangorestframework_camel_case.util import underscoreize as drf_cc_under


def underscoreize(*args, **kwargs):
    return drf_cc_under(*args, **kwargs)


def format_currency(pennies):
    return '${0:.2f}'.format(pennies / 100)

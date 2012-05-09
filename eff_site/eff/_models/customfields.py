# -*- coding: utf-8 *-*
from django.db import models


# Money-related constants
def MoneyField(**kwargs):
    """
    Returns a django.db.models.DecimalField properly configured for money
    values.

    You can set additional arguments to configure the field (any standard
    DecimalField argument works)
    """
    args = dict(max_digits=19, decimal_places=2)
    args.update(kwargs)
    return models.DecimalField(**args)


def HourField(**kwargs):
    """
    Returns a django.db.models.DecimalField properly configured for storing
    hours values.

    You can set additional arguments to configure the field (any standard
    DecimalField argument works)
    """
    args = dict(max_digits=19, decimal_places=3)
    args.update(kwargs)
    return models.DecimalField(**args)

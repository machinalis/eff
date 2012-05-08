# -*- coding: utf-8 *-*
from django.db import models


# Money-related constants
def MoneyField(**kwargs):
    """
    Returns a django.db.models.DecimalField properly configured for storing
    positive money values.

    You can set additional arguments to configure the field (any standard
    DecimalField argument works)

    If you want to store negative values too, set validators=[] in the kwargs
    """
    args = dict(max_digits=19, decimal_places=2)
    args.update(kwargs)
    return models.DecimalField(**args)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon basic classes for list handling
http://persimmon-project.org

Persimmon constants

"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"


__author__ = 'ibegtin'

TAGPATTERN_TYPE_LINEAR = 1      # Linear tag pattern
TAGPATTERN_TYPE_VERTICAL = 2    # Vertical tag pattern
TAGPATTERN_TYPE_COMPLEX = 3     # Complex tag pattern

BOOLEAN_RUSSIAN_YESNO = {
    'Да' : True,
    'Нет' : False
}

DEFAULT_BOOLEAN_MAP = {
    '1' : True,
    '0' : False
}

TAG_KEY_ALLATTR = "__all"       # Defines usage of all attributes for tag key generation

RULE_TYPE_COPY = 1           # Makes copy of the url
RULE_TYPE_REGEXP = 2         # Regular expression
RULE_TYPE_DELETE = 3         # Deletes specified item element
RULE_TYPE_MERGEFIELDS = 5    # merges to fields by pattern
RULE_TYPE_ABSURLS = 6        # Converts url to absolute

SCHEME_LIST_TABLE = 1		 # Table is simple list of records of objects
SCHEME_TABLE_KEYVALUE = 2	 # Two column table of name/value pairs mapped to object
SCHEME_DD_TABLE_KEYVALUE = 3 # DT/DD list as table of key/value
SCHEME_LIST_OBJECTS = 10     # List of objects mapped using Xpath or regexp
SCHEME_ITEM_OBJECT = 12      # Object mapped using Xpath or regexp
SCHEME_COMPLEX = 100         # Special type of scheme as mix of objects

PATH_TYPE_XPATH = 2         # Type of tag path

FIELD_TYPE_STRING = 1		# Represents simple string
FIELD_TYPE_ATTRIBUTE = 2    # Represents string as attribute of tag
FIELD_TYPE_UINT32 = 10		# Represents unsigned integer
FIELD_TYPE_DATE = 20          # Represents date field
FIELD_TYPE_DATETIME = 21      # Date and time field
FIELD_TYPE_TIME = 22          # Time field
FIELD_TYPE_BOOLEAN = 30       # Boolean field
FIELD_TYPE_CUSTOMGROUP = 40   # Custom group of values mapped to fields
FIELD_TYPE_URL = 50           # URL Field
FIELD_TYPE_REGEXPMAP = 60     # Regexp mapper field

PAGE_TYPE_RANGE = 1		# Fixed number of pages listed via xrange
PAGE_TYPE_PAGED = 2		# Pages listed by attribute with page number
PAGE_TYPE_COUNTED = 3		# Pages listed by attribute with number of items passed


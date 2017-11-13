#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon schemes 'News'
http://persimmon-project.org

Persimmon schemes. Basic 'news' schemes

"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "3.0.4"
__copyright__ = "Copyright (c) 2008 Ivan Begtin"
__license__ = "Proprietary"
from persimmon.web.consts import FIELD_TYPE_URL, FIELD_TYPE_STRING, SCHEME_LIST_TABLE
from persimmon.web.base import ElementPath
from persimmon.web.mapper import SourceScheme, MapperField, MapperScheme, MergeFieldsMapRule, RuleScheme

DUMA_FRAC_SCHEME = SourceScheme(attrs={
    'is_paged': False,
    'has_unique_url': False,
    'root_url': 'http://www.duma.gov.ru',
    'url': 'http://www.duma.gov.ru/structure/factions/',
    'encoding': 'utf8'
}, pagination=None,
                                lister={
                                    'data_area_path': ElementPath("//table[@id='lists_list_elements_36']",
                                                                  setKey='data_area'),
                                    'scheme': MapperScheme(schemeMap={
                                        0: MapperField('url', ['title', 'url'], FIELD_TYPE_URL, unique=True,
                                                       path=ElementPath('a')),
                                        1: MapperField('num', 'num', FIELD_TYPE_STRING),
                                        2: MapperField('website', [None, 'websiteUrl'], FIELD_TYPE_URL, unique=False,
                                                       path=ElementPath('a')),
                                    },
                                                           schemeType=SCHEME_LIST_TABLE,
                                                           schemePath=ElementPath('', startKey='data_area'),
                                                           rule_scheme=RuleScheme(rules=[
                                                               MergeFieldsMapRule(key='url', to='url',
                                                                                  pattern='{root_url}{url}',
                                                                                  area='source', fields=['root_url'])
                                                           ]),
                                                           row_shift=1
                                    )
                                },
)

DUMA_DEP_SCHEME = SourceScheme(attrs={
    'is_paged': True,
    'has_unique_url': False,
    'root_url': 'http://www.duma.gov.ru',
    'url': 'http://www.duma.gov.ru/structure/deputies/?letter=%D0%92%D1%81%D0%B5',
    'encoding': 'utf8'
}, pagination=None,
                                lister={
                                    'data_area_path': ElementPath("//table[@id='lists_list_elements_35']",
                                                                  setKey='data_area'),
                                    'scheme': MapperScheme(schemeMap={
                                        0: MapperField('url', ['title', 'url'], FIELD_TYPE_URL, unique=True,
                                                       path=ElementPath('a')),
                                        1: MapperField('name', 'name', FIELD_TYPE_STRING),
                                        2: MapperField('faction', ['factionName', 'factionUrl'], FIELD_TYPE_URL, unique=False,
                                                       path=ElementPath('a')),
                                    },
                                                           schemeType=SCHEME_LIST_TABLE,
                                                           schemePath=ElementPath('', startKey='data_area'),
                                                           rule_scheme=RuleScheme(rules=[
                                                               MergeFieldsMapRule(key='url', to='url',
                                                                                  pattern='{root_url}{url}',
                                                                                  area='source', fields=['root_url'])
                                                           ]),
                                                           row_shift=1
                                    )
                                },
)


def export_source(source_type, limit=500):
    import json
    import sys
    s = source_type
    items = s.getitems(limit=limit)
    json.dump(items, sys.stdout, indent=4)


if __name__ == '__main__':
    export_source(DUMA_FRAC_SCHEME, 10)
#    export_source(DUMA_DEP_SCHEME, 10)

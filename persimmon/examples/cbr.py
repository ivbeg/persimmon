#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon schemes 'News'
http://persimmon-project.org

Persimmon schemes. Basic 'news' schemes

"""


__author__ = "Ivan Begtin"
__version__ = "1.0.4"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"

from persimmon.web.consts import *
from persimmon.web.base import ElementPath
from persimmon.web.mapper import SourceScheme, MapperField, RegexpMapRule, RegexpMapField, DeleteFieldMapRule, MapperScheme, RuleScheme, MergeFieldsMapRule, DateMapperField, BooleanMapperField, AttributeMapperField, Pagination, DoublePagination


#class


CBR_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.cbr.ru',
    'url' : 'http://www.cbr.ru/credit/colist.asp?find=&x=26&y=1&how=name&reg=0&status=3',
    'url_item_prefix' : 'http://www.cbr.ru/credit/coinfo.asp?id=',
    'url_pattern' : 'http://www.cbr.ru/credit/coinfo.asp?id={id}',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
	'data_area_path' : ElementPath("//table[@class='CBRTBL info_table']", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
		    0 :  MapperField('num', 'num', FIELD_TYPE_STRING),
		    1 :  MapperField('comments', 'comments', FIELD_TYPE_STRING),
	    	2 :  MapperField('regnum', 'regnum', FIELD_TYPE_UINT32, unique=True),
		    3 :  MapperField('name', ['name', '__jsurl'], FIELD_TYPE_URL, unique=True, path=ElementPath('a')),
		    4 :  MapperField('address', 'address', FIELD_TYPE_STRING),
		},
		schemeType=SCHEME_LIST_TABLE,
		schemePath=ElementPath(None, startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    RegexpMapRule(key='__jsurl', to="uniquecode", regexp='^javascript:info\((?P<uniquecode>.*)\)$'),
                    MergeFieldsMapRule(key='uniquecode', to='url', pattern='{url_item_prefix}{uniquecode}', area='source', fields=['url_item_prefix']),
                    DeleteFieldMapRule(key='__jsurl')
                ])
	    ),
    },
    mapper = {
	'data_area_path' : ElementPath("//a[@href='javascript:history.back()']/parent::*", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
		    u'Регистрационный номер' :  MapperField('regnum', 'regnum', FIELD_TYPE_UINT32, unique=True),
		    u'Дата регистрации Банком России' :  DateMapperField('reg_date', 'reg_date', format='%d.%m.%Y'),
		    u'Основной государственный регистрационный номер' :  MapperField('basicregnum', 'basicregnum', FIELD_TYPE_CUSTOMGROUP, unique=True),
		    u'БИК' :  MapperField('bik', 'bik', FIELD_TYPE_STRING, unique=True),
		    u'Адрес из устава' :  MapperField('org_address', 'org_address', FIELD_TYPE_STRING),
		    u'Адрес фактический' :  MapperField('actual_address', 'actual_address', FIELD_TYPE_STRING),
		    u'Телефон' :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
		    u'Устав' :  MapperField('ustav', 'ustav', FIELD_TYPE_STRING),
		    u'Уставный капитал' :  MapperField('capital', 'capital', FIELD_TYPE_STRING),
		    u'Лицензия (дата выдачи/последней замены)' :  MapperField('license', 'license', FIELD_TYPE_STRING),
		    u'Участие в системе страхования вкладов' : BooleanMapperField('insurance_membership', 'insurance_membership', boolean_map=BOOLEAN_RUSSIAN_YESNO),
		    u'Фирменное наименование на английском языке' :  MapperField('engname', 'engname', FIELD_TYPE_STRING),
		},
		schemeType=SCHEME_TABLE_KEYVALUE,
		schemePath=ElementPath("//table[@class=' nodata']"),
#        sub_schemes={
#            None : MapperScheme(schemeMap={
#                0 :  MapperField('name', 'name', FIELD_TYPE_STRING, path=ElementPath("tbody/tr[position()=1]/td/strong")),
#                },
#                schemeType=SCHEME_ITEM_OBJECT,
#                schemePath=ElementPath('table/tbody/tr/td', startKey='item_area'), keepRaw=False)
#            }
	    )
    }
)


def export_source(source_type, limit=500):
		s = source_type
		items = s.getitems(limit=limit, useMapper=False)
		print(len(items))
		for item in items:
			print(item)
			for key, value in list(item.items()):
				if key != '__raw':
					try:
						print(key, '-', value.encode('cp866', 'ignore'))
					except:
						print(key, '-', value)

if __name__ == '__main__':
    export_source(CBR_SOURCE_SCHEME, 1000)

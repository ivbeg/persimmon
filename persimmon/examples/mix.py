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
	'data_area_path' : ElementPath("//td[text()='наименование']/parent::*/parent::*/parent::*", setKey='data_area'),
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
		    'Регистрационный номер' :  MapperField('regnum', 'regnum', FIELD_TYPE_UINT32, unique=True),
		    'Дата внесения в КГР' :  DateMapperField('reg_date', 'reg_date', format='%d.%m.%Y'),
		    'Основной государственный регистрационный номер' :  MapperField('basicregnum', 'basicregnum', FIELD_TYPE_CUSTOMGROUP, unique=True),
		    'БИК' :  MapperField('bik', 'bik', FIELD_TYPE_STRING, unique=True),
		    'Адрес из устава' :  MapperField('org_address', 'org_address', FIELD_TYPE_STRING),
		    'Адрес фактический' :  MapperField('actual_address', 'actual_address', FIELD_TYPE_STRING),
		    'Телефон' :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
		    'Устав' :  MapperField('ustav', 'ustav', FIELD_TYPE_STRING),
		    'Уставный капитал' :  MapperField('capital', 'capital', FIELD_TYPE_STRING),
		    'Лицензия (дата выдачи/последней замены)' :  MapperField('license', 'license', FIELD_TYPE_STRING),
		    'Участие в системе страхования вкладов' : BooleanMapperField('insurance_membership', 'insurance_membership', boolean_map=BOOLEAN_RUSSIAN_YESNO)
		},
		schemeType=SCHEME_TABLE_KEYVALUE,
		schemePath=ElementPath("//td[text()='Регистрационный номер']/parent::tr/parent::tbody/parent::table"),
        sub_schemes={
            None : MapperScheme(schemeMap={
                0 :  MapperField('name', 'name', FIELD_TYPE_STRING, path=ElementPath("tbody/tr[position()=1]/td/strong")),
                },
                schemeType=SCHEME_ITEM_OBJECT,
                schemePath=ElementPath('table/tbody/tr/td', startKey='item_area'), keepRaw=False)
            }
	    )
    }
)

ETC_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.gostrade.ru',
    'url' : 'http://www.gostrade.ru/public.purchase/default.asp',
    'base_url' : 'http://www.gostrade.ru/public.purchase/',
    'url_pattern' : 'http://www.gostrade.ru/public.purchase/notice.asp?contestid={id}&report=create',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//table[@class='htmltable_table']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('purchaseType', 'purchaseType', FIELD_TYPE_STRING, path=ElementPath('div/div/sup[position()=1]')),
            1 :  MapperField('url', ['url_text','url'], FIELD_TYPE_URL, path=ElementPath("div/div/sup/a[contains(@href, 'notice.asp')]")),
            2 :  MapperField('__name', '__name', FIELD_TYPE_STRING, path=ElementPath("div/h3")),
        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath('//h3/parent::*/parent::*', startKey='data_area', setKey="item_area"), keepRaw=False,
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{base_url}{url}', area='source', fields=['base_url']),
                    RegexpMapRule(key='__name', to=["pub_date", "uniquecode", 'name'], regexp='^(?P<pub_date>[0-9]{2}\.[0-9]{2}\.[1-2][0-9]{3}\W+[1-2][0-9]:[0-9]{2}:[0-9]{2})\W+(?P<uniquecode>[0-9]{5,10})\w+(?P<name>.*)$')
                ]),
        sub_schemes={
            'documents' : MapperScheme(schemeMap={
                0 :  MapperField('url', ['url_text','url'], FIELD_TYPE_URL, path=ElementPath("a[contains(@href, 'getfile.asp')]")),
                },
                schemeType=SCHEME_LIST_OBJECTS,
                schemePath=ElementPath('table/tbody/tr/td', startKey='item_area'), keepRaw=False,
                rule_scheme=RuleScheme(rules=[
                        MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url']),
                        ]),

            )
            }
            ),
    },
)

VOLOGDA_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.vologda-city.ru',
    'url' : 'http://www.vologda-city.ru/news',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//div[@id='region-content']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('pub_date', 'pub_date', format='%d.%m.%Y', path=ElementPath("div[@class='documentByLine']")),
            1 :  MapperField('title', ['title', 'url'], FIELD_TYPE_URL, path=ElementPath("h2[@class='tileHeadline']/a")),
            2 :  MapperField('body', 'body', FIELD_TYPE_STRING, path=ElementPath("p[@class='tileBody']")),
            3 :  AttributeMapperField('image', 'image', attrname='src', path=ElementPath("a/img[@class='tileImage']")),

        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath("//div[@class='tileItem visualIEFloatFix']", startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])
        ),
    },
)

BALASHIKHA_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.balashiha.ru',
    'url' : 'http://www.balashiha.ru/news.php',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//ul", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('pub_date', 'pub_date', format='%Y-%m-%d', path=ElementPath("b")),
            1 :  MapperField('title', ['title', 'url'], FIELD_TYPE_URL, path=ElementPath("a")),
            2 :  MapperField('body', 'body', FIELD_TYPE_STRING, path=None),

        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath("li", startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                ])
        ),
    },
)

ARBITR_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.arbitr.ru',
    'url' : 'http://www.arbitr.ru/news/',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//span[@class='newshl']/parent::*/parent::*", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('pub_date', 'pub_date', format='%d.%m.%Y', path=ElementPath("span[@class='newshl']")),
            1 :  MapperField('body', 'body', FIELD_TYPE_STRING, path=ElementPath("span[@class='newst']")),
            2 :  MapperField('url', [None, 'url'], FIELD_TYPE_URL, path=ElementPath("span[@class='newst']/a")),
            3 :  MapperField('url', [None, 'url'], FIELD_TYPE_URL, path=ElementPath("a")),

        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath("div", startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                ])
        ),
    },
)

KAZNA_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : True,
    'root_url' : 'http://www.roskazna.ru',
    'url' : 'http://www.roskazna.ru/news.html',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//h1/following-sibling::table", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('pub_date', 'pub_date', format="%d.%m'%Y", path=ElementPath("td[@class='vat black']")),
            1 :  MapperField('body', 'body', FIELD_TYPE_STRING, path=ElementPath("td[@class='vat']")),
            2 :  MapperField('url', [None, 'url'], FIELD_TYPE_URL, path=ElementPath("td[@class'vat']/a[@class='more']")),

        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath("tr", startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])
        ),
    },
)

SOVBEZ_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : True,
    'has_unique_url' : True,
    'root_url' : 'http://www.scrf.gov.ru',
    'url' : 'http://www.scrf.gov.ru/news/index{{page}}.html',
    'encoding' : 'windows-1251'
}, pagination=Pagination(page_type=PAGE_TYPE_PAGED, is_counted=True, page_len=20, start_empty=True, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@class='body_text_black']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('pub_date', 'pub_date', format='%d.%m.%Y', path=ElementPath("td[@class='subsubtitle']")),
            2 :  MapperField('url', ['title', 'url'], FIELD_TYPE_URL, path=ElementPath("td/div/a")),

        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath("tbody/tr[@align='left']", startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])
        ),
    },
)






VOLOGDA_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : True,
    'root_url' : 'http://www.vologda-city.ru',
    'url' : 'http://www.vologda-city.ru/zakaz/zakup/?&page={{page}}',
    },
    pagination = Pagination(page_type=PAGE_TYPE_PAGED, is_counted=True, page_len=20, start_empty=False, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@class='listing']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  DateMapperField('bidStartDate', 'bidStartDate', format='%d.%m.%Y'),
            1 :  DateMapperField('bidEndDate', 'bidEndDate', format='%d.%m.%Y %H:%M'),
            2 :  MapperField('purchaseType', 'purchaseType', FIELD_TYPE_STRING),
            3 :  MapperField('url', ['title', 'url'], FIELD_TYPE_URL, unique=True, path=ElementPath('a')),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])
        )
    },
)


SWIFT_SOURCE_SCHEME = SourceScheme(attrs={
	'is_paged' : True,
	'has_unique_url' : False,
	'root_url' : 'http://www.swift.ru',
	'url' : 'http://www.swift.ru/index.php?n=1&f=10&lett={{page}}',
    },
    pagination = Pagination(page_type=PAGE_TYPE_RANGE, pages=range(2,30), is_counted=False, page_len=None),
    lister = {
    'data_area_path' : ElementPath("//p[text()='BIC']/parent::*/parent::*/parent::*/parent::*/parent::*", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
		    0 :  MapperField('name', 'name', FIELD_TYPE_STRING, unique=True),
		    1 :  MapperField('bic', 'bic', FIELD_TYPE_STRING, unique=True),
	    	    2 :  MapperField('city', 'city', FIELD_TYPE_STRING),
		},
		schemeType=SCHEME_LIST_TABLE,
		schemePath=ElementPath('', startKey='data_area')
	    )
    },
)

BANKIRU_SOURCE_SCHEME = SourceScheme(attrs={
	'is_paged' : True,
	'has_unique_url' : False,
	'root_url' : 'http://www.banki.ru',
	'url' : 'http://www.banki.ru/banks/moscow/index.php?PAGEN_1={{page}}',
    'encoding' : 'windows-1251'
    }, pagination=Pagination(page_type=PAGE_TYPE_PAGED, is_counted=True, page_len=50),
    lister = {
	'data_area_path' : ElementPath("//table[@class='banksTbl']", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
		    0 :  MapperField('name', ['name', 'url'], FIELD_TYPE_URL, unique=True, path=ElementPath('a')),
		    1 :  MapperField('license', 'license', FIELD_TYPE_STRING, unique=True),
	    	2 :  MapperField('rating', 'rating', FIELD_TYPE_UINT32, path=ElementPath('a')),
	    	3 :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
	    	4 :  MapperField('site_url', ['site_url_name', 'site_url'], FIELD_TYPE_URL, path=ElementPath('a')),
		},
		schemeType=SCHEME_LIST_TABLE,
		limit=50,
		schemePath=ElementPath('', startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])
	    )
    },
)

MTT_ABC_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : False,
    'root_url' : 'http://www.mtt.ru',
    'url' : 'http://www.mtt.ru/info/codes/index.wbp?country=%d0%ee%f1%f1%e8%ff&countryCode=&city=&cityCode=&page={{page}}',
    'encoding' : 'windows-1251'
    },
#    pagination = Pagination(page_type=PAGE_TYPE_RANGE, pages=xrange(1,96), is_counted=False, page_len=None),
 pagination=Pagination(page_type=PAGE_TYPE_PAGED, is_counted=True, page_len=20, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@id='searchCodeResultsTable']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('country', 'country', FIELD_TYPE_STRING),
            1 :  MapperField('country_code', 'country_code', FIELD_TYPE_STRING),
            2 :  MapperField('city', 'city', FIELD_TYPE_STRING),
            3 :  MapperField('city_code', 'city_code', FIELD_TYPE_STRING),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area'),
        keepRaw=False,
        rule_scheme=RuleScheme(rules=[
                ]),
        row_shift=0
        )
    },
)

#
MTT_DEF_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : False,
    'has_unique_url' : False,
    'root_url' : 'http://www.mtt.ru',
    'url' : 'http://www.mtt.ru/info/def/index.wbp?def=&number=&region=&standard=&date=&operator=',
    'encoding' : 'windows-1251'
    }, pagination=None,
    lister = {
    'data_area_path' : ElementPath("//table[@id='searchCodeResultsTable']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('operator', 'operator', FIELD_TYPE_STRING),
            1 :  MapperField('region_name', 'region_name', FIELD_TYPE_STRING),
            2 :  MapperField('defcode', 'defcode', FIELD_TYPE_STRING),
            3 :  MapperField('range', 'range', FIELD_TYPE_STRING),
            4 :  MapperField('date', 'date', FIELD_TYPE_STRING),
#            4 :  DateMapperField('date', 'date', format='%d.%m.%Y'),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                ]),
        row_shift=0
        )
    },
)


LJBLOG_SOURCE_SCHEME = SourceScheme(attrs={
	'is_paged' : True,
	'has_unique_url' : False,
	'root_url' : 'http://ivbeg.livejournal.com',
	'url' : 'http://ivbeg.livejournal.com/?skip={{page}}',

    },
    pagination =Pagination(page_type=PAGE_TYPE_COUNTED, is_counted=True, page_len=20),
    lister  = {
	'data_area_path' : ElementPath("//div[@id='beta-inner']", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
#		    0 :  MapperField('name', 'name', FIELD_TYPE_URL, unique=True, path='a'),
#		    1 :  MapperField('license', 'license', FIELD_TYPE_STRING, unique=True),
#	    	    2 :  MapperField('rating', 'rating', FIELD_TYPE_UINT32, path='a'),
#	    	    3 :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
#	    	    4 :  MapperField('site_url', 'site_url', FIELD_TYPE_URL, path='a'),
		},
		schemeType=SCHEME_LIST_OBJECTS,
		limit=20,
		schemePath=ElementPath('//div[@class="entry"]', startKey='data_area')
	    )
    },
)

ERUS_SCHEME = {
    'attrs' : {
	'is_paged' : True,
	'has_unique_url' : True,
	'root_url' : 'http://www.erus.ru',
	'url' : 'http://www.erus.ru/public.faces/default.asp?bddtname=ware&bddtsetpage={{page}}',
	'pagination' : Pagination(page_type=PAGE_TYPE_PAGED, is_counted=True, page_len=40)
    },
    'lister' : {
	'data_area_path' : ElementPath("//td[@class='htmltable_data_cell']/parent::*/parent::*/parent::*", setKey='data_area'),
	'scheme' : MapperScheme(schemeMap={
		},
		schemeType=SCHEME_LIST_OBJECTS,
		limit=40,
		schemePath=ElementPath("//td[@class='htmltable_data_cell']", startKey='data_area')
	    )
    },
}

SMI_SOURCE_PAGES = ['a', 'b', 'c', 'd', 'e', 'f',
                    'g', 'h', 'i', 'j', 'k', 'l',
                    'm', 'n', 'o', 'p', 'q', 'r', 's',
                    't', 'u', 'v', 'w', 'x', 'y', 'z',
                    'RA', 'RB', 'RG', 'RD', 'RE', 'RYO',
                    'RZH', 'RZ', 'RI', 'RIY', 'RK', 'RL',
                    'RM', 'RN', 'RO', 'RP', 'RR', 'RS',
                    'RT', 'RU', 'RF', 'RH', 'RC', 'RCH',
                    'RSH', 'RSCH', 'RTZ', 'RY', 'RMZ',
                    'REE', 'RYU', 'RYA']
ESMI_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : False,
    'url' : 'http://www.fapmc.ru/popup/?smi_type=2&letter={{f_page}}&page={{page}}',
    'encoding' : 'windows-1251'
    },
    pagination = DoublePagination(f_page_type=PAGE_TYPE_RANGE, f_pages=SMI_SOURCE_PAGES, page_type=PAGE_TYPE_PAGED, is_counted=False, page_len=100, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@class='on']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('__iternum', '__iternum', FIELD_TYPE_STRING, unique=False),
            1 :  MapperField('name', 'name', FIELD_TYPE_STRING),
            2 :  MapperField('license', 'license', FIELD_TYPE_STRING, unique=True),
            3 :  MapperField('reg_date', 'reg_date', FIELD_TYPE_STRING),
#            3 :  DateMapperField('reg_date', 'reg_date', format='%d.%m.%Y'),
            4 :  MapperField('agency_name', 'agency_name', FIELD_TYPE_STRING),
            5 :  MapperField('form', 'form', FIELD_TYPE_STRING),
            6 :  MapperField('territory', 'territory', FIELD_TYPE_STRING),
            7 :  MapperField('topic', 'topic', FIELD_TYPE_STRING),
            8 :  MapperField('founders', 'founders', FIELD_TYPE_STRING),
            9 :  MapperField('postaddress', 'postaddress', FIELD_TYPE_STRING),
            10 :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
            11 :  MapperField('langs', 'langs', FIELD_TYPE_STRING),
            12 :  MapperField('period', 'period', FIELD_TYPE_STRING),
            13 :  MapperField('reregister', 'reregister', FIELD_TYPE_STRING),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area')
        )
    },
)

PSMI_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : False,
    'url' : 'http://www.fapmc.ru/popup/?smi_type=1&letter={{f_page}}&page={{page}}',
    'encoding' : 'windows-1251'
    },
    pagination = DoublePagination(f_page_type=PAGE_TYPE_RANGE, f_pages=SMI_SOURCE_PAGES, page_type=PAGE_TYPE_PAGED, is_counted=False, page_len=100, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@class='on']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('__iternum', '__iternum', FIELD_TYPE_STRING, unique=False),
            1 :  MapperField('name', 'name', FIELD_TYPE_STRING),
            2 :  MapperField('license', 'license', FIELD_TYPE_STRING, unique=True),
            3 :  MapperField('reg_date', 'reg_date', FIELD_TYPE_STRING),
#            3 :  DateMapperField('reg_date', 'reg_date', format='%d.%m.%Y'),
            4 :  MapperField('agency_name', 'agency_name', FIELD_TYPE_STRING),
            5 :  MapperField('form', 'form', FIELD_TYPE_STRING),
            6 :  MapperField('territory', 'territory', FIELD_TYPE_STRING),
            7 :  MapperField('topic', 'topic', FIELD_TYPE_STRING),
            8 :  MapperField('founders', 'founders', FIELD_TYPE_STRING),
            9 :  MapperField('postaddress', 'postaddress', FIELD_TYPE_STRING),
            10 :  MapperField('phone', 'phone', FIELD_TYPE_STRING),
            11 :  MapperField('langs', 'langs', FIELD_TYPE_STRING),
            12 :  MapperField('period', 'period', FIELD_TYPE_STRING),
            13 :  MapperField('reregister', 'reregister', FIELD_TYPE_STRING),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area')
        )
    },
)



NUMERIC_SOURCE_PAGES=['1', '2', '3', '4', '5', '6', '7', '8','9','0']

MOSCLASS_OKOGU_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : False,
    'root_url' : 'http://www.mosclassific.ru/mClass/',
    'url' : 'http://www.mosclassific.ru/mClass/okogu_view.php?filter=100&text={{f_page}}&zone=&type=&sort=KOD&direct=ASC&PAGEN_1={{page}}',
    'encoding' : 'windows-1251'
    },
    pagination = DoublePagination(f_page_type=PAGE_TYPE_RANGE, f_pages=NUMERIC_SOURCE_PAGES, page_type=PAGE_TYPE_PAGED, is_counted=False, page_len=100, num_shift=1),
    lister = {
    'data_area_path' : ElementPath("//table[@class='list']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('url', [None, 'url'], FIELD_TYPE_URL, unique=False, path=ElementPath('b/a')),
            1 :  MapperField('block', 'block', FIELD_TYPE_STRING, unique=False),
            2 :  MapperField('code', 'code', FIELD_TYPE_STRING, unique=True),
            3 :  MapperField('name', 'name', FIELD_TYPE_STRING, unique=True),
        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ])

        ),
    },
    mapper = {
    'data_area_path' : ElementPath("//table", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            'Сокращенное наименование' :  MapperField('sokr', 'sokr', FIELD_TYPE_STRING, unique=True),
            'Наименование' :  MapperField('name', 'name', FIELD_TYPE_STRING, unique=True),
            'Код позиции' :  MapperField('code', 'code', FIELD_TYPE_STRING, unique=True),
        },
        schemeType=SCHEME_TABLE_KEYVALUE,
        schemePath=ElementPath('//table', startKey='data_area'),
        )
    },
)

# Схема выгрузки сообществ из Livejournal
LJCOMM_SOURCE_SCHEME = SourceScheme(attrs={
    'is_paged' : True,
    'has_unique_url' : False,
    'root_url' : 'http://www.livejournal.ru',
    'url' : 'http://www.livejournal.ru/communities/{{page}}',
    },
    pagination = Pagination(page_type=PAGE_TYPE_RANGE, pages=range(1,268), is_counted=False, page_len=None),
    lister = {
    'data_area_path' : ElementPath("//ul[@id='comms']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('url', ['name', 'url'], FIELD_TYPE_URL, unique=False, path=ElementPath("span/a[@class='fn org url']")),
        },
        schemeType=SCHEME_LIST_OBJECTS,
        schemePath=ElementPath('li/dl/dd/ul/li', startKey='data_area'), keepRaw=False
        )
    },
)

RT_PHONE_SOURCE_SCHEME = SourceScheme(attrs={'is_paged' : False,
    'has_unique_url' : False,
    'root_url' : 'http://www.rt.ru',
    'url' : 'http://www.rt.ru/help-info/mh/',
    'encoding' : 'windows-1251'
}, pagination=None,  lister = {
    'data_area_path' : ElementPath("//table[@class='fmain_table']", setKey='data_area'),
    'scheme' : MapperScheme(schemeMap={
            0 :  MapperField('country_name',  'country_name', FIELD_TYPE_STRING),
            1 :  MapperField('code', 'code', FIELD_TYPE_STRING),
            2 :  MapperField('url', [None, 'url'], FIELD_TYPE_URL, path=ElementPath('a')),

        },
        schemeType=SCHEME_LIST_TABLE,
        schemePath=ElementPath('', startKey='data_area'),
        rule_scheme=RuleScheme(rules=[
                    MergeFieldsMapRule(key='url', to='url', pattern='{root_url}{url}', area='source', fields=['root_url'])
                ]),
        keepRaw=False,
        row_shift=1
        ),
    },
)

def __export_esmi():
    import sys
    s = ESMI_SOURCE_SCHEME
    items = s.getitems(limit=200, useMapper=True)
    f = open('results.csv', 'w')
    for item in items:
#        print item
        vals = [item['name'], item['license'], item['form']]
        f.write((';'.join(vals) + '\n').encode('utf8', 'ignore'))
        print(','.join(vals).encode('cp866', 'ignore'))

def __export_okogu():
    import sys
    s = MOSCLASS_OKOGU_SCHEME
    items = s.getitems(limit=500, useMapper=True)
    f = open('results.csv', 'w')
    for item in items:
#        print item.keys()
        vals = [item['code'], item['name'], item['sokr'] if item['sokr'] else ""]
        f.write((';'.join(vals) + '\n').encode('utf8', 'ignore'))
        print(','.join(vals).encode('cp866', 'ignore'))


def export_source(source_type, limit=500):
		s = source_type
		items = s.getitems(limit=limit)
		print(len(items))
		for item in items:
			print(item)
			for key, value in list(item.items()):
				if key != '__raw':
					try:
						print(key, '-', value.encode('cp866', 'ignore'))
					except:
						print(key, '-', value)

def __export_phone_abc():
    s = MTT_ABC_SOURCE_SCHEME
    items = s.getitems(limit=100000)
    print(len(items))
    f = open('abc.csv', 'w')
    for item in items:
        s = (';'.join(map(str, list(item.values())))).encode('utf8')
        f.write(s + '\n')
    f.close()

def __export_phone_world():
    s = RT_PHONE_SOURCE_SCHEME
    items = s.getitems(limit=10000)
    print(len(items))
    f = open('world_phone.csv', 'w')
    for item in items:
        s = (';'.join(map(str, list(item.values())))).encode('utf8')
        f.write(s + '\n')
    f.close()

if __name__ == '__main__':
#    __export_phone_world()
#    s = LJCOMM_SOURCE_SCHEME
#    items = s.getitems(500)
#    names = []
#    for item in items:
#        names.append(item['name'])
#    f = open('ljcomms.txt', 'w')
#    f.write(','.join(names))
#    f.close()
#    print len(names)
#        for key, value in item.items():
#            if key != '__raw':
#                print key, value
#    __export_okogu()
#    __export_esmi()
    export_source(CBR_SOURCE_SCHEME, 10)

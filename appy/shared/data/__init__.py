# -*- coding: utf-8 -*-
'''This folder contains copies of external, "authentic" data, stored as text
   files, like ISO 639.2 country codes. In this package, corresponding Python
   classes are available for accessing the data in the text files.'''

# ------------------------------------------------------------------------------
import os, os.path

# List of names of language in their own language ------------------------------
# It was copied from Plone 2.5.5 (PloneLanguageTool), don't know any "authentic
# source" for that.
nativeNames = {
  'aa' : 'магIарул мацI',
  'ab' : 'бызшәа',
  'af' : 'Afrikaans',
  'am' : 'አማርኛ',
  'ar' : 'العربية',
  'as' : 'অসমিয়া',
  'ay' : 'Aymara',
  'az' : 'Azəri Türkçəsi',
  'ba' : 'Bashkir',
  'be' : 'Беларускі',
  'bg' : 'Български',
  'bh' : 'Bihari',
  'bi' : 'Bislama',
  'bn' : 'বাংলা',
  'bo' : 'བོད་སྐད་',
  'bs' : 'Bosanski',
  'br' : 'Brezhoneg',
  'ca' : 'Català',
  'ch' : 'Chamoru',
  'co' : 'Corsu',
  'cs' : 'Čeština',
  'cy' : 'Cymraeg',
  'da' : 'Dansk',
  'de' : 'Deutsch',
  'dz' : 'རྫོང་ཁ',
  'el' : 'Ελληνικά',
  'en' : 'English',
  'eo' : 'Esperanto',
  'es' : 'Español',
  'et' : 'Eesti',
  'eu' : 'Euskara',
  'fa' : 'فارسی',
  'fi' : 'Suomi',
  'fj' : 'Fiji',
  'fo' : 'Føroyska',
  'fr' : 'Français',
  'fy' : 'Frysk',
  'ga' : 'Gaeilge',
  'gd' : 'Gàidhlig',
  'gl' : 'Galego',
  'gn' : 'Guarani',
  'gu' : 'ગુજરાતી',
  'gv' : 'Gaelg',
  'ha' : 'هَوُس',
  'he' : 'עברית',
  'hi' : 'हिंदी',
  'hr' : 'Hrvatski',
  'hu' : 'Magyar',
  'hy' : 'Հայերէն',
  'ia' : 'Interlingua',
  'id' : 'Bahasa Indonesia',
  'ie' : 'Interlingue',
  'ik' : 'Inupiak',
  'is' : 'Íslenska',
  'it' : 'Italiano',
  'iu' : 'ᐃᓄᒃᑎᑐᑦ',
  'ja' : '日本語',
  'jbo': 'lojban',
  'jw' : 'Basa Jawi',
  'ka' : 'ქართული',
  'kk' : 'ﻗﺎﺯﺍﻗﺸﺎ',
  'kl' : 'Greenlandic',
  'km' : 'ខ្មែរ',
  'kn' : 'ಕನ್ನಡ',
  'ko' : '한국어',
  'ks' : 'काऽशुर',
  'ku' : 'Kurdí',
  'kw' : 'Kernewek',
  'ky' : 'Кыргыз',
  'la' : 'Latin',
  'lb' : 'Lëtzebuergesch',
  'li' : 'Limburgs',
  'ln' : 'Lingala',
  'lo' : 'ພາສາລາວ',
  'lt' : 'Lietuviskai',
  'lv' : 'Latviešu',
  'mg' : 'Malagasy',
  'mi' : 'Maori',
  'mk' : 'Македонски',
  'ml' : 'മലയാളം',
  'mn' : 'Монгол',
  'mo' : 'Moldavian',
  'mr' : 'मराठी',
  'ms' : 'Bahasa Melayu',
  'mt' : 'Malti',
  'my' : 'Burmese',
  'na' : 'Nauru',
  'ne' : 'नेपाली',
  'nl' : 'Nederlands',
  'no' : 'Norsk',
  'nn' : 'Nynorsk',
  'oc' : 'Languedoc',
  'om' : 'Oromo',
  'or' : 'ଓଡ଼ିଆ',
  'pa' : 'ਪੰਜਾਬੀ',
  'pl' : 'Polski',
  'ps' : 'پښتو',
  'pt' : 'Português',
  'qu' : 'Quechua',
  'rm' : 'Rumantsch',
  'rn' : 'Kirundi',
  'ro' : 'Română',
  'ru' : 'Русский',
  'rw' : 'Kiyarwanda',
  'sa' : 'संस्कृत',
  'sd' : 'Sindhi',
  'se' : 'Northern Sámi',
  'sg' : 'Sangho',
  'sh' : 'Serbo-Croatian',
  'si' : 'Singhalese',
  'sk' : 'Slovenčina',
  'sl' : 'Slovenščina',
  'sm' : 'Samoan',
  'sn' : 'Shona',
  'so' : 'Somali',
  'sq' : 'Shqip',
  'sr' : 'српски',
  'ss' : 'Siswati',
  'st' : 'Sesotho',
  'su' : 'Sudanese',
  'sv' : 'Svenska',
  'sw' : 'Kiswahili',
  'ta' : 'தமிழ',
  'te' : 'తెలుగు',
  'tg' : 'Тоҷики',
  'th' : 'ไทย',
  'ti' : 'ትግርኛ',
  'tk' : 'түркmенче',
  'tl' : 'Tagalog',
  'tn' : 'Setswana',
  'to' : 'Lea faka-Tonga',
  'tr' : 'Türkçe',
  'ts' : 'Tsonga',
  'tt' : 'татарча',
  'tw' : 'Twi',
  'ug' : 'Uigur',
  'uk' : 'Українська',
  'ur' : 'اردو',
  'uz' : 'Ўзбекча',
  'vi' : 'Tiếng Việt',
  'vo' : 'Volapük',
  'wa' : 'Walon',
  'wo' : 'Wolof',
  'xh' : 'isiXhosa',
  'yi' : 'ײִדיש',
  'yo' : 'Yorùbá',
  'za' : 'Zhuang',
  'zh' : '中文',
  'zu' : 'isiZulu'
}
# List of languages having direction right-to-left (RTL) -----------------------
rtlLanguages = ('ar', 'he', 'fa')

# Countries of the "euro" zone
vatEuroCountries = ('AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'GR', 'ES',
                    'FI', 'FR', 'GB', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
                    'NL', 'PL' 'PT', 'RO', 'SE', 'SI', 'SK')

# ------------------------------------------------------------------------------
class Languages:
    '''This class gives access to the language codes and names as standardized
       by ISO-639. The file has been downloaded in July 2009 from
       http://www.loc.gov/standards/iso639-2/ascii_8bits.html (UTF-8 version)'''

    def __init__(self):
        self.fileName = os.path.dirname(__file__) + '/LanguageCodesIso639.2.txt'
        self.languageCodes = []
        # Names of languages in English
        self.languageNames = []
        # Names of languages in their language. It is not part of ISO 639.2 and
        # is taken from dict languageNames above.
        self.nativeNames = []
        self.parseFile()

    def parseFile(self):
        '''Parses the language codes and names in the ISO file and puts them in
           self.languageCodes, self.languageNames and self.nativeNames.'''
        f = file(self.fileName)
        for line in f:
            if line.strip():
                lineElems = line.split('|')
                if lineElems[2].strip():
                    # I take only those that have a 2-chars ISO-639-1 code.
                    self.languageCodes.append(lineElems[2])
                    self.languageNames.append(lineElems[3])
                    if lineElems[2] in nativeNames:
                        self.nativeNames.append(nativeNames[lineElems[2]])
                    else:
                        # Put the english name nevertheless.
                        self.nativeNames.append(lineElems[3])
        f.close()

    def exists(self, code):
        '''Is p_code a valid 2-digits language code?'''
        return code in self.languageCodes

    def get(self, code):
        '''Returns information about the language whose code is p_code.'''
        try:
            iCode = self.languageCodes.index(code)
            return self.languageCodes[iCode], self.languageNames[iCode], \
                   self.nativeNames[iCode]
        except ValueError:
            return None, None, None

    def __repr__(self):
        i = -1
        res = ''
        for languageCode in self.languageCodes:
            i += 1
            res += 'Language: ' + languageCode + ' - ' + self.languageNames[i]
            res += '\n'
        return res
# We instantiate here Languages because it is used by the appy.gen languages
# management.
languages = Languages()

# Country codes ISO 3166-1. ----------------------------------------------------
class Countries:
    '''This class gives access to the country codes and names as standardized by
       ISO 3166-1. The file has been downloaded in March 2011 from
       http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm
       (first line has been removed).'''

    def __init__(self):
        # This file has been downloaded from
        # http://www.iso.org/iso/country_codes.htm and converted to utf-8.
        self.fileName = os.path.dirname(__file__) + '/CountryCodesIso3166.1.txt'
        self.countryCodes = []
        # Names of countries in English
        self.countryNames = []
        self.parseFile()

    def parseFile(self):
        f = file(self.fileName)
        for line in f:
            if line.strip():
                name, code = line.split(';')
                self.countryCodes.append(code.strip())
                self.countryNames.append(name.strip())
        f.close()

    def exists(self, code):
        '''Is p_code a valid 2-digits country code?'''
        return code in self.countryCodes
# We instantiate here Countries because it is used by appy.gen for some field
# validations.
countries = Countries()

# ------------------------------------------------------------------------------
class BelgianCities:
    '''This class contains data about Belgian cities (postal codes). It creates
       a dictionary whose keys are postal codes and whose values are city names.
       The corresponding Excel file was downloaded on 2009-10-26 from
       https://www.post.be/site/fr/sse/advertising/addressed/biblio.html,
       converted to CSV (field separator being ";" field content is surrrounded
       by double quotes).'''

    def __init__(self):
        self.fileName = os.path.dirname(__file__) + '/BelgianCommunes.txt'
        self.data = {}
        self.parseFile()

    def parseFile(self):
        f = file(self.fileName)
        for line in f:
            if line.strip():
                lineElems = line.split(';')
                self.data[int(lineElems[0].strip('"'))]= lineElems[1].strip('"')

    def exists(self, postalCode):
        '''Is postalCode a valid Belgian postal code?'''
        return self.data.has_key(postalCode)
# ------------------------------------------------------------------------------

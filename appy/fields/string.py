# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# This file is part of Appy, a framework for building applications in the Python
# language. Copyright (C) 2007 Gaetan Delannay

# Appy is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.

# Appy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
import re, random
from appy.gen.layout import Table
from appy.gen.indexer import XhtmlTextExtractor
from appy.fields import Field
from appy.px import Px
from appy.shared.data import countries
from appy.shared.xml_parser import XhtmlCleaner
from appy.shared.diff import HtmlDiff
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
digit  = re.compile('[0-9]')
alpha  = re.compile('[a-zA-Z0-9]')
letter = re.compile('[a-zA-Z]')
digits = '0123456789'
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
# No "0" or "1" that could be interpreted as letters "O" or "l".
passwordDigits = '23456789'
# No letters i, l, o (nor lowercase nor uppercase) that could be misread.
passwordLetters = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ'
emptyTuple = ()

# ------------------------------------------------------------------------------
class Selection:
    '''Instances of this class may be given as validator of a String, in order
       to tell Appy that the validator is a selection that will be computed
       dynamically.'''
    def __init__(self, methodName):
        # The p_methodName parameter must be the name of a method that will be
        # called every time Appy will need to get the list of possible values
        # for the related field. It must correspond to an instance method of
        # the class defining the related field. This method accepts no argument
        # and must return a list (or tuple) of pairs (lists or tuples):
        # (id, text), where "id" is one of the possible values for the
        # field, and "text" is the value as will be shown on the screen.
        # You can use self.translate within this method to produce an
        # internationalized version of "text" if needed.
        self.methodName = methodName

    def getText(self, obj, value, field, language=None):
        '''Gets the text that corresponds to p_value.'''
        if language:
            withTranslations = language
        else:
            withTranslations = True
        vals = field.getPossibleValues(obj, ignoreMasterValues=True,\
                                       withTranslations=withTranslations)
        for v, text in vals:
            if v == value: return text
        return value

# ------------------------------------------------------------------------------
class String(Field):
    # Javascript files sometimes required by this type
    jsFiles = {'edit': ('ckeditor/ckeditor.js',),
               'view': ('ckeditor/ckeditor.js',)}

    # Some predefined regular expressions that may be used as validators
    c = re.compile
    EMAIL = c('[a-zA-Z][\w\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\w\.-]*[a-zA-Z0-9]\.' \
              '[a-zA-Z][a-zA-Z\.]*[a-zA-Z]')
    ALPHANUMERIC = c('[\w-]+')
    URL = c('(http|https):\/\/[a-z0-9]+([\-\.]{1}[a-z0-9]+)*(\.[a-z]{2,5})?' \
            '(([0-9]{1,5})?\/.*)?')

    # Possible values for "format"
    LINE = 0
    TEXT = 1
    XHTML = 2
    PASSWORD = 3
    CAPTCHA = 4

    # Default ways to render multingual fields
    defaultLanguagesLayouts = {
      LINE:  {'edit': 'vertical',   'view': 'vertical'},
      TEXT:  {'edit': 'horizontal', 'view': 'vertical'},
      XHTML: {'edit': 'horizontal', 'view': 'horizontal'},
    }

    # pxView part for formats String.LINE (but that are not selections) and
    # String.PASSWORD (a fake view for String.PASSWORD and no view at all for
    # String.CAPTCHA).
    pxViewLine = Px('''
     <span if="not value" class="smaller">-</span>
     <x if="value">
      <!-- A password -->
      <x if="fmt == 3">********</x>
      <!-- A URL -->
      <a if="(fmt != 3) and isUrl" target="_blank" href=":value">:value</a>
      <!-- Any other value -->
      <x if="(fmt != 3) and not isUrl">::value</x>
     </x>''')

    # pxView part for format String.TEXT.
    pxViewText = Px('''
     <span if="not value" class="smaller">-</span>
     <x if="value">::zobj.formatText(value, format='html')</x>''')

    # pxView part for format String.XHTML.
    pxViewRich = Px('''
     <div if="not mayAjaxEdit" class="xhtml">::value or '-'</div>
     <x if="mayAjaxEdit" var2="name=lg and ('%s_%s' % (name, lg)) or name">
      <div class="xhtml" contenteditable="true"
           id=":'%s_%s_ck' % (zobj.id, name)">::value or '-'</div>
      <script if="mayAjaxEdit">::field.getJsInlineInit(zobj, name, lg)</script>
     </x>''')

    # PX displaying the language code and name besides the part of the
    # multilingual field storing content in this language.
    pxLanguage = Px('''
     <td style=":'padding-top:%dpx' % lgTop" width="25px">
      <span class="language help"
            title=":ztool.getLanguageName(lg)">:lg.upper()</span>
     </td>''')

    pxMultilingual = Px('''
     <!-- Horizontally-layouted multilingual field -->
     <table if="mLayout == 'horizontal'" width="100%"
            var="count=len(languages)">
      <tr valign="top"><x for="lg in languages"><x>:field.pxLanguage</x>
       <td width=":'%d%%' % int(100.0/count)"
           var="requestValue=requestValue[lg]|None;
                value=value[lg]|emptyDefault">:field.subPx[layoutType][fmt]</td>
      </x></tr></table>

     <!-- Vertically-layouted multilingual field -->
     <table if="mLayout == 'vertical'">
      <tr valign="top" height="20px" for="lg in languages">
       <x>:field.pxLanguage</x>
       <td var="requestValue=requestValue[lg]|None;
                value=value[lg]|emptyDefault">:field.subPx[layoutType][fmt]</td>
     </tr></table>''')

    pxView = Px('''
     <x var="fmt=field.format; isUrl=field.isUrl;
             languages=field.getAttribute(zobj, 'languages');
             multilingual=len(languages) &gt; 1;
             mLayout=multilingual and field.getLanguagesLayout('view');
             mayAjaxEdit=not showChanges and field.inlineEdit and \
                         (layoutType != 'cell') and \
                         zobj.mayEdit(field.writePermission)">
      <x if="field.isSelect">
       <span if="not value" class="smaller">-</span>
       <x if="value and not isMultiple">::value</x>
       <ul if="value and isMultiple"><li for="sv in value"><i>::sv</i></li></ul>
      </x>
      <!-- Any other unilingual field -->
      <x if="not field.isSelect and not multilingual"
         var2="lg=None">:field.subPx['view'][fmt]</x>
      <!-- Any other multilingual field -->
      <x if="not field.isSelect and multilingual"
         var2="lgTop=1; emptyDefault='-'">:field.pxMultilingual</x>
      <!-- If this field is a master field -->
      <input type="hidden" if="masterCss" class=":masterCss" value=":rawValue"
             name=":name" id=":name"/></x>''')

    # pxEdit part for formats String.LINE (but that are not selections),
    # String.PASSWORD and String.CAPTCHA.
    pxEditLine = Px('''
     <input var="inputId=not lg and name or '%s_%s' % (name, lg);
                 placeholder=field.getAttribute(obj, 'placeholder') or ''"
            id=":inputId" name=":inputId" size=":field.width"
            maxlength=":field.maxChars" placeholder=":placeholder"
            value=":inRequest and requestValue or value"
            style=":'text-transform:%s' % field.transform"
            type=":(fmt == 3) and 'password' or 'text'"/>
     <!-- Display a captcha if required -->
     <span if="fmt == 4">:_('captcha_text', \
                            mapping=field.getCaptchaChallenge(req.SESSION))
     </span>''')

    # pxEdit part for formats String.TEXT and String.XHTML.
    pxEditTextArea = Px('''
     <textarea var="inputId=not lg and name or '%s_%s' % (name, lg)"
               id=":inputId" name=":inputId" cols=":field.width"
               style=":'text-transform:%s' % field.transform"
               rows=":field.height">:inRequest and requestValue or value
     </textarea>
     <script if="fmt == 2"
             type="text/javascript">::field.getJsInit(zobj, lg)</script>''')

    pxEdit = Px('''
     <x var="fmt=field.format;
             languages=field.getAttribute(zobj, 'languages');
             multilingual=len(languages) &gt; 1;
             mLayout=multilingual and field.getLanguagesLayout('edit')">
      <select if="field.isSelect"
              var2="possibleValues=field.getPossibleValues(zobj, \
                      withTranslations=True, withBlankValue=True)"
              name=":name" id=":name" class=":masterCss"
              multiple=":isMultiple and 'multiple' or ''"
              onchange=":field.getOnChange(zobj, layoutType)"
              size=":isMultiple and field.height or 1">
       <option for="val in possibleValues" value=":val[0]"
               selected=":field.isSelected(zobj, name, val[0], rawValue)"
               title=":val[1]">:ztool.truncateValue(val[1],field.width)</option>
      </select>
      <!-- Any other unilingual field -->
      <x if="not field.isSelect and not multilingual"
         var2="lg=None">:field.subPx['edit'][fmt]</x>
      <!-- Any other multilingual field -->
      <x if="not field.isSelect and multilingual"
         var2="lgTop=(fmt!=2) and 3 or 1;
               emptyDefault=''">:field.pxMultilingual</x>
      </x>''')

    pxCell = Px('''
     <x var="multipleValues=value and isMultiple">
      <x if="multipleValues">:', '.join(value)</x>
      <x if="not multipleValues">:field.pxView</x>
     </x>''')

    pxSearch = Px('''
     <!-- Show a simple search field for most String fields -->
     <input if="not field.isSelect" type="text" maxlength=":field.maxChars"
            size=":field.swidth" value=":field.sdefault"
            name=":'%s*string-%s' % (widgetName, field.transform)"
            style=":'text-transform:%s' % field.transform"/>
     <!-- Show a multi-selection box for fields whose validator defines a list
          of values, with a "AND/OR" checkbox. -->
     <x if="field.isSelect">
      <!-- The "and" / "or" radio buttons -->
      <x if="field.multiplicity[1] != 1"
         var2="operName='o_%s' % name;
              orName='%s_or' % operName;
              andName='%s_and' % operName">
       <input type="radio" name=":operName" id=":orName" checked="checked"
              value="or"/>
       <label lfor=":orName">:_('search_or')</label>
       <input type="radio" name=":operName" id=":andName" value="and"/>
       <label lfor=":andName">:_('search_and')</label><br/>
      </x>
      <!-- The list of values -->
      <select var="preSelected=field.sdefault"
              name=":widgetName" size=":field.sheight" multiple="multiple"
              onchange=":field.getOnChange(ztool, 'search', className)">
       <option for="v in field.getPossibleValues(ztool, withTranslations=True,\
                                     withBlankValue=False, className=className)"
               selected=":v[0] in preSelected" value=":v[0]"
               title=":v[1]">:ztool.truncateValue(v[1], field.swidth)</option>
      </select>
     </x><br/>''')

    # Sub-PX to use according to String format.
    subPx = {
     'edit': {LINE:pxEditLine, TEXT:pxEditTextArea, XHTML:pxEditTextArea,
              PASSWORD:pxEditLine, CAPTCHA:pxEditLine},
     'view': {LINE:pxViewLine, TEXT:pxViewText, XHTML:pxViewRich,
              PASSWORD:pxViewLine, CAPTCHA:pxViewLine}
    }
    subPx['cell'] = subPx['view']

    # Some predefined functions that may also be used as validators
    @staticmethod
    def _MODULO_97(obj, value, complement=False):
        '''p_value must be a string representing a number, like a bank account.
           this function checks that the 2 last digits are the result of
           computing the modulo 97 of the previous digits. Any non-digit
           character is ignored. If p_complement is True, it does compute the
           complement of modulo 97 instead of modulo 97. p_obj is not used;
           it will be given by the Appy validation machinery, so it must be
           specified as parameter. The function returns True if the check is
           successful.'''
        if not value: return True
        # First, remove any non-digit char
        v = ''
        for c in value:
            if digit.match(c): v += c
        # There must be at least 3 digits for performing the check
        if len(v) < 3: return False
        # Separate the real number from the check digits
        number = int(v[:-2])
        checkNumber = int(v[-2:])
        # Perform the check
        if complement:
            return (97 - (number % 97)) == checkNumber
        else:
            # The check number can't be 0. In this case, we force it to be 97.
            # This is the way Belgian bank account numbers work. I hope this
            # behaviour is general enough to be implemented here.
            mod97 = (number % 97)
            if mod97 == 0: return checkNumber == 97
            else:          return checkNumber == mod97
    @staticmethod
    def MODULO_97(obj, value): return String._MODULO_97(obj, value)
    @staticmethod
    def MODULO_97_COMPLEMENT(obj, value):
        return String._MODULO_97(obj, value, True)
    BELGIAN_ENTERPRISE_NUMBER = MODULO_97_COMPLEMENT

    @staticmethod
    def BELGIAN_NISS(obj, value):
        '''Returns True if the NISS in p_value is valid.'''
        if not value: return True
        # Remove any non-digit from nrn
        niss = sutils.keepDigits(value)
        # NISS must be made of 11 numbers
        if len(niss) != 11: return False
        # When NRN begins with 0 or 1, it must be prefixed with number "2" for
        # checking the modulo 97 complement.
        nissForModulo = niss
        if niss.startswith('0') or niss.startswith('1'):
            nissForModulo = '2'+niss
        # Check modulo 97 complement
        return String.MODULO_97_COMPLEMENT(None, nissForModulo)

    @staticmethod
    def IBAN(obj, value):
        '''Checks that p_value corresponds to a valid IBAN number. IBAN stands
           for International Bank Account Number (ISO 13616). If the number is
           valid, the method returns True.'''
        if not value: return True
        # First, remove any non-digit or non-letter char
        v = ''
        for c in value:
            if alpha.match(c): v += c
        # Maximum size is 34 chars
        if (len(v) < 8) or (len(v) > 34): return False
        # 2 first chars must be a valid country code
        if not countries.exists(v[:2].upper()): return False
        # 2 next chars are a control code whose value must be between 0 and 96.
        try:
            code = int(v[2:4])
            if (code < 0) or (code > 96): return False
        except ValueError:
            return False
        # Perform the checksum
        vv = v[4:] + v[:4] # Put the 4 first chars at the end.
        nv = ''
        for c in vv:
            # Convert each letter into a number (A=10, B=11, etc)
            # Ascii code for a is 65, so A=10 if we perform "minus 55"
            if letter.match(c): nv += str(ord(c.upper()) - 55)
            else: nv += c
        return int(nv) % 97 == 1

    @staticmethod
    def BIC(obj, value):
        '''Checks that p_value corresponds to a valid BIC number. BIC stands
           for Bank Identifier Code (ISO 9362). If the number is valid, the
           method returns True.'''
        if not value: return True
        # BIC number must be 8 or 11 chars
        if len(value) not in (8, 11): return False
        # 4 first chars, representing bank name, must be letters
        for c in value[:4]:
            if not letter.match(c): return False
        # 2 next chars must be a valid country code
        if not countries.exists(value[4:6].upper()): return False
        # Last chars represent some location within a country (a city, a
        # province...). They can only be letters or figures.
        for c in value[6:]:
            if not alpha.match(c): return False
        return True

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 format=LINE, show=True, page='main', group=None, layouts=None,
                 move=0, indexed=False, searchable=False,
                 specificReadPermission=False, specificWritePermission=False,
                 width=None, height=None, maxChars=None, colspan=1, master=None,
                 masterValue=None, focus=False, historized=False, mapping=None,
                 label=None, sdefault='', scolspan=1, swidth=None, sheight=None,
                 persist=True, transform='none', placeholder=None,
                 styles=('p','h1','h2','h3','h4'), allowImageUpload=True,
                 spellcheck=False, languages=('en',), languagesLayouts=None,
                 inlineEdit=False):
        # According to format, the widget will be different: input field,
        # textarea, inline editor... Note that there can be only one String
        # field of format CAPTCHA by page, because the captcha challenge is
        # stored in the session at some global key.
        self.format = format
        self.isUrl = validator == String.URL
        # When format is XHTML, the list of styles that the user will be able to
        # select in the styles dropdown is defined hereafter.
        self.styles = styles
        # When format is XHTML, do we allow the user to upload images in it ?
        self.allowImageUpload = allowImageUpload
        # When format is XHTML, do we run the CK spellchecker ?
        self.spellcheck = spellcheck
        # If "languages" holds more than one language, the field will be
        # multi-lingual and several widgets will allow to edit/visualize the
        # field content in all the supported languages. The field is also used
        # by the CK spell checker.
        self.languages = languages
        # When content exists in several languages, how to render them? Either
        # horizontally (one below the other), or vertically (one besides the
        # other). Specify here a dict whose keys are layouts ("edit", "view")
        # and whose values are either "horizontal" or "vertical".
        self.languagesLayouts = languagesLayouts
        # When format in XHTML, can the field be inline-edited (ckeditor)?
        self.inlineEdit = inlineEdit
        # The following field has a direct impact on the text entered by the
        # user. It applies a transformation on it, exactly as does the CSS
        # "text-transform" property. Allowed values are those allowed for the
        # CSS property: "none" (default), "uppercase", "capitalize" or
        # "lowercase".
        self.transform = transform
        # "placeholder", similar to the HTML attribute of the same name, allows
        # to specify a short hint that describes the expected value of the input
        # field. It is shown inside the input field and disappears as soon as
        # the user encodes something in it. Works only for strings whose format
        # is LINE. Does not work with IE < 10. You can specify a method here,
        # that can, for example, return an internationalized value.
        self.placeholder = placeholder
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, searchable,
                       specificReadPermission, specificWritePermission, width,
                       height, maxChars, colspan, master, masterValue, focus,
                       historized, mapping, label, sdefault, scolspan, swidth,
                       sheight, persist)
        self.isSelect = self.isSelection()
        # If self.isSelect, self.sdefault must be a list of value(s).
        if self.isSelect and not sdefault:
            self.sdefault = []
        # Default width, height and maxChars vary according to String format
        if width == None:
            if format == String.TEXT:  self.width  = 60
            # This width corresponds to the standard width of an Appy page.
            if format == String.XHTML: self.width  = None
            else:                      self.width  = 30
        if height == None:
            if format == String.TEXT: self.height = 5
            elif self.isSelect:       self.height = 4
            else:                     self.height = 1
        if maxChars == None:
            if self.isSelect: pass
            elif format == String.LINE: self.maxChars = 256
            elif format == String.TEXT: self.maxChars = 9999
            elif format == String.XHTML: self.maxChars = 99999
            elif format == String.PASSWORD: self.maxChars = 20
        self.filterable = self.indexed and (self.format == String.LINE) and \
                          not self.isSelect
        self.swidth = self.swidth or self.width
        self.sheight = self.sheight or self.height
        self.checkParameters()

    def checkParameters(self):
        '''Ensures this String is correctly defined.'''
        error = None
        if self.isMultilingual(None):
            if self.isSelect:
                error = "A selection field can't be multilingual."
            elif self.format in (String.PASSWORD, String.CAPTCHA):
                error = "A password or captcha field can't be multilingual."
        if error: raise Exception(error)

    def isSelection(self):
        '''Does the validator of this type definition define a list of values
           into which the user must select one or more values?'''
        res = True
        if type(self.validator) in (list, tuple):
            for elem in self.validator:
                if not isinstance(elem, basestring):
                    res = False
                    break
        else:
            if not isinstance(self.validator, Selection):
                res = False
        return res

    def isMultilingual(self, obj, dontKnow=False):
        '''Is this field multilingual ? If we don't know, say p_dontKnow.'''
        # In the following case, impossible to know: we say no.
        if not obj:
            if callable(self.languages): return dontKnow
            else: return len(self.languages) > 1
        return len(self.getAttribute(obj, 'languages')) > 1

    def getDefaultLayouts(self):
        '''Returns the default layouts for this type. Default layouts can vary
           acccording to format, multiplicity or history.'''
        if self.format == String.TEXT:
            return {'view': 'l-f', 'edit': 'lrv-d-f'}
        elif self.format == String.XHTML:
            if self.historized:
                # self.historized can be a method or a boolean. If it is a
                # method, it means that under some condition, historization will
                # be enabled. So we come here also in this case.
                view = 'lc-f'
            else:
                view = 'l-f'
            return {'view': Table(view, width='100%'), 'edit': 'lrv-d-f'}
        elif self.isMultiValued():
            return {'view': 'l-f', 'edit': 'lrv-f'}

    def getLanguagesLayout(self, layoutType):
        '''Gets the way to render a multilingual field on p_layoutType.'''
        if self.languagesLayouts and (layoutType in self.languagesLayouts):
            return self.languagesLayouts[layoutType]
        # Else, return a default value that depends of the format.
        return String.defaultLanguagesLayouts[self.format][layoutType]

    def getValue(self, obj):
        # Cheat if this field represents p_obj's state.
        if self.name == 'state': return obj.State()
        value = Field.getValue(self, obj)
        if not value:
            if self.isMultiValued(): return emptyTuple
            else: return value
        if isinstance(value, basestring) and self.isMultiValued():
            value = [value]
        elif isinstance(value, tuple):
            value = list(value)
        return value

    def getCopyValue(self, obj):
        '''If the value is mutable (ie, a dict for a multilingual field), return
           a copy of it instead of the value stored in the database.'''
        res = self.getValue(obj)
        if isinstance(res, dict): res = res.copy()
        return res

    def valueIsInRequest(self, obj, request, name):
        languages = self.getAttribute(obj, 'languages')
        if len(languages) == 1:
            return Field.valueIsInRequest(self, obj, request, name)
        # Is is sufficient to check that at least one of the language-specific
        # values is in the request.
        return request.has_key('%s_%s' % (name, languages[0]))

    def getRequestValue(self, obj, requestName=None):
        '''The request value may be multilingual.'''
        request = obj.REQUEST
        name = requestName or self.name
        languages = self.getAttribute(obj, 'languages')
        # A unilingual field.
        if len(languages) == 1: return request.get(name, None)
        # A multilingual field.
        res = {}
        for language in languages:
            res[language] = request.get('%s_%s' % (name, language), None)
        return res

    def isEmptyValue(self, obj, value):
        '''Returns True if the p_value must be considered as an empty value.'''
        if not self.isMultilingual(obj):
            return Field.isEmptyValue(self, obj, value)
        # For a multilingual value, as soon as a value is not empty for a given
        # language, the whole value is considered as not being empty.
        if not value: return True
        for v in value.itervalues():
            if not Field.isEmptyValue(self, obj, v): return
        return True

    def isCompleteValue(self, obj, value):
        '''Returns True if the p_value must be considered as complete. For a
           unilingual field, being complete simply means not being empty. For a
           multilingual field, being complete means that a value is present for
           every language.'''
        if not self.isMultilingual(obj):
            return Field.isCompleteValue(self, obj, value)
        # As soon as a given language value is empty, the global value is not
        # complete.
        if not value: return True
        for v in value.itervalues():
            if Field.isEmptyValue(self, obj, v): return
        return True

    def getDiffValue(self, obj, value, language):
        '''Returns a version of p_value that includes the cumulative diffs
           between successive versions. If the field is non-multilingual, it
           must be called with p_language being None. Else, p_language
           identifies the language-specific part we will work on.'''
        res = None
        lastEvent = None
        name = language and ('%s-%s' % (self.name, language)) or self.name
        for event in obj.workflow_history['appy']:
            if event['action'] != '_datachange_': continue
            if name not in event['changes']: continue
            if res == None:
                # We have found the first version of the field
                res = event['changes'][name][0] or ''
            else:
                # We need to produce the difference between current result and
                # this version.
                iMsg, dMsg = obj.getHistoryTexts(lastEvent)
                thisVersion = event['changes'][name][0] or ''
                comparator = HtmlDiff(res, thisVersion, iMsg, dMsg)
                res = comparator.get()
            lastEvent = event
        # Now we need to compare the result with the current version.
        iMsg, dMsg = obj.getHistoryTexts(lastEvent)
        comparator = HtmlDiff(res, value or '', iMsg, dMsg)
        return comparator.get()

    def getUnilingualFormattedValue(self, obj, value, showChanges=False,
                                    userLanguage=None, language=None):
        '''If no p_language is specified, this method is called by
           m_getFormattedValue for getting a non-multilingual value (ie, in
           most cases). Else, this method returns a formatted value for the
           p_language-specific part of a multilingual value.'''
        if Field.isEmptyValue(self, obj, value): return ''
        res = value
        if self.isSelect:
            if isinstance(self.validator, Selection):
                # Value(s) come from a dynamic vocabulary
                val = self.validator
                if self.isMultiValued():
                    return [val.getText(obj, v, self, language=userLanguage) \
                            for v in value]
                else:
                    return val.getText(obj, value, self, language=userLanguage)
            else:
                # Value(s) come from a fixed vocabulary whose texts are in
                # i18n files.
                _ = obj.translate
                if self.isMultiValued():
                    res = [_('%s_list_%s' % (self.labelId, v), \
                             language=userLanguage) for v in value]
                else:
                    res = _('%s_list_%s' % (self.labelId, value), \
                            language=userLanguage)
        elif (self.format == String.XHTML) and showChanges:
            # Compute the successive changes that occurred on p_value.
            res = self.getDiffValue(obj, res, language)
        # If value starts with a carriage return, add a space; else, it will
        # be ignored.
        if isinstance(res, basestring) and \
           (res.startswith('\n') or res.startswith('\r\n')): res = ' ' + res
        return res

    def getFormattedValue(self, obj, value, showChanges=False, language=None):
        '''Be careful: p_language represents the UI language, while "languages"
           below represents the content language(s) of this field. p_language
           can be used, ie, to translate a Selection value.'''
        languages = self.getAttribute(obj, 'languages')
        if len(languages) == 1:
            return self.getUnilingualFormattedValue(obj, value, showChanges,
                                                    userLanguage=language)
        # Return the dict of values whose individual, language-specific values
        # have been formatted via m_getUnilingualFormattedValue.
        if not value: return value
        res = {}
        for lg in languages:
            res[lg] = self.getUnilingualFormattedValue(obj, value[lg],
                                                       showChanges, language=lg)
        return res

    def getShownValue(self, obj, value, showChanges=False, language=None):
        '''Be careful: p_language represents the UI language, while "languages"
           below represents the content language(s) of this field. For a
           multilingual field, this method only shows one specific language
           part.'''
        languages = self.getAttribute(obj, 'languages')
        if len(languages) == 1:
            return self.getUnilingualFormattedValue(obj, value, showChanges,
                                                    userLanguage=language)
        if not value: return value
        # Try to propose the part that is in the user language, or the part of
        # the first content language else.
        lg = obj.getUserLanguage()
        if lg not in value: lg = languages[0]
        return self.getUnilingualFormattedValue(obj, value[lg], showChanges,
                                                language=lg)

    def extractText(self, value):
        '''Extracts pure text from XHTML p_value.'''
        return XhtmlTextExtractor(raiseOnError=False).parse('<p>%s</p>' % value)

    emptyStringTuple = ('',)
    emptyValuesCatalogIgnored = (None, '')

    def getIndexValue(self, obj, forSearch=False):
        '''Pure text must be extracted from rich content; multilingual content
           must be concatenated.'''
        isXhtml = self.format == String.XHTML
        if self.isMultilingual(obj):
            res = self.getValue(obj)
            if res:
                vals = []
                for v in res.itervalues():
                    if isinstance(v, unicode): v = v.encode('utf-8')
                    if isXhtml: vals.append(self.extractText(v))
                    else: vals.append(v)
                res = ' '.join(vals)
        else:
            res = Field.getIndexValue(self, obj, forSearch)
            if res and isXhtml: res = self.extractText(res)
        # Ugly catalog: if I give an empty tuple as index value, it keeps the
        # previous value. If I give him a tuple containing an empty string, it
        # is ok.
        if isinstance(res, tuple) and not res: res = self.emptyStringTuple
        # Ugly catalog: if value is an empty string or None, it keeps the
        # previous index value.
        if res in self.emptyValuesCatalogIgnored: res = ' '
        return res

    def getPossibleValues(self, obj, withTranslations=False,
                          withBlankValue=False, className=None,
                          ignoreMasterValues=False):
        '''Returns the list of possible values for this field (only for fields
           with self.isSelect=True). If p_withTranslations is True, instead of
           returning a list of string values, the result is a list of tuples
           (s_value, s_translation). Moreover, p_withTranslations can hold a
           given language: in this case, this language is used instead of the
           user language. If p_withBlankValue is True, a blank value is
           prepended to the list, excepted if the type is multivalued. If
           p_className is given, p_obj is the tool and, if we need an instance
           of p_className, we will need to use obj.executeQuery to find one.'''
        if not self.isSelect: raise Exception('This field is not a selection.')
        # Get the user language for translations, from "withTranslations".
        lg = isinstance(withTranslations, str) and withTranslations or None
        req = obj.REQUEST
        if ('masterValues' in req) and not ignoreMasterValues:
            # Get possible values from self.masterValue
            masterValues = req['masterValues']
            if '*' in masterValues: masterValues = masterValues.split('*')
            values = self.masterValue(obj.appy(), masterValues)
            if not withTranslations: res = values
            else:
                res = []
                for v in values:
                    res.append( (v, self.getFormattedValue(obj,v,language=lg)) )
        else:
            # If this field is an ajax-updatable slave, no need to compute
            # possible values: it will be overridden by method self.masterValue
            # by a subsequent ajax request (=the "if" statement above).
            if self.masterValue and callable(self.masterValue) and \
               not ignoreMasterValues: return []
            if isinstance(self.validator, Selection):
                # We need to call self.methodName for getting the (dynamic)
                # values. If methodName begins with _appy_, it is a special Appy
                # method: we will call it on the Mixin (=p_obj) directly. Else,
                # it is a user method: we will call it on the wrapper
                # (p_obj.appy()). Some args can be hidden into p_methodName,
                # separated with stars, like in this example: method1*arg1*arg2.
                # Only string params are supported.
                methodName = self.validator.methodName
                # Unwrap parameters if any.
                if methodName.find('*') != -1:
                    elems = methodName.split('*')
                    methodName = elems[0]
                    args = elems[1:]
                else:
                    args = ()
                # On what object must we call the method that will produce the
                # values?
                if methodName.startswith('tool:'):
                    obj = obj.getTool()
                    methodName = methodName[5:]
                else:
                    # We must call on p_obj. But if we have something in
                    # p_className, p_obj is the tool and not an instance of
                    # p_className as required. So find such an instance.
                    if className:
                        brains = obj.executeQuery(className, maxResults=1,
                                                  brainsOnly=True)
                        if brains:
                            obj = brains[0].getObject()
                # Do we need to call the method on the object or on the wrapper?
                if methodName.startswith('_appy_'):
                    exec 'res = obj.%s(*args)' % methodName
                else:
                    exec 'res = obj.appy().%s(*args)' % methodName
                if not withTranslations: res = [v[0] for v in res]
                elif isinstance(res, list): res = res[:]
            else:
                # The list of (static) values is directly given in
                # self.validator.
                res = []
                for value in self.validator:
                    label = '%s_list_%s' % (self.labelId, value)
                    if withTranslations:
                        res.append( (value, obj.translate(label, language=lg)) )
                    else:
                        res.append(value)
        if withBlankValue and not self.isMultiValued():
            # Create the blank value to insert at the beginning of the list
            if withTranslations:
                blankValue = ('', obj.translate('choose_a_value', language=lg))
            else:
                blankValue = ''
            # Insert the blank value in the result
            if isinstance(res, tuple):
                res = (blankValue,) + res
            else:
                res.insert(0, blankValue)
        return res

    def validateValue(self, obj, value):
        if self.format == String.CAPTCHA:
            challenge = obj.REQUEST.SESSION.get('captcha', None)
            # Compute the challenge minus the char to remove
            i = challenge['number']-1
            text = challenge['text'][:i] + challenge['text'][i+1:]
            if value != text:
                return obj.translate('bad_captcha')
        elif self.isSelect:
            # Check that the value is among possible values
            possibleValues = self.getPossibleValues(obj,ignoreMasterValues=True)
            if isinstance(value, basestring):
                error = value not in possibleValues
            else:
                error = False
                for v in value:
                    if v not in possibleValues:
                        error = True
                        break
            if error: return obj.translate('bad_select_value')

    def applyTransform(self, value):
        '''Applies a transform as required by self.transform on single
           value p_value.'''
        if self.transform in ('uppercase', 'lowercase'):
            # For those transforms, I will remove any accent, because, most of
            # the time, if the user wants to apply such effect, it is for ease
            # of data manipulation, so I guess without accent.
            value = sutils.normalizeString(value, usage='noAccents')
        # Apply the transform
        if   self.transform == 'lowercase':  return value.lower()
        elif self.transform == 'uppercase':  return value.upper()
        elif self.transform == 'capitalize': return value.capitalize()
        return value

    def getUnilingualStorableValue(self, obj, value):
        isString = isinstance(value, basestring)
        isEmpty = Field.isEmptyValue(self, obj, value)
        # Apply transform if required
        if isString and not isEmpty and (self.transform != 'none'):
           value = self.applyTransform(value)
        # Clean XHTML strings
        if not isEmpty and (self.format == String.XHTML):
            # When image upload is allowed, ckeditor inserts some "style" attrs
            # (ie for image size when images are resized). So in this case we
            # can't remove style-related information.
            try:
                value = XhtmlCleaner(keepStyles=False).clean(value)
            except XhtmlCleaner.Error, e:
                # Errors while parsing p_value can't prevent the user from
                # storing it.
                pass
        # Clean TEXT strings
        if not isEmpty and (self.format == String.TEXT):
            value = value.replace('\r', '')
        # Truncate the result if longer than self.maxChars
        if isString and self.maxChars and (len(value) > self.maxChars):
            value = value[:self.maxChars]
        # Get a multivalued value if required.
        if value and self.isMultiValued() and \
           (type(value) not in sutils.sequenceTypes):
            value = [value]
        return value

    def getStorableValue(self, obj, value):
        languages = self.getAttribute(obj, 'languages')
        if len(languages) == 1:
            return self.getUnilingualStorableValue(obj, value)
        # A multilingual value is stored as a dict whose keys are ISO 2-letters
        # language codes and whose values are strings storing content in the
        # language ~{s_language: s_content}~.
        if not value: return
        for lg in languages:
            value[lg] = self.getUnilingualStorableValue(obj, value[lg])
        return value

    def store(self, obj, value):
        '''Stores p_value on p_obj for this field.'''
        languages = self.getAttribute(obj, 'languages')
        if (len(languages) > 1) and value and \
           (not isinstance(value, dict) or (len(value) != len(languages))):
            raise Exception('Multilingual field "%s" accepts a dict whose '\
                            'keys are in field.languages and whose ' \
                            'values are strings.' % self.name)
        Field.store(self, obj, value)

    def storeFromAjax(self, obj):
        '''Stores the new field value from an Ajax request, or do nothing if
           the action was canceled.'''
        rq = obj.REQUEST
        if rq.get('cancel') == 'True': return
        requestValue = rq['fieldContent']
        # Remember previous value if the field is historized.
        previousData = obj.rememberPreviousData([self])
        if self.isMultilingual(obj):
            # We take a copy of previousData because it is mutable (dict).
            previousData[self.name] = previousData[self.name].copy()
            # We get a partial value, for one language only.
            language = rq['languageOnly']
            v = self.getUnilingualStorableValue(obj, requestValue)
            getattr(obj.aq_base, self.name)[language] = v
            part = ' (%s)' % language
        else:
            self.store(obj, self.getStorableValue(obj, requestValue))
            part = ''
        # Update the object history when relevant
        if previousData: obj.historizeData(previousData)
        # Update obj's last modification date
        from DateTime import DateTime
        obj.modified = DateTime()
        obj.reindex()
        obj.log('Ajax-edited %s%s on %s.' % (self.name, part, obj.id))

    def getIndexType(self):
        '''Index type varies depending on String parameters.'''
        # If String.isSelect, be it multivalued or not, we define a ListIndex:
        # this way we can use AND/OR operator.
        if self.isSelect:
            return 'ListIndex'
        elif self.format == String.TEXT:
            return 'TextIndex'
        elif self.format == String.XHTML:
            return 'XhtmlIndex'
        return Field.getIndexType(self)

    def getJs(self, layoutType, res):
        if self.format == String.XHTML: Field.getJs(self, layoutType, res)

    def getCaptchaChallenge(self, session):
        '''Returns a Captcha challenge in the form of a dict. At key "text",
           value is a string that the user will be required to re-type, but
           without 1 character whose position is at key "number". The challenge
           is stored in the p_session, for the server-side subsequent check.'''
        length = random.randint(5, 9) # The length of the challenge to encode
        number = random.randint(1, length) # The position of the char to remove
        text = '' # The challenge the user needs to type (minus one char)
        for i in range(length):
            j = random.randint(0, 1)
            chars = (j == 0) and passwordDigits or passwordLetters
            # Choose a char
            text += chars[random.randint(0,len(chars)-1)]
        res = {'text': text, 'number': number}
        session['captcha'] = res
        return res

    def generatePassword(self):
        '''Generates a password (we recycle here the captcha challenge
           generator).'''
        return self.getCaptchaChallenge({})['text']

    ckLanguages = {'en': 'en_US', 'pt': 'pt_BR', 'da': 'da_DK', 'nl': 'nl_NL',
                   'fi': 'fi_FI', 'fr': 'fr_FR', 'de': 'de_DE', 'el': 'el_GR',
                   'it': 'it_IT', 'nb': 'nb_NO', 'pt': 'pt_PT', 'es': 'es_ES',
                   'sv': 'sv_SE'}
    def getCkLanguage(self, obj, language):
        '''Gets the language for CK editor SCAYT. p_language is one of
           self.languages if the field is multilingual, None else. If p_language
           is not supported by CK, we use english.'''
        if not language:
            language = self.getAttribute(obj, 'languages')[0]
        if language in self.ckLanguages: return self.ckLanguages[language]
        return 'en_US'

    def getCkParams(self, obj, language):
        '''Gets the base params to set on a rich text field.'''
        ckAttrs = {'toolbar': 'Appy',
                   'format_tags': ';'.join(self.styles),
                   'scayt_sLang': self.getCkLanguage(obj, language)}
        if self.width: ckAttrs['width'] = self.width
        if self.spellcheck: ckAttrs['scayt_autoStartup'] = True
        if self.allowImageUpload:
            ckAttrs['filebrowserUploadUrl'] = '%s/upload' % obj.absolute_url()
        ck = []
        for k, v in ckAttrs.iteritems():
            if isinstance(v, int): sv = str(v)
            if isinstance(v, bool): sv = str(v).lower()
            else: sv = '"%s"' % v
            ck.append('%s: %s' % (k, sv))
        return ', '.join(ck)

    def getJsInit(self, obj, language):
        '''Gets the Javascript init code for displaying a rich editor for this
           field (rich field only). If the field is multilingual, we must init
           the rich text editor for a given p_language (among self.languages).
           Else, p_languages is None.'''
        name = not language and self.name or ('%s_%s' % (self.name, language))
        return 'CKEDITOR.replace("%s", {%s})' % \
               (name, self.getCkParams(obj, language))

    def getJsInlineInit(self, obj, name, language):
        '''Gets the Javascript init code for enabling inline edition of this
           field (rich text only). If the field is multilingual, the current
           p_language is given and p_name includes it. Else, p_language is
           None.'''
        uid = obj.id
        fieldName = language and name.rsplit('_',1)[0] or name
        lg = language or ''
        return "CKEDITOR.disableAutoInline = true;\n" \
               "CKEDITOR.inline('%s_%s_ck', {%s, on: {blur: " \
               "function( event ) { var content = event.editor.getData(); " \
               "doInlineSave('%s','%s','%s',content,'%s')}}})" % \
               (uid, name, self.getCkParams(obj, language), uid, fieldName,
                obj.absolute_url(), lg)

    def isSelected(self, obj, fieldName, vocabValue, dbValue):
        '''When displaying a selection box (only for fields with a validator
           being a list), must the _vocabValue appear as selected? p_fieldName
           is given and used instead of field.name because it may be a a fake
           name containing a row number from a field within a list field.'''
        rq = obj.REQUEST
        # Get the value we must compare (from request or from database)
        if rq.has_key(fieldName):
            compValue = rq.get(fieldName)
        else:
            compValue = dbValue
        # Compare the value
        if type(compValue) in sutils.sequenceTypes:
            return vocabValue in compValue
        return vocabValue == compValue
# ------------------------------------------------------------------------------

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

    def getText(self, obj, value, appyType):
        '''Gets the text that corresponds to p_value.'''
        for v, text in appyType.getPossibleValues(obj, ignoreMasterValues=True,\
                                                  withTranslations=True):
            if v == value:
                return text
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

    pxView = Px('''
     <x var="fmt=field.format; isUrl=field.isUrl;
             mayAjaxEdit=not showChanges and field.inlineEdit and \
                         zobj.mayEdit(field.writePermission)">
      <x if="fmt in (0, 3)">
       <ul if="value and isMultiple">
        <li for="sv in value"><i>::sv</i></li>
       </ul>
       <x if="value and not isMultiple">
        <!-- A password -->
        <x if="fmt == 3">********</x>
        <!-- A URL -->
        <a if="(fmt != 3) and isUrl" target="_blank" href=":value">:value</a>
        <!-- Any other value -->
        <x if="(fmt != 3) and not isUrl">::value</x>
       </x>
      </x>
      <!-- Unformatted text -->
      <x if="value and (fmt == 1)">::zobj.formatText(value, format='html')</x>
      <!-- XHTML text -->
      <x if="fmt == 2">
       <div if="not mayAjaxEdit" class="xhtml">::value or '-'</div>
       <div if="mayAjaxEdit" class="xhtml" contenteditable="true"
            id=":'%s_%s_ck' % (zobj.id, name)">::value or '-'</div>
       <script if="mayAjaxEdit">::field.getJsInlineInit(zobj)</script>
      </x>
      <span if="not value and (fmt != 2)" class="smaller">-</span>
      <input type="hidden" if="masterCss" class=":masterCss" value=":rawValue"
             name=":name" id=":name"/>
     </x>''')

    pxEdit = Px('''
     <x var="fmt=field.format;
             isOneLine=fmt in (0,3,4)">
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
      <x if="isOneLine and not field.isSelect"
         var2="placeholder=field.getAttribute(obj, 'placeholder') or ''">
       <input id=":name" name=":name" size=":field.width"
              maxlength=":field.maxChars" placeholder=":placeholder"
              value=":inRequest and requestValue or value"
              style=":'text-transform:%s' % field.transform"
              type=":(fmt == 3) and 'password' or 'text'"/>
       <!-- Display a captcha if required -->
       <span if="fmt == 4">:_('captcha_text', \
                              mapping=field.getCaptchaChallenge(req.SESSION))
       </span>
      </x>
      <x if="fmt in (1,2)">
       <textarea id=":name" name=":name" cols=":field.width"
                 class=":(fmt == 2) and ('rich_%s' % name) or ''"
                 style=":'text-transform:%s' % field.transform"
                 rows=":field.height">:inRequest and requestValue or value
       </textarea>
       <script if="fmt == 2"
               type="text/javascript">::field.getJsInit(zobj)</script>
      </x>
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

    # Possible values for "format"
    LINE = 0
    TEXT = 1
    XHTML = 2
    PASSWORD = 3
    CAPTCHA = 4
    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 format=LINE, show=True, page='main', group=None, layouts=None,
                 move=0, indexed=False, searchable=False,
                 specificReadPermission=False, specificWritePermission=False,
                 width=None, height=None, maxChars=None, colspan=1, master=None,
                 masterValue=None, focus=False, historized=False, mapping=None,
                 label=None, sdefault='', scolspan=1, swidth=None, sheight=None,
                 persist=True, transform='none', placeholder=None,
                 styles=('p','h1','h2','h3','h4'), allowImageUpload=True,
                 spellcheck=False, contentLanguage=None, inlineEdit=False):
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
        # What is the language of field content?
        self.contentLanguage = contentLanguage
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

    def getValue(self, obj):
        # Cheat if this field represents p_obj's state
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

    def store(self, obj, value):
        '''When the value is XHTML, we perform some cleanup.'''
        if not self.persist: return
        if (self.format == String.XHTML) and value:
            # When image upload is allowed, ckeditor inserts some "style" attrs
            # (ie for image size when images are resized). So in this case we
            # can't remove style-related information.
            try:
                value = XhtmlCleaner(keepStyles=False).clean(value)
            except XhtmlCleaner.Error, e:
                # Errors while parsing p_value can't prevent the user from
                # storing it.
                obj.log('Unparsable XHTML content in field "%s".' % self.name,
                        type='warning')
        Field.store(self, obj, value)

    def storeFromAjax(self, obj):
        '''Stores the new field value from an Ajax request, or do nothing if
           the action was canceled.'''
        rq = obj.REQUEST
        if rq.get('cancel') != 'True': self.store(obj, rq['fieldContent'])

    def getDiffValue(self, obj, value):
        '''Returns a version of p_value that includes the cumulative diffs
           between  successive versions.'''
        res = None
        lastEvent = None
        for event in obj.workflow_history.values()[0]:
            if event['action'] != '_datachange_': continue
            if self.name not in event['changes']: continue
            if res == None:
                # We have found the first version of the field
                res = event['changes'][self.name][0] or ''
            else:
                # We need to produce the difference between current result and
                # this version.
                iMsg, dMsg = obj.getHistoryTexts(lastEvent)
                thisVersion = event['changes'][self.name][0] or ''
                comparator = HtmlDiff(res, thisVersion, iMsg, dMsg)
                res = comparator.get()
            lastEvent = event
        # Now we need to compare the result with the current version.
        iMsg, dMsg = obj.getHistoryTexts(lastEvent)
        comparator = HtmlDiff(res, value or '', iMsg, dMsg)
        return comparator.get()

    def getFormattedValue(self, obj, value, showChanges=False):
        if self.isEmptyValue(value): return ''
        res = value
        if self.isSelect:
            if isinstance(self.validator, Selection):
                # Value(s) come from a dynamic vocabulary
                val = self.validator
                if self.isMultiValued():
                    return [val.getText(obj, v, self) for v in value]
                else:
                    return val.getText(obj, value, self)
            else:
                # Value(s) come from a fixed vocabulary whose texts are in
                # i18n files.
                t = obj.translate
                if self.isMultiValued():
                    res = [t('%s_list_%s' % (self.labelId, v)) for v in value]
                else:
                    res = t('%s_list_%s' % (self.labelId, value))
        elif (self.format == String.XHTML) and showChanges:
            # Compute the successive changes that occurred on p_value.
            res = self.getDiffValue(obj, res)
        # If value starts with a carriage return, add a space; else, it will
        # be ignored.
        if isinstance(res, basestring) and \
           (res.startswith('\n') or res.startswith('\r\n')): res = ' ' + res
        return res

    emptyStringTuple = ('',)
    emptyValuesCatalogIgnored = (None, '')
    def getIndexValue(self, obj, forSearch=False):
        '''For indexing purposes, we return only strings, not unicodes.'''
        res = Field.getIndexValue(self, obj, forSearch)
        if isinstance(res, unicode):
            res = res.encode('utf-8')
        if res and forSearch and (self.format == String.XHTML):
            # Convert the value to simple text.
            extractor = XhtmlTextExtractor(raiseOnError=False)
            res = extractor.parse('<p>%s</p>' % res)
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
           (s_value, s_translation). If p_withBlankValue is True, a blank value
           is prepended to the list, excepted if the type is multivalued. If
           p_className is given, p_obj is the tool and, if we need an instance
           of p_className, we will need to use obj.executeQuery to find one.'''
        if not self.isSelect: raise Exception('This field is not a selection.')
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
                    res.append( (v, self.getFormattedValue(obj, v)) )
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
                        res.append( (value, obj.translate(label)) )
                    else:
                        res.append(value)
        if withBlankValue and not self.isMultiValued():
            # Create the blank value to insert at the beginning of the list
            if withTranslations:
                blankValue = ('', obj.translate('choose_a_value'))
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

    def getStorableValue(self, value):
        isString = isinstance(value, basestring)
        # Apply transform if required
        if isString and not self.isEmptyValue(value) and \
           (self.transform != 'none'):
           value = self.applyTransform(value)
        # Truncate the result if longer than self.maxChars
        if isString and self.maxChars and (len(value) > self.maxChars):
            value = value[:self.maxChars]
        # Get a multivalued value if required.
        if value and self.isMultiValued() and \
           (type(value) not in sutils.sequenceTypes):
            value = [value]
        return value

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
    def getCkLanguage(self):
        '''Gets the language for CK editor SCAYT. We will use
           self.contentLanguage. If it is not supported by CK, we use
           english.'''
        lang = self.contentLanguage
        if lang and (lang in self.ckLanguages): return self.ckLanguages[lang]
        return 'en_US'

    def getCkParams(self, obj):
        '''Gets the base params to set on a rich text field.'''
        ckAttrs = {'toolbar': 'Appy',
                   'format_tags': ';'.join(self.styles),
                   'scayt_sLang': self.getCkLanguage()}
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

    def getJsInit(self, obj):
        '''Gets the Javascript init code for displaying a rich editor for this
           field (rich field only).'''
        return 'CKEDITOR.replace("%s", {%s})' % \
               (self.name, self.getCkParams(obj))

    def getJsInlineInit(self, obj):
        '''Gets the Javascript init code for enabling inline edition of this
           field (rich text only).'''
        uid = obj.id
        return "CKEDITOR.disableAutoInline = true;\n" \
               "CKEDITOR.inline('%s_%s_ck', {%s, on: {blur: " \
               "function( event ) { var content = event.editor.getData(); " \
               "doInlineSave('%s', '%s', '%s', content)}}})" % \
               (uid, self.name, self.getCkParams(obj), uid, self.name,
                obj.absolute_url())

        return "CKEDITOR.disableAutoInline = true;\n" \
               "CKEDITOR.inline('%s_%s_ck', {on: {blur: " \
               "function( event ) { var data = event.editor.getData(); " \
               "askAjaxChunk('%s_%s','POST','%s','%s:pxSave', " \
               "{'fieldContent': encodeURIComponent(data)}, " \
               "null, evalInnerScripts);}}});"% \
               (uid, self.name, uid, self.name, obj.absolute_url(), self.name)

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

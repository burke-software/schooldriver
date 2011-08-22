# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Appy is a framework for building applications in the Python language.
# Copyright (C) 2007 Gaetan Delannay

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,USA.

# ------------------------------------------------------------------------------
import xml.sax, difflib, types
from xml.sax.handler import ContentHandler, ErrorHandler, feature_external_ges,\
                            property_interning_dict
from xml.sax.xmlreader import InputSource
from appy.shared import UnicodeBuffer, xmlPrologue
from appy.shared.errors import AppyError

# Constants --------------------------------------------------------------------
CONVERSION_ERROR = '"%s" value "%s" could not be converted by the XML ' \
                   'unmarshaller.'
CUSTOM_CONVERSION_ERROR = 'Custom converter for "%s" values produced an ' \
                          'error while converting value "%s". %s'
XML_ENTITIES = {'lt': '<', 'gt': '>', 'amp': '&', 'quot': "'", 'apos': "'"}
HTML_ENTITIES = {
        'iexcl': '¡',  'cent': '¢', 'pound': '£', 'curren': '€', 'yen': '¥',
        'brvbar': 'Š', 'sect': '§', 'uml': '¨', 'copy':'©', 'ordf':'ª',
        'laquo':'«', 'not':'¬', 'shy':'­', 'reg':'®', 'macr':'¯', 'deg':'°',
        'plusmn':'±', 'sup2':'²', 'sup3':'³', 'acute':'Ž',
        'micro':'µ', 'para':'¶', 'middot':'·', 'cedil':'ž', 'sup1':'¹',
        'ordm':'º', 'raquo':'»', 'frac14':'Œ', 'frac12':'œ', 'frac34':'Ÿ',
        'iquest':'¿', 'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â', 'Atilde':'Ã',
        'Auml':'Ä', 'Aring':'Å', 'AElig':'Æ', 'Ccedil':'Ç', 'Egrave':'È',
        'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë', 'Igrave':'Ì', 'Iacute':'Í',
        'Icirc':'Î', 'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ', 'Ograve':'Ò',
        'Oacute':'Ó', 'Ocirc':'Ó', 'Otilde':'Õ', 'Ouml':'Ö', 'times':'×',
        'Oslash':'Ø', 'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û', 'Uuml':'Ü',
        'Yacute':'Ý', 'THORN':'Þ', 'szlig':'ß', 'agrave':'à', 'aacute':'á',
        'acirc':'â', 'atilde':'ã', 'auml':'ä', 'aring':'å', 'aelig':'æ',
        'ccedil':'ç', 'egrave':'è', 'eacute':'é', 'ecirc':'ê', 'euml':'ë',
        'igrave':'ì', 'iacute':'í', 'icirc':'î', 'iuml':'ï', 'eth':'ð',
        'ntilde':'ñ', 'ograve':'ò', 'oacute':'ó', 'ocirc':'ô', 'otilde':'õ',
        'ouml':'ö', 'divide':'÷', 'oslash':'ø', 'ugrave':'ù', 'uacute':'ú',
        'ucirc':'û', 'uuml':'ü', 'yacute':'ý', 'thorn':'þ', 'yuml':'ÿ',
        'euro':'€', 'nbsp':' ', "rsquo":"'", "lsquo":"'", "ldquo":"'",
        "rdquo":"'", 'ndash': ' ', 'oelig':'oe', 'quot': "'", 'mu': 'µ'}
import htmlentitydefs
for k, v in htmlentitydefs.entitydefs.iteritems():
    if not HTML_ENTITIES.has_key(k) and not XML_ENTITIES.has_key(k):
        HTML_ENTITIES[k] = ''

# ------------------------------------------------------------------------------
class XmlElement:
    '''Represents an XML tag.'''
    def __init__(self, elem, attrs=None, nsUri=None):
        '''An XmlElement instance may represent:
           - an already parsed tag (in this case, p_elem may be prefixed with a
             namespace);
           - the definition of an XML element (in this case, no namespace can be
             found in p_elem; but a namespace URI may be defined in p_nsUri).'''
        self.elem = elem
        self.attrs = attrs
        if elem.find(':') != -1:
            self.ns, self.name = elem.split(':')
        else:
            self.ns = ''
            self.name = elem
            self.nsUri = nsUri
    def equalsTo(self, other, namespaces=None):
        '''Does p_elem == p_other? If a p_namespaces dict is given, p_other must
           define a nsUri.'''
        res = None
        if namespaces:
            res = self.elem == ('%s:%s' % (namespaces[other.nsUri], other.name))
        else:
            res = self.elem == other.elem
        return res
    def __repr__(self):
        res = self.elem
        if self.attrs:
            res += '('
            for attrName, attrValue in self.attrs.items():
                res += '%s="%s"' % (attrName, attrValue)
            res += ')'
        return res
    def getFullName(self, namespaces=None):
        '''Gets the name of the element including the namespace prefix.'''
        if not namespaces:
            res = self.elem
        else:
            res = '%s:%s' % (namespaces[self.nsUri], self.name)
        return res

class XmlEnvironment:
    '''An XML environment remembers a series of elements during a SAX parsing.
       This class is an abstract class that gathers basic things like
       namespaces.'''
    def __init__(self):
        # This dict contains the xml namespace declarations encountered so far
        self.namespaces = {} # ~{s_namespaceUri:s_namespaceName}~
        self.currentElem = None # The currently parsed element
        self.parser = None
    def manageNamespaces(self, attrs):
        '''Manages namespaces definitions encountered in p_attrs.'''
        for attrName, attrValue in attrs.items():
            if attrName.startswith('xmlns:'):
                self.namespaces[attrValue] = attrName[6:]
    def ns(self, nsUri):
        '''Returns the namespace corresponding to o_nsUri.'''
        return self.namespaces[nsUri]

class XmlParser(ContentHandler, ErrorHandler):
    '''Basic expat-based XML parser that does things like :
      - remembering the currently parsed element;
      - managing namespace declarations.
      This parser also knows about HTML entities.'''
    def __init__(self, env=None, caller=None):
        '''p_env should be an instance of a class that inherits from
           XmlEnvironment: it specifies the environment to use for this SAX
           parser.'''
        ContentHandler.__init__(self)
        if not env: env = XmlEnvironment()
        self.env = env
        self.env.parser = self
        self.caller = caller # The class calling this parser
        self.parser = xml.sax.make_parser() # Fast, standard expat parser
        self.res = None # The result of parsing.

    # ContentHandler methods ---------------------------------------------------
    def startDocument(self):
        self.parser._parser.UseForeignDTD(True)
    def setDocumentLocator(self, locator):
        self.locator = locator
        return self.env
    def endDocument(self):
        return self.env
    def startElement(self, elem, attrs):
        self.env.manageNamespaces(attrs)
        if self.env.currentElem == None:
            self.env.currentElem = XmlElement(elem, attrs=attrs)
        else:
            # Reuse the exiting instance in order to avoid creating one instance
            # every time an elem is met in the XML file.
            self.env.currentElem.__init__(elem, attrs)
        return self.env
    def endElement(self, elem):
        self.env.currentElem.__init__(elem)
        return self.env
    def characters(self, content):
        return self.env

    def skippedEntity(self, name):
        '''This method is called every time expat does not recognize an entity.
           We provide here support for HTML entities.'''
        if HTML_ENTITIES.has_key(name):
            self.characters(HTML_ENTITIES[name].decode('utf-8'))
        else:
            # Put a question mark instead of raising an exception.
            self.characters('?')

    def parse(self, xml, source='string'):
        '''Parses a XML stream.
           * If p_source is "string", p_xml must be a string containing
             valid XML content.
           * If p_source is "file": p_xml can be:
             - a string containing the path to the XML file on disk;
             - a file instance opened for reading. Note that in this case, this
               method will close it.
        '''
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        self.parser.setContentHandler(self)
        self.parser.setErrorHandler(self)
        self.parser.setFeature(feature_external_ges, False)
        inputSource = InputSource()
        if source == 'string':
            inputSource.setByteStream(StringIO(xml))
        else:
            if not isinstance(xml, file):
                xml = file(xml)
            inputSource.setByteStream(xml)
        self.parser.parse(inputSource)
        if isinstance(xml, file): xml.close()
        return self.res

# ------------------------------------------------------------------------------
from appy.shared import UnmarshalledFile
from appy import Object
try:
    from DateTime import DateTime
except ImportError:
    DateTime = 'unicode'

class XmlUnmarshaller(XmlParser):
    '''This class allows to parse a XML file and recreate the corresponding web
       of Python objects. This parser assumes that the XML file respects this
       convention: any tag may define in attribute "type" storing the type of
       its content, which may be:
       
       bool * int * float * long * DateTime * tuple * list * object

       If "object" is specified, it means that the tag contains sub-tags, each
       one corresponding to the value of an attribute for this object.
       if "tuple" is specified, it will be converted to a list.'''
    def __init__(self, classes={}, tagTypes={}, conversionFunctions={}):
        XmlParser.__init__(self)
        # self.classes below is a dict whose keys are tag names and values are
        # Python classes. During the unmarshalling process, when an object is
        # encountered, instead of creating an instance of Object, we will create
        # an instance of the class specified in self.classes.
        # Root tag is named "xmlPythonData" by default by the XmlMarshaller.
        # This will not work if the object in the specified tag is not an
        # Object instance (ie it is a list or tuple or simple value). Note that
        # we will not call the constructor of the specified class. We will
        # simply create an instance of Objects and dynamically change the class
        # of the created instance to this class.
        if not isinstance(classes, dict) and classes:
            # The user may only need to define a class for the root tag
            self.classes = {'xmlPythonData': classes}
        else:
            self.classes = classes
        # We expect that the parsed XML file will follow some conventions
        # (ie, a tag that corresponds to a list has attribute type="list" or a
        # tag that corresponds to an object has attribute type="object".). If
        # it is not the case of p_xmlContent, you can provide the missing type
        # information in p_tagTypes. Here is an example of p_tagTypes:
        # {"information": "list", "days": "list", "person": "object"}.
        self.tagTypes = tagTypes
        # The parser assumes that data is represented in some standard way. If
        # it is not the case, you may provide, in this dict, custom functions
        # allowing to convert values of basic types (long, float, DateTime...).
        # Every such function must take a single arg which is the value to
        # convert and return the converted value. Dict keys are strings
        # representing types ('bool', 'int', 'unicode', etc) and dict values are
        # conversion functions. Here is an example:
        # {'int': convertInteger, 'DateTime': convertDate}
        # NOTE: you can even invent a new basic type, put it in self.tagTypes,
        # and create a specific conversionFunction for it. This way, you can
        # for example convert strings that have specific values (in this case,
        # knowing that the value is a 'string' is not sufficient).        
        self.conversionFunctions = conversionFunctions

    def convertAttrs(self, attrs):
        '''Converts XML attrs to a dict.'''
        res = {}
        for k, v in attrs.items():
            if ':' in k: # An attr prefixed with a namespace. Remove this.
                k = k.split(':')[-1]
            res[str(k)] = v
        return res

    def startDocument(self):
        self.res = None # The resulting web of Python objects (Object instances)
        self.env.containerStack = [] # The stack of current "containers" where
        # to store the next parsed element. A container can be a list, a tuple,
        # an object (the root object of the whole web or a sub-object).
        self.env.currentBasicType = None # Will hold the name of the currently
        # parsed basic type (unicode, float...)
        self.env.currentContent = '' # We store here the content of tags.

    containerTags = ('tuple', 'list', 'object', 'file')
    numericTypes = ('bool', 'int', 'float', 'long')
    def startElement(self, elem, attrs):
        # Remember the name of the previous element
        previousElem = None
        if self.env.currentElem:
            previousElem = self.env.currentElem.name
        e = XmlParser.startElement(self, elem, attrs)
        # Determine the type of the element.
        elemType = 'unicode' # Default value
        if attrs.has_key('type'):
            elemType = attrs['type']
        elif self.tagTypes.has_key(elem):
            elemType = self.tagTypes[elem]
        if elemType in self.containerTags:
            # I must create a new container object.
            if elemType == 'object':
                newObject = Object(**self.convertAttrs(attrs))
            elif elemType == 'tuple': newObject = [] # Tuples become lists
            elif elemType == 'list': newObject = []
            elif elemType == 'file':
                newObject = UnmarshalledFile()
                if attrs.has_key('name'):
                    newObject.name = attrs['name']
                if attrs.has_key('mimeType'):
                    newObject.mimeType = attrs['mimeType']
            else: newObject = Object(**self.convertAttrs(attrs))
            # Store the value on the last container, or on the root object.
            self.storeValue(elem, newObject)
            # Push the new object on the container stack
            e.containerStack.append(newObject)
        else:
            # If we are already parsing a basic type, it means that we were
            # wrong for our diagnotsic of the containing element: it was not
            # basic. We will make the assumption that the containing element is
            # then an object.
            if e.currentBasicType:
                # Previous elem was an object: create it on the stack.
                newObject = Object()
                self.storeValue(previousElem, newObject)
                e.containerStack.append(newObject)
            e.currentBasicType = elemType

    def storeValue(self, name, value):
        '''Stores the newly parsed p_value (contained in tag p_name) on the
           current container in environment self.env.'''
        e = self.env
        # Remove namespace prefix when relevant
        if ':' in name: name = name.split(':')[-1]
        # Change the class of the value if relevant
        if (name in self.classes) and isinstance(value, Object):
            value.__class__ = self.classes[name]
        # Where must I store this value?
        if not e.containerStack:
            # I store the object at the root of the web.
            self.res = value
        else:
            currentContainer = e.containerStack[-1]
            if isinstance(currentContainer, list):
                currentContainer.append(value)
            elif isinstance(currentContainer, UnmarshalledFile):
                currentContainer.content += value
            else:
                # Current container is an object
                if hasattr(currentContainer, name) and \
                   getattr(currentContainer, name):
                    # We have already encountered a sub-object with this name.
                    # Having several sub-objects with the same name, we will
                    # create a list.
                    attrValue = getattr(currentContainer, name)
                    if not isinstance(attrValue, list):
                        attrValue = [attrValue, value]
                    else:
                        attrValue.append(value)
                else:
                    attrValue = value
                setattr(currentContainer, name, attrValue)

    def characters(self, content):
        e = XmlParser.characters(self, content)
        if e.currentBasicType:
            e.currentContent += content

    def endElement(self, elem):
        e = XmlParser.endElement(self, elem)
        if e.currentBasicType:
            value = e.currentContent.strip()
            if not value: value = None
            else:
                # If we have a custom converter for values of this type, use it.
                if self.conversionFunctions.has_key(e.currentBasicType):
                    try:
                        value = self.conversionFunctions[e.currentBasicType](
                            value)
                    except Exception, err:
                        raise AppyError(CUSTOM_CONVERSION_ERROR % (
                            e.currentBasicType, value, str(err)))
                # If not, try a standard conversion
                elif e.currentBasicType in self.numericTypes:
                    try:
                        exec 'value = %s' % value
                    except SyntaxError:
                        raise AppyError(CONVERSION_ERROR % (
                            e.currentBasicType, value))
                    except NameError:
                        raise AppyError(CONVERSION_ERROR % (
                            e.currentBasicType, value))
                    # Check that the value is of the correct type. For instance,
                    # a float value with a comma in it could have been converted
                    # to a tuple instead of a float.
                    if not isinstance(value, eval(e.currentBasicType)):
                        raise AppyError(CONVERSION_ERROR % (
                            e.currentBasicType, value))
                elif e.currentBasicType == 'DateTime':
                    value = DateTime(value)
                elif e.currentBasicType == 'base64':
                    value = e.currentContent.decode('base64')
            # Store the value on the last container
            self.storeValue(elem, value)
            # Clean the environment
            e.currentBasicType = None
            e.currentContent = ''
        else:
            e.containerStack.pop()

    # Alias: "unmarshall" -> "parse"
    unmarshall = XmlParser.parse

# ------------------------------------------------------------------------------
class XmlMarshaller:
    '''This class allows to produce a XML version of a Python object, which
       respects some conventions as described in the doc of the corresponding
       Unmarshaller (see above).'''
    xmlEntities = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;',
                   "'": '&apos;'}
    trueFalse = {True: 'True', False: 'False'}
    sequenceTypes = (tuple, list)
    fieldsToMarshall = 'all'
    fieldsToExclude = []
    atFiles = ('image', 'file') # Types of archetypes fields that contain files.

    def __init__(self, cdata=False, dumpUnicode=False, conversionFunctions={},
                 dumpXmlPrologue=True, rootTag='xmlPythonData', namespaces={},
                 namespacedTags={}):
        # If p_cdata is True, all string values will be dumped as XML CDATA.
        self.cdata = cdata
        # If p_dumpUnicode is True, the result will be unicode.
        self.dumpUnicode = dumpUnicode
        # The following dict stores specific conversion (=Python to XML)
        # functions. A specific conversion function is useful when you are not
        # happy with the way built-in converters work, or if you want to
        # specify a specific way to represent, in XML, some particular Python
        # object or value. In this dict, every key represents a given type
        # (class names must be full-path class names); every value is a function
        # accepting 2 args: first one is the UnicodeBuffer where the result is
        # being dumped, while the second one is the Python object or value to
        # dump.
        self.conversionFunctions = conversionFunctions
        # If dumpXmlPrologue is True, the XML prologue will be dumped.
        self.dumpXmlPrologue = dumpXmlPrologue
        # The name of the root tag
        self.rootElementName = rootTag
        # The namespaces that will be defined at the root of the XML message.
        # It is a dict whose keys are namespace prefixes and whose values are
        # namespace URLs.
        self.namespaces = namespaces
        # The following dict will tell which XML tags will get which namespace
        # prefix ({s_tagName: s_prefix}). Special optional dict entry
        # '*':s_prefix will indicate a default prefix that will be applied to
        # any tag that does not have it own key in this dict.
        self.namespacedTags = namespacedTags
        self.objectType = None # Will be given by method m_marshal

    def getTagName(self, name):
        '''Returns the name of tag p_name as will be dumped. It can be p_name,
           or p_name prefixed with a namespace prefix (will depend on
           self.prefixedTags).'''
        # Determine the prefix
        prefix = ''
        if name in self.namespacedTags: prefix = self.namespacedTags[name]
        elif '*' in self.namespacedTags: prefix = self.namespacedTags['*']
        if prefix: return '%s:%s' % (prefix, name)
        return name

    def dumpRootTag(self, res, instance):
        '''Dumps the root tag.'''
        # Dumps the name of the tag.
        tagName = self.getTagName(self.rootElementName)
        res.write('<'); res.write(tagName)
        # Dumps namespace definitions if any
        for prefix, url in self.namespaces.iteritems():
            res.write(' xmlns:%s="%s"' % (prefix, url))
        # Dumps Appy- or Plone-specific attributed
        if self.objectType != 'popo':
            res.write(' type="object" id="%s"' % instance.UID())
        res.write('>')
        return tagName

    def dumpString(self, res, s):
        '''Dumps a string into the result.'''
        if self.cdata: res.write('<![CDATA[')
        if isinstance(s, str):
            s = s.decode('utf-8')
        # Replace special chars by XML entities
        for c in s:
            if self.xmlEntities.has_key(c):
                res.write(self.xmlEntities[c])
            else:
                res.write(c)
        if self.cdata: res.write(']]>')

    def dumpFile(self, res, v):
        '''Dumps a file into the result.'''
        if not v: return
        # p_value contains the (possibly binary) content of a file. We will
        # encode it in Base64, in one or several parts.
        partTag = self.getTagName('part')
        res.write('<%s type="base64" number="1">' % partTag)
        if hasattr(v, 'data'):
            # The file is an Archetypes file.
            valueType = v.data.__class__.__name__
            if valueType == 'Pdata':
                # There will be several parts.
                res.write(v.data.data.encode('base64'))
                # Write subsequent parts
                nextPart = v.data.next
                nextPartNumber = 2
                while nextPart:
                    res.write('</%s>' % partTag) # Close the previous part
                    res.write('<%s type="base64" number="%d">' % \
                              (partTag, nextPartNumber))
                    res.write(nextPart.data.encode('base64'))
                    nextPart = nextPart.next
                    nextPartNumber += 1
            else:
                res.write(v.data.encode('base64'))
        else:
            res.write(v.encode('base64'))
        res.write('</%s>' % partTag)

    def dumpValue(self, res, value, fieldType, isRef=False):
        '''Dumps the XML version of p_value to p_res.'''
        # Use a custom function if one is defined for this type of value.
        className = value.__class__.__name__
        if className in self.conversionFunctions:
            self.conversionFunctions[className](res, value)
            return
        # Use a standard conversion else.
        if fieldType == 'file':
            self.dumpFile(res, value)
        elif isRef:
            if value:
                if type(value) in self.sequenceTypes:
                    for elem in value:
                        self.dumpField(res, 'url', elem.absolute_url())
                else:
                    self.dumpField(res, 'url', value.absolute_url())
        elif type(value) in self.sequenceTypes:
            # The previous condition must be checked before this one because
            # referred objects may be stored in lists or tuples, too.
            for elem in value:
                self.dumpField(res, 'e', elem)
        elif isinstance(value, basestring):
            self.dumpString(res, value)
        elif isinstance(value, bool):
            res.write(self.trueFalse[value])
        elif fieldType == 'object':
            if hasattr(value, 'absolute_url'):
                # Dump the URL to the object only
                res.write(value.absolute_url())
            else:
                # Dump the entire object content
                for k, v in value.__dict__.iteritems():
                    if not k.startswith('__'):
                        self.dumpField(res, k, v)
                # Maybe we could add a parameter to the marshaller to know how
                # to marshall objects (produce an ID, an URL, include the entire
                # tag but we need to take care of circular references,...)
        else:
            res.write(value)

    def dumpField(self, res, fieldName, fieldValue, fieldType='basic'):
        '''Dumps in p_res, the value of the p_field for p_instance.'''
        fieldTag = self.getTagName(fieldName)
        res.write('<'); res.write(fieldTag)
        # Dump the type of the field as an XML attribute
        fType = None # No type will mean "unicode".
        if   fieldType == 'file':                         fType = 'file'
        elif fieldType == 'ref':                          fType = 'list'
        elif isinstance(fieldValue, bool):                fType = 'bool'
        elif isinstance(fieldValue, int):                 fType = 'int'
        elif isinstance(fieldValue, float):               fType = 'float'
        elif isinstance(fieldValue, long):                fType = 'long'
        elif isinstance(fieldValue, tuple):               fType = 'tuple'
        elif isinstance(fieldValue, list):                fType = 'list'
        elif fieldValue.__class__.__name__ == 'DateTime': fType = 'DateTime'
        elif self.isAnObject(fieldValue):                 fType = 'object'
        if self.objectType != 'popo':
            if fType: res.write(' type="%s"' % fType)
            # Dump other attributes if needed
            if type(fieldValue) in self.sequenceTypes:
                res.write(' count="%d"' % len(fieldValue))
        if fType == 'file':
            if hasattr(fieldValue, 'content_type'):
                res.write(' mimeType="%s"' % fieldValue.content_type)
            if hasattr(fieldValue, 'filename'):
                res.write(' name="')
                self.dumpString(res, fieldValue.filename)
                res.write('"')
        res.write('>')
        # Dump the field value
        self.dumpValue(res, fieldValue, fType, isRef=(fieldType=='ref'))
        res.write('</'); res.write(fieldTag); res.write('>')

    def isAnObject(self, instance):
        '''Returns True if p_instance is a class instance, False if it is a
           basic type, or tuple, sequence, etc.'''
        iType = type(instance)
        if iType == types.InstanceType:
            return True
        elif iType.__name__ == 'ImplicitAcquirerWrapper':
            # This is the case with Archetype instances
            return True
        elif iType.__class__.__name__ == 'ExtensionClass':
            return True
        
        return False

    def marshall(self, instance, objectType='popo', conversionFunctions={}):
        '''Returns in a UnicodeBuffer the XML version of p_instance. If
           p_instance corresponds to a Plain Old Python Object, specify 'popo'
           for p_objectType. If p_instance corresponds to an Archetypes object
           (Zope/Plone), specify 'archetype' for p_objectType. if p_instance is
           a Appy object, specify "appy" as p_objectType. If p_instance is not
           an instance at all, but another Python data structure or basic type,
           p_objectType is ignored.'''
        self.objectType = objectType
        # Call the XmlMarshaller constructor if it hasn't been called yet.
        if not hasattr(self, 'cdata'):
            XmlMarshaller.__init__(self)
        if conversionFunctions:
            self.conversionFunctions.update(conversionFunctions)
        # Create the buffer where the XML result will be dumped.
        res = UnicodeBuffer()
        # Dump the XML prologue if required
        if self.dumpXmlPrologue:
            res.write(xmlPrologue)
        if self.isAnObject(instance):
            # Dump the root tag
            rootTagName = self.dumpRootTag(res, instance)
            # Dump the fields of this root object
            if objectType == 'popo':
                for fieldName, fieldValue in instance.__dict__.iteritems():
                    mustDump = False
                    if fieldName in self.fieldsToExclude:
                        mustDump = False
                    elif self.fieldsToMarshall == 'all':
                        mustDump = True
                    else:
                        if (type(self.fieldsToMarshall) in self.sequenceTypes) \
                           and (fieldName in self.fieldsToMarshall):
                            mustDump = True
                    if mustDump:
                        self.dumpField(res, fieldName, fieldValue)
            elif objectType == 'archetype':
                for field in instance.schema.fields():
                    # Dump only needed fields
                    mustDump = False
                    if field.getName() in self.fieldsToExclude:
                        mustDump = False
                    elif (self.fieldsToMarshall == 'all') and \
                       (field.schemata != 'metadata'):
                        mustDump = True
                    elif self.fieldsToMarshall == 'all_with_metadata':
                        mustDump = True
                    else:
                        if (type(self.fieldsToMarshall) in self.sequenceTypes) \
                           and (field.getName() in self.fieldsToMarshall):
                            mustDump = True
                    if mustDump:
                        fieldType = 'basic'
                        if field.type in self.atFiles:
                            fieldType = 'file'
                        elif field.type == 'reference':
                            fieldType = 'ref'
                        self.dumpField(res, field.getName(),field.get(instance),
                                       fieldType=fieldType)
            elif objectType == 'appy':
                for field in instance.getAllAppyTypes():
                    # Dump only needed fields
                    if field.name in self.fieldsToExclude: continue
                    if (field.type == 'Ref') and field.isBack: continue
                    if (type(self.fieldsToMarshall) in self.sequenceTypes) \
                        and (field.name not in self.fieldsToMarshall): continue
                    # Determine field type
                    fieldType = 'basic'
                    if field.type == 'File':
                        fieldType = 'file'
                    elif field.type == 'Ref':
                        fieldType = 'ref'
                    self.dumpField(res, field.name,field.getValue(instance),
                                   fieldType=fieldType)
                # Dump the object history.
                histTag = self.getTagName('history')
                eventTag = self.getTagName('event')
                res.write('<%s type="list">' % histTag)
                wfInfo = instance.portal_workflow.getWorkflowsFor(instance)
                if wfInfo:
                    history = instance.workflow_history[wfInfo[0].id]
                    for event in history:
                        res.write('<%s type="object">' % eventTag)
                        for k, v in event.iteritems():
                            self.dumpField(res, k, v)
                        res.write('</%s>' % eventTag)
                res.write('</%s>' % histTag)
            self.marshallSpecificElements(instance, res)
            res.write('</'); res.write(rootTagName); res.write('>')
        else:
            self.dumpField(res, self.rootElementName, instance)
        # Return the result
        res = res.getValue()
        if not self.dumpUnicode:
            res = res.encode('utf-8')
        return res

    def marshallSpecificElements(self, instance, res):
        '''You can use this marshaller as a base class for creating your own.
           In this case, this method will be called by the marshall method
           for allowing your concrete marshaller to insert more things in the
           result. p_res is the UnicodeBuffer buffer where the result of the
           marshalling process is currently dumped; p_instance is the instance
           currently marshalled.'''

# ------------------------------------------------------------------------------
class XmlHandler(ContentHandler):
    '''This handler is used for producing, in self.res, a readable XML
       (with carriage returns) and for removing some tags that always change
       (like dates) from a file that need to be compared to another file.'''
    def __init__(self, xmlTagsToIgnore, xmlAttrsToIgnore):
        ContentHandler.__init__(self)
        self.res = unicode(xmlPrologue)
        self.namespaces = {} # ~{s_namespaceUri:s_namespaceName}~
        self.indentLevel = -1
        self.tabWidth = 3
        self.tagsToIgnore = xmlTagsToIgnore
        self.attrsToIgnore = xmlAttrsToIgnore
        self.ignoring = False # Some content must be ignored, and not dumped
        # into the result.
    def isIgnorable(self, elem):
        '''Is p_elem an ignorable element ?'''
        res = False
        for tagName in self.tagsToIgnore:
            if isinstance(tagName, list) or isinstance(tagName, tuple):
                # We have a namespace
                nsUri, elemName = tagName
                try:
                    nsName = self.ns(nsUri)
                    elemFullName = '%s:%s' % (nsName, elemName)
                except KeyError:
                    elemFullName = ''
            else:
                # No namespace
                elemFullName = tagName
            if elemFullName == elem:
                res = True
                break
        return res
    def setDocumentLocator(self, locator):
        self.locator = locator
    def endDocument(self):
        pass
    def dumpSpaces(self):
        self.res += '\n' + (' ' * self.indentLevel * self.tabWidth)
    def manageNamespaces(self, attrs):
        '''Manage namespaces definitions encountered in attrs'''
        for attrName, attrValue in attrs.items():
            if attrName.startswith('xmlns:'):
                self.namespaces[attrValue] = attrName[6:]
    def ns(self, nsUri):
        return self.namespaces[nsUri]
    def startElement(self, elem, attrs):
        self.manageNamespaces(attrs)
        # Do we enter into a ignorable element ?
        if self.isIgnorable(elem):
            self.ignoring = True
        else:
            if not self.ignoring:
                self.indentLevel += 1
                self.dumpSpaces()
                self.res += '<%s' % elem
                attrsNames = attrs.keys()
                attrsNames.sort()
                for attrToIgnore in self.attrsToIgnore:
                    if attrToIgnore in attrsNames:
                        attrsNames.remove(attrToIgnore)
                for attrName in attrsNames:
                    self.res += ' %s="%s"' % (attrName, attrs[attrName])
                self.res += '>'
    def endElement(self, elem):
        if self.isIgnorable(elem):
            self.ignoring = False
        else:
            if not self.ignoring:
                self.dumpSpaces()
                self.indentLevel -= 1
                self.res += '</%s>' % elem
    def characters(self, content):
        if not self.ignoring:
            self.res += content.replace('\n', '')

# ------------------------------------------------------------------------------
class XmlComparator:
    '''Compares 2 XML files and produces a diff.'''
    def __init__(self, fileNameA, fileNameB, areXml=True, xmlTagsToIgnore=(),
        xmlAttrsToIgnore=()):
        self.fileNameA = fileNameA
        self.fileNameB = fileNameB
        self.areXml = areXml # Can also diff non-XML files.
        self.xmlTagsToIgnore = xmlTagsToIgnore
        self.xmlAttrsToIgnore = xmlAttrsToIgnore

    def filesAreIdentical(self, report=None, encoding=None):
        '''Compares the 2 files and returns True if they are identical (if we
           ignore xmlTagsToIgnore and xmlAttrsToIgnore).
           If p_report is specified, it must be an instance of
           appy.shared.test.TestReport; the diffs will be dumped in it.'''
        # Perform the comparison
        differ = difflib.Differ()
        if self.areXml:
            f = file(self.fileNameA)
            contentA = f.read()
            f.close()
            f = file(self.fileNameB)
            contentB = f.read()
            f.close()
            xmlHandler = XmlHandler(self.xmlTagsToIgnore, self.xmlAttrsToIgnore)
            xml.sax.parseString(contentA, xmlHandler)
            contentA = xmlHandler.res.split('\n')
            xmlHandler = XmlHandler(self.xmlTagsToIgnore, self.xmlAttrsToIgnore)
            xml.sax.parseString(contentB, xmlHandler)
            contentB = xmlHandler.res.split('\n')
        else:
            f = file(self.fileNameA)
            contentA = f.readlines()
            f.close()
            f = file(self.fileNameB)
            contentB = f.readlines()
            f.close()
        diffResult = list(differ.compare(contentA, contentB))
        # Analyse, format and report the result.
        atLeastOneDiff = False
        lastLinePrinted = False
        i = -1
        for line in diffResult:
            i += 1
            if line and (line[0] != ' '):
                if not atLeastOneDiff:
                    msg = 'Difference(s) detected between files %s and %s:' % \
                          (self.fileNameA, self.fileNameB)
                    if report: report.say(msg, encoding='utf-8')
                    else:      print msg
                    atLeastOneDiff = True
                if not lastLinePrinted:
                    if report: report.say('...')
                    else: print '...'
                if self.areXml:
                    if report: report.say(line, encoding=encoding)
                    else: print line
                else:
                    if report: report.say(line[:-1], encoding=encoding)
                    else: print line[:-1]
                lastLinePrinted = True
            else:
                lastLinePrinted = False
        return not atLeastOneDiff
# ------------------------------------------------------------------------------

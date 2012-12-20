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
import time
from appy.shared.utils import Traceback
from appy.shared.xml_parser import escapeXhtml

# Some POD-specific constants --------------------------------------------------
XHTML_HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
XHTML_LISTS = ('ol', 'ul')
XHTML_PARAGRAPH_TAGS = XHTML_HEADINGS + XHTML_LISTS + ('p',)
XHTML_PARAGRAPH_TAGS_NO_LISTS = XHTML_HEADINGS + ('p',)
XHTML_INNER_TAGS = ('b', 'i', 'u', 'em')
XHTML_UNSTYLABLE_TAGS = XHTML_LISTS + ('li', 'a')

# ------------------------------------------------------------------------------
class PodError(Exception):
    def dumpTraceback(buffer, tb, textNs, removeFirstLine):
        if removeFirstLine:
            # This error came from an exception raised by pod. The text of the
            # error may be very long, so we avoid having it as error cause +
            # in the first line of the traceback.
            linesToRemove = 3
        else:
            linesToRemove = 2
        i = 0
        for tLine in tb.splitlines():
            i += 1
            if i > linesToRemove:
                buffer.write('<%s:p>' % textNs)
                try:
                    buffer.dumpContent(tLine)
                except UnicodeDecodeError, ude:
                    buffer.dumpContent(tLine.decode('utf-8'))
                buffer.write('</%s:p>' % textNs)
    dumpTraceback = staticmethod(dumpTraceback)
    def dump(buffer, message, withinElement=None, removeFirstLine=False, dumpTb=True):
        '''Dumps the error p_message in p_buffer.'''
        # Define some handful shortcuts
        e = buffer.env
        ns = e.namespaces
        dcNs = e.ns(e.NS_DC)
        officeNs = e.ns(e.NS_OFFICE)
        textNs = e.ns(e.NS_TEXT)
        if withinElement:
            buffer.write('<%s>' % withinElement.OD.elem)
            for subTag in withinElement.subTags:
                buffer.write('<%s>' % subTag.elem)
        buffer.write('<%s:annotation><%s:creator>POD</%s:creator>' \
                     '<%s:date>%s</%s:date><%s:p>' % \
                     (officeNs, dcNs, dcNs, dcNs,
                      time.strftime('%Y-%m-%dT%H:%M:%S'), dcNs, textNs))
        buffer.dumpContent(message)
        buffer.write('</%s:p>' % textNs)
        if dumpTb:
            # We don't dump the traceback if it is an expression error (it is
            # already included in the error message)
            PodError.dumpTraceback(buffer, Traceback.get(), textNs,
                                   removeFirstLine)
        buffer.write('</%s:annotation>' % officeNs)
        if withinElement:
            subTags = withinElement.subTags[:]
            subTags.reverse()
            for subTag in subTags:
                buffer.write('</%s>' % subTag.elem)
            buffer.write('</%s>' % withinElement.OD.elem)
    dump = staticmethod(dump)

# XXX To remove, present for backward compatibility only.
convertToXhtml = escapeXhtml
# ------------------------------------------------------------------------------

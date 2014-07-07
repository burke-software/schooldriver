'''PX stands for *P*ython *X*ML. It is a templating engine that reuses the pod
   engine to produce XML (including XHTML) from templates written as a mix of
   Python and XML.'''

# ------------------------------------------------------------------------------
import xml.sax
from px_parser import PxParser, PxEnvironment
from appy.pod.buffers import MemoryBuffer
from appy.shared.xml_parser import xmlPrologue, xhtmlPrologue

# Exception class --------------------------------------------------------------
class PxError(Exception): pass

# ------------------------------------------------------------------------------
class Px:
    '''Represents a (chunk of) PX code.'''
    xmlPrologue = xmlPrologue
    xhtmlPrologue = xhtmlPrologue

    def __init__(self, content, isFileName=False, partial=True,
                 template=None, hook=None, prologue=None, unicode=True):
        '''p_content is the PX code, as a string, or a file name if p_isFileName
           is True. If this code represents a complete XML file, p_partial is
           False. Else, we must surround p_content with a root tag to be able
           to parse it with a SAX parser.

           If this PX is based on another PX template, specify the PX template
           in p_template and the name of the p_hook where to insert this PX into
           the template PX.

           If a p_prologue is specified, it will be rendered at the start of the
           PX result.

           By default, a PX's result will be a unicode. If you want to get an
           encoded str instead, use p_unicode=False.
        '''
        # Get the PX content
        if isFileName:
            f = file(content)
            self.content = f.read()
            f.close()
        else:
            self.content = content
        # It this content a complete XML file, or just some part of it?
        self.partial = partial
        # Is this PX based on a template PX?
        self.template = template
        self.hook = hook
        # Is there some (XML, XHTML...) prologue to dump?
        self.prologue = prologue
        # Will the result be unicode or str?
        self.unicode = unicode
        self.parse()

    def parse(self):
        '''Parses self.content and create the structure corresponding to this
           PX.'''
        if self.partial:
            # Surround the partial chunk with a root tag: it must be valid XML.
            self.content = '<x>%s</x>' % self.content
        # Create a PX parser
        self.parser = PxParser(PxEnvironment(), self)
        # Parses self.content (a PX code in a string) with self.parser, to
        # produce a tree of memory buffers.
        try:
            self.parser.parse(self.content)
        except xml.sax.SAXParseException, spe:
            self.completeErrorMessage(spe)
            raise spe

    def completeErrorMessage(self, parsingError):
        '''A p_parsingError occurred. Complete the error message with the
           erroneous line from self.content.'''
        # Split lines from self.content
        splitted = self.content.split('\n')
        i = parsingError.getLineNumber() - 1
        # Get the erroneous line, and add a subsequent line for indicating
        # the erroneous column.
        column = ' ' * (parsingError.getColumnNumber()-1) + '^'
        lines = [splitted[i], column]
        # Get the previous and next lines when present.
        if i > 0: lines.insert(0, splitted[i-1])
        if i < len(splitted)-1: lines.append(splitted[i+1])
        parsingError._msg += '\n%s' % '\n'.join(lines)

    def __call__(self, context, applyTemplate=True):
        '''Renders the PX.

           If the PX is based on a template PX, we have 2 possibilities.
           1. p_applyTemplate is True. This case corresponds to the initial
              call to the current PX. In this case we call the template with a
              context containing, in the hook variable, the current PX.
           2. p_applyTemplate is False. In this case, we are currently executing
              the PX template, and, at the hook, we must include the current PX,
              as is, without re-applying the template (else, an infinite
              recursion would occur).
        '''
        # Developer, forget the following line forever.
        if '_ctx_' not in context: context['_ctx_'] = context

        if self.hook and applyTemplate:
            # Call the template PX, filling the hook with the current PX.
            context[self.hook] = self
            return self.template(context)
        else:
            # Create a Memory buffer for storing the result.
            env = self.parser.env
            result = MemoryBuffer(env, None)
            env.ast.evaluate(result, context)
            res = result.content
            if self.prologue:
                res = self.prologue + res
            if not self.unicode:
                res = res.encode('utf-8')
            return res

    def override(self, content, partial=True):
        '''Overrides the content of this PX with a new p_content (as a
           string).'''
        self.partial = partial
        self.content = content
        # Parse again, with new content.
        self.parse()
# ------------------------------------------------------------------------------

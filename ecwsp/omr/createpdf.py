#   Copyright 2011 Burke Software and Consulting LLC
#   Author Callista Goss <calli@burkesoftware.com>
#   
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.



from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.barcode.common import *
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.graphics.barcode import getCodes, createBarcodeDrawing, getCodeNames, createBarcodeDrawing, createBarcodeImageInMemory
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from xml.dom import minidom
from orderedDict import OrderedDict
from tempfile import gettempdir

def createpdf(xml_test):
    global page
    page = 1
    xml(xml_test)
    createBanding()
    pdf = "/test.pdf"
    temp = gettempdir()
    temp_pdf_file = temp + pdf
    temp_banding_file = temp + "/banding.xml"
    c = canvas.Canvas(temp_pdf_file, pagesize=letter)
    createTest(c)
    c.showPage()
    c.save()
    download = c.getpdfdata()
    banding = open(temp_banding_file, 'w')
    doc.writexml(banding)
    banding.close()
    
    return download, temp_pdf_file, temp_banding_file
    
def newPage(c):
    global page
    c.translate(0,0)
    barcode(c)
    drawLines(c)
    c.translate(left_margin,bottom_margin)
    pageBanding()
    page = page +1
    
def drawLines(c):
    #bottom left
    c.line(.5*inch,.5*inch,1.25*inch,.5*inch)
    c.line(.5*inch,.5*inch,.5*inch,1.25*inch)
    #bottom right
    c.line(width - .75*inch,.5*inch,width - 1.5*inch,.5*inch)
    c.line(width - .75*inch,.5*inch,width - .75*inch,1.5*inch)
    #top left
    c.line(.5*inch,height - .75*inch,1.25*inch,height - .75*inch)
    c.line(.5*inch,height - .75*inch,.5*inch,height - 1.5*inch)
    #top right
    c.line(width - .75*inch,height - .75*inch,width - 1.75*inch, height - .75*inch)
    c.line(width - .75*inch,height - .75*inch,width - .75*inch, height - 1.5*inch)
    
def barcode(c):
    global code
    code = "A" + str(id).zfill(6) + (str(page).zfill(3)) + "A"
    barcode = Codabar(code, barWidth = inch*0.02)
    x = width - (3.2*inch)
    y = height - (.5*inch)
    barcode.drawOn(c,x,y)
    
def createTest(c):
    #need to do it for multiple tests -tests[id]:questions and -teacher_tests[id]:teacher_questions
    global indent, questions, choices, column, sort, next_line, width, height, next_line,left_margin,right_margin,bottom_margin,top_margin, id, newbox
    indent = 0
    column = 0
    
    #top right corner is 612x792 - x,y in 1/72 of an inch OR (width-margins) x (1height-margins)
    #translate: moves the starting point up and to the right x*inch
    #global default_font, font_size, line_space,left_margin,right_margin,top_margin,bottom_margin,first_line,width,height,indent
    default_font = "Helvetica"
    font_size = 12
    #spacing: 1 for single line, 2 for double spacing, etc
    line_space = 1.5*font_size
    left_margin,right_margin,top_margin,bottom_margin = inch,inch,inch,inch
    width, height = letter
    first_line = (height) - (top_margin + bottom_margin + font_size)
    ct = 1
    for test, questions in tests.iteritems():
        newbox = False
        newbox_trigger = False
        page = 1
        id = test
        newPage(c)
        c.setFont(default_font,font_size)
        testBanding()
        
        c.drawString(indent,first_line, title)
        next_line = first_line - (line_space)
        c.drawString(indent,next_line,names[id])
        next_line = next_line - (line_space)
        
        def createSections(questions,choices):
            global indent, column, sort, next_line, oldindent, lastline
            lines = 0
            sort = 1
            for question in questions:
                if next_line + font_size <=0:
                    if newbox_trigger:
                        lastline = next_line
                        oldindent = indent
                        newbox = True
                    column +=1
                    if column == 3:
                        column=0
                        c.showPage()
                        newPage(c)
                    next_line = first_line - line_space*2
                    indent = ((width-left_margin-right_margin)/3)*column
                choice_number = len(questions[question])
                if choice_number > 0:
                    next_line=next_line - line_space
                if choice_number ==2:
                    extra_indent=45
                elif choice_number <= 5:
                    extra_indent = 25
                else:
                    extra_indent = 18
                    
                c.drawString(indent,next_line,question)
                questionBanding(question)
                sort+=1
                choice_indent = indent + extra_indent
                for choice in questions[question]:
                    c.drawString(choice_indent,next_line+line_space,choice)
                    c.rect(choice_indent,next_line,12,12,fill=0)
                    choiceBanding(choice_indent,next_line+13,choice_indent+13,next_line+26,choice)
                    choice_indent+=extra_indent;
                next_line = next_line - line_space
                lines+=1
    
    
    
        createSections(questions,choices)
        if teacherNode:
            global oldindent,lastline
            newbox = False
            newbox_trigger = True
            next_line = next_line - line_space*4
            if next_line + font_size <= 0:
                oldindent = indent
                lastline = next_line
                column +=1
                if column == 3:
                    column=0    
                    c.showPage()
                    newPage(c)
                next_line = first_line - line_space*2
                indent = ((width-left_margin-right_margin)/3)*column
            #draw a box
            c.drawString(indent,next_line,teacher_section)
            beginy = next_line+line_space
            
            c.line(indent-20,beginy,150+indent,beginy)
            next_line = next_line - (line_space)
            createSections(teacher_questions,teacher_choices)
            
            if newbox == True:
                c.line(oldindent-20,lastline,oldindent+150,lastline)
                c.line(indent-5,first_line - line_space,150+indent,first_line - line_space)
                c.line(indent-5,first_line - line_space,indent-5,next_line)
                c.line(150+indent,first_line - line_space,150+indent,next_line)
                c.line(oldindent-20,beginy,oldindent-20,lastline)
                c.line(150,beginy,150+indent,lastline)
                c.line(indent-5,next_line,150+indent,next_line)
            else:
                c.line(indent-20,next_line,150+indent,next_line)
                c.line(indent-20,beginy,indent-20,next_line)
                c.line(150+indent,beginy,150+indent,next_line)
        
        if ct < tests.__len__():
            column = 0
            indent = 0
            page = 1
            c.showPage()
        ct+=1

def xml(test_xml):
    global tests, teacher_tests
    global title, names, questions, choices, id,teacher_questions, teacher_choices, teacher_section
    xmldoc = minidom.parseString(test_xml)
    #xmldoc = xml
    test = xmldoc.firstChild
    global teacherNode
    teacherNode = None
    ids = xmldoc.getElementsByTagName('id')
    teacher_tests = OrderedDict()
    tests = OrderedDict()
    names = OrderedDict()
    #put student_names in a dict to match tests
    for singleid in ids:
        id = singleid.firstChild.nodeValue
        title = singleid.getElementsByTagName('title')[0].firstChild.data
        sections = singleid.getElementsByTagName('section')
        studentNode = sections[0]
        names[id] = studentNode.getElementsByTagName('name')[0].firstChild.data
        if len(sections)>1:
            teacherNode = sections[1]
        #student = {dict of tests:{dict of questions:[list of choices]}{}}
        questions = OrderedDict()
        questionNodes = studentNode.getElementsByTagName('question')
        for question in questionNodes:
            questiontemp = question.getElementsByTagName('text')[0].firstChild.wholeText
            choicesNodes = question.getElementsByTagName('choice')
            choices = []
            for choice in choicesNodes:
                choicetemp = [choice.firstChild.nodeValue]
                choices.extend(choicetemp)
            counter = 0
            temp = questiontemp
            while temp in questions:
                counter = counter +1
                temp = questiontemp + `counter` + '.'
            if counter != 0:
                questiontemp += `counter` + '.'
            questions[questiontemp] = choices
        
        tests[id] = questions
            
        #teacher = {{dict of essay questions:[list of point values]}{}}
        if teacherNode!=None:
            teacher_section = teacherNode.getElementsByTagName('name')[0].firstChild.data
            teacher_questions = OrderedDict()
            teacher_questionNodes = teacherNode.getElementsByTagName('question')
            for teacher_question in teacher_questionNodes:
                questiontemp = teacher_question.getElementsByTagName('text')[0].firstChild.wholeText
                choicesNodes = teacher_question.getElementsByTagName('choice')
                teacher_choices = []
                for choice in choicesNodes:
                    choicetemp = [choice.firstChild.nodeValue]
                    teacher_choices.extend(choicetemp)
                counter = 0
                temp = questiontemp
                while temp in teacher_questions:
                    counter = counter +1
                    temp = questiontemp + `counter` + '.'
                if counter != 0:
                    questiontemp += `counter` + '.'
                teacher_questions[questiontemp] = teacher_choices
            
        teacher_tests[id] = teacher_questions    

def createBanding():
    global doc, questionnaire
    doc = minidom.Document()
    quexf = doc.createElement("queXF")
    doc.appendChild(quexf)
    questionnaire = doc.createElement("questionnaire")
    quexf.appendChild(questionnaire)

def testBanding():
    global doc, questionnaire
    idtag = doc.createElement("id")
    questionnaire.appendChild(idtag)
    idtext = doc.createTextNode(str(id))
    idtag.appendChild(idtext)
    
    sectiontag = doc.createElement("section")
    sectiontag.setAttribute("id","1")
    questionnaire.appendChild(sectiontag)
    label = doc.createElement("label")
    sectiontag.appendChild(label)
    labeltext = doc.createTextNode(str(names[id]))
    label.appendChild(labeltext)
    
def pageBanding():
    global pagetag
    pagetag = doc.createElement("page")
    questionnaire.appendChild(pagetag)
    pgidtag = doc.createElement("id")
    pagetag.appendChild(pgidtag)
    pgidtext = doc.createTextNode(code)
    pgidtag.appendChild(pgidtext)
    
    rotationtag = doc.createElement("rotation")
    pagetag.appendChild(rotationtag)
    rotationText = doc.createTextNode("0")
    rotationtag.appendChild(rotationText)

def questionBanding(question):
    global boxgroup
    boxgroup = doc.createElement("boxgroup")
    pagetag.appendChild(boxgroup)
    typetag = doc.createElement("type")
    boxgroup.appendChild(typetag)
    typetext = doc.createTextNode("1")
    typetag.appendChild(typetext)
    widthtag = doc.createElement("width")
    boxgroup.appendChild(widthtag)
    widthtext = doc.createTextNode("1")
    widthtag.appendChild(widthtext)
    sorttag = doc.createElement("sortorder")
    boxgroup.appendChild(sorttag)
    sorttext = doc.createTextNode(str(sort))
    sorttag.appendChild(sorttext)
    label2 = doc.createElement("label")
    boxgroup.appendChild(label2)
    labeltext = doc.createTextNode(question)
    label2.appendChild(labeltext)
    groupsectiontag = doc.createElement("groupsection")
    groupsectiontag.setAttribute("idref","1")
    boxgroup.appendChild(groupsectiontag)
        
def choiceBanding(topx,topy,botx,boty,choice):
    topx = (topx+inch)*300/72
    botx = (botx+inch)*300/72
    topy = (height - topy-top_margin)*300/72
    boty = (height - boty-top_margin)*300/72
    box = doc.createElement("box")
    boxgroup.appendChild(box)
    tlx = doc.createElement("tlx")
    box.appendChild(tlx)
    tlxnum = doc.createTextNode(str(topx))
    tlx.appendChild(tlxnum)
    tly = doc.createElement("tly")
    box.appendChild(tly)
    tlynum = doc.createTextNode(str(topy))
    tly.appendChild(tlynum)
    brx = doc.createElement("brx")
    box.appendChild(brx)
    brxnum = doc.createTextNode(str(botx))
    brx.appendChild(brxnum)
    bry = doc.createElement("bry")
    box.appendChild(bry)
    brynum = doc.createTextNode(str(boty))
    bry.appendChild(brynum)
    value = doc.createElement("value")
    box.appendChild(value)
    #value
    #valuetext = doc.createTextNode('')
    boxlabel = doc.createElement("label")
    box.appendChild(boxlabel)
    boxlabeltext = doc.createTextNode(choice)
    boxlabel.appendChild(boxlabeltext)
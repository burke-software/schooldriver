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

def createpdf(xml_test, response):
    global page
    page = 1
    xml(xml_test)
    createBanding()
    pdf = "Test_" + id + "_" + studentName.replace(' ','_') + ".pdf"
    print pdf
    c = canvas.Canvas(response, pagesize=letter)
    createTest(c)
    c.showPage()
    c.save()
    
    #banding = open('/home/calli/Downloads/smallerFile.xml', 'w')
    #doc.writexml(banding)
    #banding.close()
    return pdf

    
    
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
    code = str(id) + str(page)
    code = code.zfill(8)
    barcode = Codabar(code, barWidth = inch*0.02)
    x = width - (3*inch)
    y = height - (.5*inch)
    barcode.drawOn(c,x,y)
    
def createTest(c):
    global indent, column, sort, next_line, width, height, next_line,left_margin,right_margin,bottom_margin,top_margin
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
    newPage(c)
    c.setFont(default_font,font_size)
    
    c.drawString(indent,first_line, title)
    next_line = first_line - (line_space)
    c.drawString(indent,next_line,studentName)
    next_line = next_line - (line_space)
    sort = 1
    
    
    def createSections(groups,questions,choices):
        global indent, column, sort, next_line
        for group in groups:
            c.drawString(indent,next_line,group)
            next_line = next_line - line_space
            if next_line + font_size <= 0:
                column +=1
                if column == 3:
                    column=0    
                    c.showPage()
                    newPage(c)
                next_line = first_line - line_space*2
                indent = ((width-left_margin-right_margin)/3)*column
    
            questions = groups[group]
            oldnumber = 0
            for question in questions:
                if next_line + font_size <=0:
                    column +=1
                    if column == 3:
                        column=0
                        c.showPage()
                        newPage(c)
                    next_line = first_line - line_space*2
                    indent = ((width-left_margin-right_margin)/3)*column
                
                choice_number = len(questions[question])
                if choice_number != oldnumber:
                    next_line=next_line - line_space
                if choice_number ==2:
                    extra_indent=45
                elif choice_number <= 5:
                    extra_indent = 25
                else:
                    extra_indent = 18
                    
                c.drawString(indent,next_line,question)
                questionBanding(group, question)
                sort+=1
                choice_indent = indent + extra_indent
                for choice in questions[question]:
                    if choice_number != oldnumber:
                        c.drawString(choice_indent,next_line+line_space,choice)
                    c.rect(choice_indent,next_line,12,12,fill=0)
                    choiceBanding(choice_indent,next_line+13,choice_indent+13,next_line+26,choice)
                    choice_indent+=extra_indent;
                next_line = next_line - line_space
                oldnumber = choice_number



    createSections(groups,questions,choices)
    if teacherNode:
        next_line = next_line - line_space*4
        if next_line + font_size <= 0:
            column +=1
            if column == 3:
                column=0    
                c.showPage()
                newPage(c)
            next_line = first_line - line_space*2
            indent = ((width-left_margin-right_margin)/3)*column
        #draw a box
        c.drawString(indent,next_line,teacher_section)
        next_line = next_line - (line_space)
        createSections(teacher_groups,teacher_questions,teacher_choices)

def xml(test_xml):
    xmldoc = minidom.parseString(test_xml)
    #xmldoc = xml
    test = xmldoc.firstChild
    global title, studentName, groups, questions, choices, id,teacherNode, teacher_groups, teacher_questions, teacher_choices, teacher_section
    teacherNode = None
    id = xmldoc.getElementsByTagName('id')[0].firstChild.nodeValue
    print id
    title = xmldoc.getElementsByTagName('title')[0].firstChild.data
    sections = xmldoc.getElementsByTagName('section')
    studentNode = sections[0]
    #do I need studentName? Should it be here?
    studentName = studentNode.getElementsByTagName('name')[0].firstChild.data
    if len(sections)>1:
        teacherNode = sections[1]
    
    
        #student = {{dict of groups:{dict of questions:[list of choices]}{}}
        groups = OrderedDict()
        groupsNodes = studentNode.getElementsByTagName('group')
        for group in groupsNodes:
            questions = OrderedDict()
            grouptemp = group.getElementsByTagName('text')[0].firstChild.wholeText
            questionNodes = group.getElementsByTagName('question')
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
            groups[grouptemp] = questions
            
        #teacher = {{dict of groups:{dict of essay questions:[list of point values]}{}}
        if teacherNode!=None:
            teacher_groups = OrderedDict()
            teacher_section = teacherNode.getElementsByTagName('name')[0].firstChild.data
            teacherGroupsNode = teacherNode.getElementsByTagName('group')
            for group in teacherGroupsNode:
                teacher_questions = OrderedDict()
                grouptemp = group.getElementsByTagName('text')[0].firstChild.wholeText
                teacher_questionNodes = group.getElementsByTagName('question')
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
                teacher_groups[grouptemp] = teacher_questions
        
            
        


def createBanding():
    global doc, questionnaire
    doc = minidom.Document()
    quexf = doc.createElement("queXF")
    doc.appendChild(quexf)
    questionnaire = doc.createElement("questionnaire")
    quexf.appendChild(questionnaire)
    
    idtag = doc.createElement("id")
    questionnaire.appendChild(idtag)
    idtext = doc.createTextNode(str(id))
    idtag.appendChild(idtext)
    
    sectiontag = doc.createElement("section")
    sectiontag.setAttribute("id","1")
    questionnaire.appendChild(sectiontag)
    label = doc.createElement("label")
    sectiontag.appendChild(label)
    labeltext = doc.createTextNode(studentName)
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
    
    
    
def questionBanding(group, question):
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
    labeltext = doc.createTextNode(group + " : " + question)
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
    #value = doc.createElement("value")
    boxlabel = doc.createElement("label")
    box.appendChild(boxlabel)
    boxlabeltext = doc.createTextNode(choice)
    boxlabel.appendChild(boxlabeltext)
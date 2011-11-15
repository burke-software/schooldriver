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

#settings required in settings_local.py: DB_USER, DB_PASS, QXF_DB

from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.barcode.common import *
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import getCodes, createBarcodeDrawing, getCodeNames, createBarcodeDrawing, createBarcodeImageInMemory
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from xml.dom import minidom
from orderedDict import OrderedDict
from tempfile import gettempdir
import MySQLdb
from django.conf import settings
from django.core.files import File
from omr.models import Test
from ecwsp.omr.queXF import import_queXF
from ecwsp.omr.models import *

def generate_xml(test_id):
    global entire_testtag
    from xml.dom import minidom
    test = Test.objects.get(id=test_id)
    

    def make_pdf(instance):
        global entire_testtag, id
        teacher_section_required = False
            
        doc = minidom.Document()
        testtag = doc.createElement("test")
        id = doc.createElement("id")
        testtag.appendChild(id)
        if instance:
            idtext = doc.createTextNode(str(instance.id))
        else:
            idtext = doc.createTextNode(str(test.id))
        id.setAttribute("testid",str(test.id))
        id.appendChild(idtext)
        titletag = doc.createElement("title")
        id.appendChild(titletag)
        titletext = doc.createTextNode(test.name)
        titletag.appendChild(titletext)        
        studentsection = doc.createElement("section")
        studentsection.setAttribute("type","student")
        id.appendChild(studentsection)
        studentnametag = doc.createElement("name")
        studentsection.appendChild(studentnametag)
        if instance:
            studentsection.setAttribute("studentid",str(instance.id))
            studentname = doc.createTextNode(str(instance.student.fname + " " + instance.student.lname))
            studentnametag.appendChild(studentname)
        else:
            studentsection.setAttribute("studentid","0")
            studentname = doc.createTextNode(" ")
            studentnametag.appendChild(studentname)
    
        questions = test.question_set.order_by('order')
        essays = []
            
        i = 1 # Question number for human use only
        priorType = None
        for q in questions:
            questiontag = doc.createElement("question")
            questiontag.setAttribute("varName",str(q.id))
            studentsection.appendChild(questiontag)
            question_number = doc.createElement("text")
            questiontag.appendChild(question_number)
            if q.type == "Essay":
                essays.append([q,q.id,i])
                teacher_section_required = True
                text = str(i) + ".  Essay Question"
            else:
                text = str(i) + ". "
                answers = []
                choices = q.answer_set.order_by('id')
                if q.type == "Multiple Choice":
                    ct=0
                    alphabet=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
                    for answer in choices:
                        answers.append((answer.id,str(alphabet[ct])))
                        ct=ct+1
                elif q.type == "True/False":
                    idlist = []
                    for answer in choices:
                        idlist.append(answer.id)
                    answers.append((idlist[0],"True"))
                    answers.append((idlist[1],"False"))
                    
                for answer_id, choice in answers:
                    choicetag = doc.createElement("choice")
                    questiontag.appendChild(choicetag)
                    choicetagtext = doc.createTextNode(str(choice))
                    choicetag.appendChild(choicetagtext)
                    choicevaluetag = doc.createElement("value")
                    choicevalue = doc.createTextNode(str(answer_id))
                    choicetag.appendChild(choicevaluetag)
                    choicevaluetag.appendChild(choicevalue)
                
            question_numbertext = doc.createTextNode(text)
            question_number.appendChild(question_numbertext)
            i=i+1
        if teacher_section_required:
            teachersection = doc.createElement("section")
            teachersection.setAttribute("type","teacher")
            id.appendChild(teachersection)
            teachertexttag = doc.createElement("name")
            teachersection.appendChild(teachertexttag)
            teachertext = doc.createTextNode("For Teacher Use Only")
            teachertexttag.appendChild(teachertext)
            for q,qid,number in essays:
                teacher_question = doc.createElement("question")
                teacher_question.setAttribute("varName",str(qid))
                teachersection.appendChild(teacher_question)
                teacher_question_number = doc.createElement("text")
                teacher_question.appendChild(teacher_question_number)
                teacher_question_numbertext = doc.createTextNode(str(number) + ". ")
                teacher_question_number.appendChild(teacher_question_numbertext)
                options = Answer.objects.filter(question=q)
                for choice in options:
                    choicetag = doc.createElement("choice")
                    teacher_question.appendChild(choicetag)
                    choicetagtext = doc.createTextNode(str(choice.point_value))
                    choicetag.appendChild(choicetagtext)
                    choicevaluetag = doc.createElement("value")
                    choicevalue = doc.createTextNode(str(choice.id))
                    choicetag.appendChild(choicevaluetag)
                    choicevaluetag.appendChild(choicevalue)
        
        entire_testtag.appendChild(id.cloneNode(True))

    entiredoc = minidom.Document()
    entire_testtag = entiredoc.createElement("test")
    entiredoc.appendChild(entire_testtag)
    make_pdf(False)
    first_pdf, first_pdf_location, first_banding = createpdf(entiredoc.toxml())
    
    pdfFile = File(open(first_pdf_location,'r'))
    bandFile = open(first_banding,'r')
    bandName = "banding_" + testid + ".xml"
    test.banding.save(bandName,File(bandFile))
    
    pdfName = "QueXF_Test_" + testid + ".pdf"
    test.queXF_pdf.save(pdfName,pdfFile)
    pdfFile.close()
    
    
    
    
    import_queXF(test.queXF_pdf.path, first_banding, test_id)
    
    entiredoc = minidom.Document()
    entire_testtag = entiredoc.createElement("test")
    
    entiredoc.appendChild(entire_testtag)
    instances = TestInstance.objects.filter(test=test.id)
    
    for instance in instances:
        make_pdf(instance)
        
    pdf, pdf_location, banding = createpdf(entiredoc.toxml())
    pdfFile = File(open(pdf_location,'r'))
    pdfName = "Answer_Sheets_Test_" + testid + ".pdf"
    test.answer_sheet_pdf.save(pdfName,pdfFile)
    pdfFile.close()
    
    test.finalized = True
    test.save()
    return pdf




def createpdf(xml_test):
    global page
    page = 1
    xml(xml_test)
    createBanding()
    pdf = "/test_" + testid + ".pdf"
    temp = gettempdir()
    temp_pdf_file = temp + pdf
    
    c = canvas.Canvas(temp_pdf_file, pagesize=letter)
    createTest(c)
    c.showPage()
    c.save()
    download = c.getpdfdata()
    if student_id[id]=="0":
        temp_banding_file = temp + "/banding.xml"
        banding = open(temp_banding_file, 'w')
        doc.writexml(banding)
        banding.close()
        return download, temp_pdf_file, temp_banding_file
        
    else:
        return download, temp_pdf_file, False
    
def newPage(c):
    global page
    c.translate(0,0)
    barcode(c)
    if student_id[id]!="0":
        student_barcode(c)
    drawLines(c)
    c.translate(left_margin,bottom_margin)
    
    pageBanding()
    page = page +1
    
def drawLines(c):
    #bottom left
    c.line(.5*inch,.5*inch,1.5*inch,.5*inch)
    c.line(.5*inch,.5*inch,.5*inch,1.5*inch)
    #bottom right
    c.line(width - .75*inch,.5*inch,width - 1.75*inch,.5*inch)
    c.line(width - .75*inch,.5*inch,width - .75*inch,1.5*inch)
    #top left
    c.line(.5*inch,height - .75*inch,1.25*inch,height - .75*inch)
    c.line(.5*inch,height - .75*inch,.5*inch,height - 1.5*inch)
    #top right
    c.line(width - .75*inch,height - .75*inch,width - 1.75*inch, height - .75*inch)
    c.line(width - .75*inch,height - .75*inch,width - .75*inch, height - 1.5*inch)
    
def barcode(c):
    global code
    code = str(testid).zfill(7) + (str(page).zfill(3))
    barcode = Codabar(code, barWidth = inch*0.028)
    x = width - (4.8*inch)
    y = height - (.6*inch)
    barcode.drawOn(c,x,y)
    
def student_barcode(c):
    global student_code
    #7 digits
    student_code = student_id[id].zfill(7)
    stopped_student_code = "A" + student_code + "A"
    student_barcode = Codabar(stopped_student_code,barWidth = inch*.03)
    x = left_margin - (.3*inch)
    y= height - (1.25*inch)
    student_barcode.drawOn(c,x,y)
    
def createTest(c):
    #need to do it for multiple tests -tests[id]:questions and -teacher_tests[id]:teacher_questions
    global indent, questions, choices, column, sort, next_line, width, height, next_line,left_margin,right_margin,bottom_margin,top_margin
    global id, var_names, teacher_varnames, page, title
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
    sort = 1
    test_count = 1
    for test, [questions, var_names] in tests.iteritems():
        page = 1
        id = test
        testBanding(test_count)
        test_count+=1
        newPage(c)
        c.setFont(default_font,font_size)
        
        title_length = title.__len__() * font_size
        #title_indent = width - indent - title_length*2 - right_margin
        #if title_indent < 250:
        #    title_indent = 250
        if title_length > 245:
            title = title[:245/font_size]
        c.drawString(250,first_line+10, title)
        next_line = first_line - (line_space)
        name_length = (names[id]).__len__() * font_size
        #name_indent = width - indent - name_length - right_margin
        #if name_indent <300:
        #    name_indent = 300
        if name_length > 295:
            name = names[id][:295/font_size]
        else: name = names[id]
        c.drawString(250,next_line+10,name)
        next_line = next_line - (line_space*2)
        
        def createSections(questions,choices, varnames):
            global indent, column, sort, next_line
            for question, varname in zip(questions,varnames.values()):
                if next_line + font_size <=0:
                    column +=1
                    if column == 3:
                        column=0
                        c.showPage()
                        newPage(c)
                        title_length = title.__len__() * font_size
                        c.drawString(width - right_margin - title_length,first_line+10, title)
                        next_line = first_line - (line_space)
                        name_length = (names[id]).__len__() * font_size
                        c.drawString(width - right_margin - name_length,next_line+10,names[id])
                        next_line = first_line - line_space*2
                    else:
                        next_line = first_line - line_space*3
                    indent = ((width-left_margin-right_margin)/3)*column
                choice_number = len(questions[question])
                if choice_number > 0:
                    next_line=next_line - line_space
                if choice_number ==2:
                    extra_indent=45
                elif choice_number <= 5:
                    extra_indent = 30
                else:
                    extra_indent = 25
                    
                c.drawString(indent,next_line,question)
                if choice_number !=0:
                    questionBanding(question,varname)
                sort+=1
                choice_indent = indent + extra_indent
                current_choice_count = 1
                for choice, value in questions[question]:
                    if current_choice_count != choice_number:
                        c.setDash([1,1,1,1],0)
                        c.setLineWidth(.5)
                        c.line(choice_indent+13,next_line+6.5,choice_indent+extra_indent,next_line+6.5)
                    c.drawString(choice_indent,next_line+line_space,str(choice))
                    c.setDash()
                    c.setLineWidth(.5)
                    c.rect(choice_indent,next_line,13,13,fill=0)
                    choiceBanding(choice_indent+.5,next_line+13,choice_indent+13,next_line+.5,choice,value)
                    choice_indent+=extra_indent
                    current_choice_count+=1
                next_line = next_line - line_space
    
    
    
        createSections(questions,choices,var_names)
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
            c.drawString(indent,next_line,teacher_section)
            beginy = next_line+line_space
            
            c.line(indent,beginy,140+indent,beginy)
            next_line = next_line - (line_space)
            [teacher_questions,teacher_varnames] = teacher_tests[test]
            createSections(teacher_questions,teacher_choices,teacher_varnames)
            

        if ct < tests.__len__():
            column = 0
            indent = 0
            page = 1
            c.showPage()
        ct+=1

def xml(test_xml):
    global tests, teacher_tests, var_names,teacher_varnames, student_id,testid
    global title, names, questions, choices, id,teacher_questions, teacher_choices, teacher_section
    xmldoc = minidom.parseString(test_xml)
    test = xmldoc.firstChild
    global teacherNode
    teacherNode = None
    ids = xmldoc.getElementsByTagName('id')
    testid = ids[0].getAttribute('testid')
    teacher_tests = OrderedDict()
    tests = OrderedDict()
    names = OrderedDict()
    student_id = OrderedDict()
    #put student_names in a dict to match tests
    for singleid in ids:
        id = singleid.firstChild.nodeValue
        title = singleid.getElementsByTagName('title')[0].firstChild.data
        sections = singleid.getElementsByTagName('section')
        studentNode = sections[0]
        names[id] = studentNode.getElementsByTagName('name')[0].firstChild.data
        student_id[id] = studentNode.getAttribute("studentid")
        if len(sections)>1:
            teacherNode = sections[1]
        #student = {dict of tests:{dict of questions:[list of choices]}{}}
        questions = OrderedDict()
        var_names = OrderedDict()
        questionNodes = studentNode.getElementsByTagName('question')
        for question in questionNodes:
            questiontemp = question.getElementsByTagName('text')[0].firstChild.wholeText
            varname = question.getAttribute('varName')
            choicesNodes = question.getElementsByTagName('choice')
            choices = []
            for choice in choicesNodes:
                choicetemp = choice.firstChild.data
                value = choice.getElementsByTagName('value')[0].firstChild.wholeText
                choices.append((choicetemp,value))
            counter = 0
            temp = questiontemp
            while temp in questions:
                counter = counter +1
                temp = questiontemp + `counter` + '.'
            if counter != 0:
                questiontemp += `counter` + '.'
            questions[questiontemp] = choices
            var_names[questiontemp] = varname
        
        tests[id] = [questions,var_names]
            
        #teacher = {{dict of essay questions:[list of point values]}{}}
        if teacherNode!=None:
            teacher_section = teacherNode.getElementsByTagName('name')[0].firstChild.data
            teacher_questions = OrderedDict()
            teacher_varnames = OrderedDict()
            teacher_questionNodes = teacherNode.getElementsByTagName('question')
            for teacher_question in teacher_questionNodes:
                questiontemp = teacher_question.getElementsByTagName('text')[0].firstChild.wholeText
                varname = teacher_question.getAttribute('varName')
                choicesNodes = teacher_question.getElementsByTagName('choice')
                teacher_choices = []
                for choice in choicesNodes:
                    choicetemp = choice.firstChild.data
                    value = choice.getElementsByTagName('value')[0].firstChild.wholeText
                    teacher_choices.append((choicetemp,value))
                counter = 0
                temp = questiontemp
                while temp in teacher_questions:
                    counter = counter +1
                    temp = questiontemp + `counter` + '.'
                if counter != 0:
                    questiontemp += `counter` + '.'
                teacher_questions[questiontemp] = teacher_choices
                teacher_varnames[questiontemp] = varname
            
            teacher_tests[id] = [teacher_questions,teacher_varnames]

def createBanding():
    global doc, questionnaire
    doc = minidom.Document()
    quexf = doc.createElement("queXF")
    doc.appendChild(quexf)
    questionnaire = doc.createElement("questionnaire")
    quexf.appendChild(questionnaire)

def testBanding(number):
    global doc, questionnaire
    
    sectiontag = doc.createElement("section")
    sectiontag.setAttribute("id",str(number))
    questionnaire.appendChild(sectiontag)
    titletag = doc.createElement("title")
    sectiontag.appendChild(titletag)
    titletext = doc.createTextNode(" ")
    titletag.appendChild(titletext)
    label = doc.createElement("label")
    sectiontag.appendChild(label)
    labeltext = doc.createTextNode(str(names[id]))
    label.appendChild(labeltext)
    
def pageBanding():
    global pagetag, page
    pagetag = doc.createElement("page")
    questionnaire.appendChild(pagetag)
    pgidtag = doc.createElement("id")
    pagetag.appendChild(pgidtag)
    pgidtext = doc.createTextNode(str(code))
    pgidtag.appendChild(pgidtext)
    
    rotationtag = doc.createElement("rotation")
    pagetag.appendChild(rotationtag)
    rotationText = doc.createTextNode("0")
    rotationtag.appendChild(rotationText)
    if student_id[id]=="0":
        barcodeBoxgroup()
    
    
def barcodeBanding():
    #doesn't work - inquiry is into QueXF
    boxgroup = doc.createElement("boxgroup")
    pagetag.appendChild(boxgroup)
    typetag = doc.createElement("type")
    boxgroup.appendChild(typetag)
    typetext = doc.createTextNode("5")
    typetag.appendChild(typetext)
    widthtag = doc.createElement("width")
    boxgroup.appendChild(widthtag)
    widthtext = doc.createTextNode("7")
    widthtag.appendChild(widthtext)
    varnametag = doc.createElement("varname")
    boxgroup.appendChild(varnametag)
    varnametext = doc.createTextNode("barcode_boxgroup")
    varnametag.appendChild(varnametext)
    sorttag = doc.createElement("sortorder")
    boxgroup.appendChild(sorttag)
    sorttext = doc.createTextNode("0")
    sorttag.appendChild(sorttext)
    label_barcode = doc.createElement("label")
    boxgroup.appendChild(label_barcode)
    #labeltext = doc.createTextNode(str(question))
    #label2.appendChild(labeltext)
    groupsectiontag = doc.createElement("groupsection")
    #groupsectiontag.setAttribute("idref","1")
    boxgroup.appendChild(groupsectiontag)
    
    
    topx = (.04*inch + left_margin) *300/72
    topy = (.4*inch) *300/72    
    botx = (2.4*inch + left_margin) *300/72
    boty = (.6*inch) *300/72
    box = doc.createElement("box")
    boxgroup.appendChild(box)
    boxid = doc.createElement("id")
    boxidtext = doc.createTextNode(str(page)) #will be student id
    box.appendChild(boxid)
    boxid.appendChild(boxidtext)
    
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
    valuetag = doc.createElement("value")
    box.appendChild(valuetag)
    #valuetext = doc.createTextNode("barcode")
    #valuetag.appendChild(valuetext)
    boxlabel = doc.createElement("label")
    box.appendChild(boxlabel)
    
def barcodeBoxgroup():
    """hacks on QueXF's database to insert the banding for the student barcode into the database
    """
    db = MySQLdb.Connect(user=settings.DB_USER, passwd=settings.DB_PASS,db=settings.QXF_DB)
    db_cursor = db.cursor()
    db_cursor.execute("SET @questionnaire_id =(SELECT qid from questionnaires where description = " + str(testid) + ")")
    db_cursor.execute("SET @pageid = (SELECT pid from pages were qid = @questionnaire_id order by pid DESC limit 1)")
    #if page ==1:
    #    db_cursor.execute("SET @pageid = (SELECT IFNULL(@page_id,0) + 1)")
        
    db_cursor.execute("INSERT INTO boxgroupstype (btid,width,pid,varname,sortorder) values (5,7,@pageid,'barcode_@pageid',0)")
    db_cursor.execute("INSERT INTO boxes (tlx,tly,brx,bry,pid,bgid,value)" +
                      " values (210, 185, 1175, 450, @pageid,LAST_INSERT_ID(),"+
                      str(student_id[id]) + ")")
    db.commit()
    db.close()    
    
def questionBanding(question, variable_name):
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
    varnametag = doc.createElement("varname")
    boxgroup.appendChild(varnametag)
    varnametext = doc.createTextNode(str(variable_name))
    varnametag.appendChild(varnametext)
    sorttag = doc.createElement("sortorder")
    boxgroup.appendChild(sorttag)
    sorttext = doc.createTextNode(str(sort))
    sorttag.appendChild(sorttext)
    label2 = doc.createElement("label")
    boxgroup.appendChild(label2)
    labeltext = doc.createTextNode(str(question))
    label2.appendChild(labeltext)
    groupsectiontag = doc.createElement("groupsection")
    groupsectiontag.setAttribute("idref","1")
    boxgroup.appendChild(groupsectiontag)
        
def choiceBanding(topx,topy,botx,boty,choice,value):
    topx = round((topx+inch)*300/72)
    botx = round((botx+inch)*300/72)
    topy = round((height - topy-top_margin)*300/72)
    boty = round((height - boty-top_margin)*300/72)
    box = doc.createElement("box")
    boxgroup.appendChild(box)
    boxid = doc.createElement("id")
    boxidtext = doc.createTextNode(str(value))
    box.appendChild(boxid)
    boxid.appendChild(boxidtext)
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
    valuetag = doc.createElement("value")
    box.appendChild(valuetag)
    valuetext = doc.createTextNode(str(value))
    valuetag.appendChild(valuetext)
    boxlabel = doc.createElement("label")
    box.appendChild(boxlabel)
    boxlabeltext = doc.createTextNode(str(choice))
    boxlabel.appendChild(boxlabeltext)

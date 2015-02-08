from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
import sys
from ecwsp.administration.models import *

def student_thumbnail(request, year):
    from ecwsp.sis.models import Student
    
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' % "thumbnails.pdf"
    
    c = canvas.Canvas(response, pagesize=letter)  
    
    students = Student.objects.filter(year=year, is_active=True).order_by('last_name', 'first_name')
    xsize = 6*cm
    ysize = 4.5*cm
    dx = .7*cm + xsize    #space between each pic
    dy = 2*cm + ysize
    x = 1*cm            # starting locations
    y = 1*cm
    xn = 0                # counters
    yn = 0
    paper_height = 23*cm
    for stu in students:
        try:    
            if stu.pic:
                c.drawImage(unicode(settings.MEDIA_ROOT[:-7] + unicode(stu.pic.url_530x400)), x, paper_height - (y-.4*cm), xsize, ysize, preserveAspectRatio=True)
            else:
                c.drawString(x, paper_height - (y+.5*cm), "No Image")
            c.drawString(x, paper_height - y, unicode(stu))
            if xn < 2:
                x += dx
                xn += 1
            else:
                x = 1*cm
                xn = 0
                if yn < 3:
                    y += dy
                    yn += 1
                else:
                    y = 1*cm
                    yn = 0
                    c.showPage()  
        except:
            print >> sys.stderr, str(sys.exc_info()[0])
    c.showPage()  
    c.save()
    return response

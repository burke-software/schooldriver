from django.contrib.auth.decorators import permission_required
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse

from ecwsp.alumni.forms import AlumniNoteForm

@permission_required('alumni.add_alumninote')
def ajax_quick_add_note(request, student_id=None):
    if request.POST:
        form = AlumniNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            note_html = '<h4>%s - %s - %s </h4>%s' % (note.category, note.user, note.date, note.note)
            return HttpResponse(note_html)
        else:
            return HttpResponse('FAIL')
    else:
        form = AlumniNoteForm(initial={'alumni':student_id})
        return HttpResponse(form);
    
@permission_required('alumni.change_alumni')
def import_clearinghouse(request):
    from ecwsp.sis.forms import UploadFileForm
    msg = 'Import a alumni data file from Student Clearinghouse'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            from ecwsp.sis.importer import Importer
            importer = Importer(file=form.cleaned_data['file'], user=request.user)
            msg, filename = importer.import_just_alumni_data()
            msg += '<br/><a href="/media/import_error.xls">Download Errors</a>'
    else:
        form = UploadFileForm()
    msg = mark_safe(msg)
    return render(request, 'sis/generic_form.html', {'form':form, 'msg':msg}, )

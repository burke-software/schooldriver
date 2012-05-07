from django.contrib.auth.decorators import permission_required
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
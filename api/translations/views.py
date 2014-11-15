from rest_framework import viewsets
from rest_framework.response import Response
import polib

class TranslationViewSet(viewsets.ViewSet):
    def list(self, request):
        lang = self.request.QUERY_PARAMS.get('lang', None)
        if lang is not None:
            try:
                po_file_path = "ecwsp/admissions/locale/%s/LC_MESSAGES/django.po" % lang
                po = polib.pofile(po_file_path)
                data = {}
                for entry in po:
                    data[entry.msgid] = entry.msgstr
                return Response(data)
            except Exception as e:
                return Response({"error": str(e)}, 500)
        else:
            return Response(
                {"error": "need to specify a language with ?lang="}, 400
                )
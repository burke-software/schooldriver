from rest_framework import viewsets
from rest_framework.response import Response
from api.translations.sync import SyncApplicationTranslationFile
from rest_framework.permissions import IsAdminUser
import polib

class AdmissionsTranslationViewSet(viewsets.ViewSet):
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

class AdmissionsTranslationSync(viewsets.ViewSet):
    """ sync the application data with the admissions' .po file,
    useful after copy changes or additions to the application template or
    application custom fields """

    permission_classes = (IsAdminUser,)

    def list(self, request):
        try:
            new_app_sync = SyncApplicationTranslationFile()
            new_app_sync.sync()
        except Exception as e:
            return Response({"error": str(e)}, 500)
        else:
            return Response({"success" : "successful application translation sync"})

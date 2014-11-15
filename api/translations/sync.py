import polib
import json
from ecwsp.admissions.models import ApplicantCustomField, StudentApplicationTemplate

class SyncApplicationTranslationFile:
    """ sync the admissions .po file to reflect changes in application
    templates or custom fields that the user has modified """

    po_file_path = "ecwsp/admissions/locale/es/LC_MESSAGES/django.po"
    translation_entries = polib.pofile(po_file_path)

    def sync(self):
        self.update_custom_field_translations()
        self.update_application_template_translations()
        self.translation_entries.save()

    def update_application_template_translations(self):
        """update translations entries for application templates"""
        for application_template in StudentApplicationTemplate.objects.all():
            json_template = json.loads(application_template.json_template)
            for section in json_template['sections']: 
                self.create_or_update_entry(
                    entry_type = 'application_section_name', 
                    entry_id = section["id"], 
                    entry_text = section["name"]
                    )
                if 'help_text' in section:
                    self.create_or_update_entry(
                        entry_type = 'application_section_help_text', 
                        entry_id = section["id"], 
                        entry_text = section["help_text"]
                        )

    def update_custom_field_translations(self):
        for custom_field in ApplicantCustomField.objects.all():
            self.create_or_update_entry(
                entry_type = "application_custom_field", 
                entry_id = custom_field.id,
                entry_text = custom_field.field_label,
                )
            if custom_field.helptext:
                self.create_or_update_entry(
                    entry_type = "application_custom_field_helptext", 
                    entry_id = custom_field.id,
                    entry_text = custom_field.helptext,
                    )

    def create_or_update_entry(self, entry_type, entry_id, entry_text):
        entry = self.get_entry_by_type_and_id(entry_type, entry_id)
        if entry is None:
            self.create_new_entry(entry_type, entry_id, entry_text)
        else:
            entry.msgid = entry_text


    def get_entry_by_type_and_id(self, entry_type, entry_id):
        existing_entry = None
        for entry in self.translation_entries:
            if existing_entry is None:
                for occurrence in entry.occurrences:
                    if occurrence[0] == unicode(entry_type) and occurrence[1] == unicode(entry_id):
                        existing_entry = entry
        return existing_entry

    def create_new_entry(self, entry_type, entry_id, entry_text):
        """create a blank entry, translate it yourself using Rosetta"""
        new_entry = polib.POEntry(
            msgid = unicode(entry_text),
            msgstr = "",
            occurrences = [(unicode(entry_type), unicode(entry_id))]
        )
        self.translation_entries.append(new_entry)




import polib
import json
from ecwsp.admissions.models import ApplicantCustomField, StudentApplicationTemplate

class SyncApplicationTranslationFile:
    """ sync the admissions .po file to reflect changes in application
    templates or custom fields that the user has modified """
    def __init__(self):
        self.po_file_path = "ecwsp/admissions/locale/es/LC_MESSAGES/django.po"
        self.translation_entries = polib.pofile(self.po_file_path)

    def sync(self):
        self.update_custom_field_translations()
        self.update_application_template_translations()
        self.translation_entries.save()

    def update_application_template_translations(self):
        """update translations entries for application templates"""
        for application_template in StudentApplicationTemplate.objects.all():
            json_template = json.loads(application_template.json_template)
            for section in json_template['sections']: 
                self.update_entry(
                    entry_type = 'application_section_name', 
                    entry_id = section["id"], 
                    entry_text = section["name"]
                    )
                if 'help_text' in section:
                    self.update_entry(
                        entry_type = 'application_section_help_text', 
                        entry_id = section["id"], 
                        entry_text = section["help_text"]
                        )

    def update_custom_field_translations(self):
        for custom_field in ApplicantCustomField.objects.all():
            self.update_entry(
                entry_type = "application_custom_field", 
                entry_id = custom_field.id,
                entry_text = custom_field.field_label,
                )
            if custom_field.helptext:
                self.update_entry(
                    entry_type = "application_custom_field_helptext", 
                    entry_id = custom_field.id,
                    entry_text = custom_field.helptext,
                    )
            if custom_field.field_choices:
                self.update_custom_field_choice_translations(custom_field)

    def get_list_of_string_choices_from_custom_field(self, custom_field):
        """ choices will either be comma delimated or {(foo, bar)} objects,
        depending on whether it is integraed with the Applicant model """
        choices = []
        if custom_field.is_field_integrated_with_applicant:
            # need to implement this - problem parsing the field_choices string here...
            choices = choices
        elif custom_field.field_choices != '':
            choices = custom_field.field_choices.split(',')
        return choices

    def update_custom_field_choice_translations(self, custom_field):
        choices = self.get_list_of_string_choices_from_custom_field(custom_field)
        for choice in choices:
            self.update_entry(
                entry_type = "application_custom_field_choice", 
                entry_id = custom_field.id,
                entry_text = choice,
            )

    def update_entry(self, entry_type, entry_id, entry_text):
        entry = self.get_entry_by_text(entry_text)
        if entry is None:
            self.create_new_entry(entry_type, entry_id, entry_text)

    def get_entry_by_text(self, entry_text):
        existing_entry = None
        for entry in self.translation_entries:
            if entry.msgid == unicode(entry_text):
                existing_entry = entry
                break
        return existing_entry

    def create_new_entry(self, entry_type, entry_id, entry_text):
        """create a blank entry, translate it yourself using Rosetta"""
        new_entry = polib.POEntry(
            msgid = unicode(entry_text),
            msgstr = "",
            occurrences = [(unicode(entry_type), unicode(entry_id))]
        )
        self.translation_entries.append(new_entry)




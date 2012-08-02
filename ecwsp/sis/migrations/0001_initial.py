# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    needed_by = (
        ("schedule", "0001_initial"),
        ("volunteer_track", "0001_initial"),
    )
    def forwards(self, orm):
        # Adding model 'UserPreference'
        db.create_table('sis_userpreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefered_file_format', self.gf('django.db.models.fields.CharField')(default='o', max_length='1')),
            ('include_deleted_students', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('omr_default_point_value', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('omr_default_save_question_to_bank', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('omr_default_number_answers', self.gf('django.db.models.fields.IntegerField')(default=2, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('sis', ['UserPreference'])

        # Adding M2M table for field additional_report_fields on 'UserPreference'
        db.create_table('sis_userpreference_additional_report_fields', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userpreference', models.ForeignKey(orm['sis.userpreference'], null=False)),
            ('reportfield', models.ForeignKey(orm['sis.reportfield'], null=False))
        ))
        db.create_unique('sis_userpreference_additional_report_fields', ['userpreference_id', 'reportfield_id'])

        # Adding model 'ReportField'
        db.create_table('sis_reportfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('sis', ['ReportField'])

        # Adding model 'MdlUser'
        db.create_table('sis_mdluser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=360, blank=True)),
        ))
        db.send_create_signal('sis', ['MdlUser'])

        # Adding model 'EmergencyContact'
        db.create_table('sis_emergencycontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('relationship_to_student', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, null=True, blank=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('primary_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('emergency_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['EmergencyContact'])

        # Adding model 'EmergencyContactNumber'
        db.create_table('sis_emergencycontactnumber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.EmergencyContact'])),
        ))
        db.send_create_signal('sis', ['EmergencyContactNumber'])

        # Adding model 'Faculty'
        db.create_table('sis_faculty', (
            ('mdluser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.MdlUser'], unique=True, primary_key=True)),
            ('alt_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, blank=True)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['Faculty'])

        # Adding model 'Cohort'
        db.create_table('sis_cohort', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('sis', ['Cohort'])

        # Adding M2M table for field students on 'Cohort'
        db.create_table('sis_studentcohort', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cohort', models.ForeignKey(orm['sis.cohort'], null=False)),
            ('student', models.ForeignKey(orm['sis.student'], null=False))
        ))
        db.create_unique('sis_studentcohort', ['cohort_id', 'student_id'])

        # Adding model 'ReasonLeft'
        db.create_table('sis_reasonleft', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('sis', ['ReasonLeft'])

        # Adding model 'GradeLevel'
        db.create_table('sis_gradelevel', (
            ('id', self.gf('django.db.models.fields.IntegerField')(unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
        ))
        db.send_create_signal('sis', ['GradeLevel'])

        # Adding model 'LanguageChoice'
        db.create_table('sis_languagechoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['LanguageChoice'])

        # Adding model 'Student'
        db.create_table('sis_student', (
            ('mdluser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.MdlUser'], unique=True, primary_key=True)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('grad_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('pic', self.gf('ecwsp.sis.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((70, 65), (530, 400)))),
            ('alert', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('bday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
            ('date_dismissed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reason_left', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.ReasonLeft'], null=True, blank=True)),
            ('unique_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=11, null=True, blank=True)),
            ('parent_guardian', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('parent_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('family_preferred_language', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['sis.LanguageChoice'], null=True, blank=True)),
            ('alt_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cache_cohort', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cache_cohorts', null=True, on_delete=models.SET_NULL, to=orm['sis.Cohort'])),
            ('individual_education_program', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cache_gpa', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('sis', ['Student'])

        # Adding M2M table for field emergency_contacts on 'Student'
        db.create_table('sis_student_emergency_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm['sis.student'], null=False)),
            ('emergencycontact', models.ForeignKey(orm['sis.emergencycontact'], null=False))
        ))
        db.create_unique('sis_student_emergency_contacts', ['student_id', 'emergencycontact_id'])

        # Adding M2M table for field siblings on 'Student'
        db.create_table('sis_student_siblings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_student', models.ForeignKey(orm['sis.student'], null=False)),
            ('to_student', models.ForeignKey(orm['sis.student'], null=False))
        ))
        db.create_unique('sis_student_siblings', ['from_student_id', 'to_student_id'])

        # Adding model 'ASPHistory'
        db.create_table('sis_asphistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('asp', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('enroll', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['ASPHistory'])

        # Adding model 'TranscriptNoteChoices'
        db.create_table('sis_transcriptnotechoices', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sis', ['TranscriptNoteChoices'])

        # Adding model 'TranscriptNote'
        db.create_table('sis_transcriptnote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('predefined_note', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.TranscriptNoteChoices'], null=True, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
        ))
        db.send_create_signal('sis', ['TranscriptNote'])

        # Adding model 'StudentNumber'
        db.create_table('sis_studentnumber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'], null=True, blank=True)),
        ))
        db.send_create_signal('sis', ['StudentNumber'])

        # Adding model 'StudentFile'
        db.create_table('sis_studentfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
        ))
        db.send_create_signal('sis', ['StudentFile'])

        # Adding model 'StudentHealthRecord'
        db.create_table('sis_studenthealthrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('record', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sis', ['StudentHealthRecord'])

        # Adding model 'SchoolYear'
        db.create_table('sis_schoolyear', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('grad_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('active_year', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('benchmark_grade', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['SchoolYear'])

        # Adding model 'ImportLog'
        db.create_table('sis_importlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('import_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('sql_backup', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('user_note', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('errors', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sis', ['ImportLog'])

        # Adding model 'MessageToStudent'
        db.create_table('sis_messagetostudent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('ckeditor.fields.RichTextField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('derp', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal('sis', ['MessageToStudent'])


    def backwards(self, orm):
        # Deleting model 'UserPreference'
        db.delete_table('sis_userpreference')

        # Removing M2M table for field additional_report_fields on 'UserPreference'
        db.delete_table('sis_userpreference_additional_report_fields')

        # Deleting model 'ReportField'
        db.delete_table('sis_reportfield')

        # Deleting model 'MdlUser'
        db.delete_table('sis_mdluser')

        # Deleting model 'EmergencyContact'
        db.delete_table('sis_emergencycontact')

        # Deleting model 'EmergencyContactNumber'
        db.delete_table('sis_emergencycontactnumber')

        # Deleting model 'Faculty'
        db.delete_table('sis_faculty')

        # Deleting model 'Cohort'
        db.delete_table('sis_cohort')

        # Removing M2M table for field students on 'Cohort'
        db.delete_table('sis_studentcohort')

        # Deleting model 'ReasonLeft'
        db.delete_table('sis_reasonleft')

        # Deleting model 'GradeLevel'
        db.delete_table('sis_gradelevel')

        # Deleting model 'LanguageChoice'
        db.delete_table('sis_languagechoice')

        # Deleting model 'Student'
        db.delete_table('sis_student')

        # Removing M2M table for field emergency_contacts on 'Student'
        db.delete_table('sis_student_emergency_contacts')

        # Removing M2M table for field siblings on 'Student'
        db.delete_table('sis_student_siblings')

        # Deleting model 'ASPHistory'
        db.delete_table('sis_asphistory')

        # Deleting model 'TranscriptNoteChoices'
        db.delete_table('sis_transcriptnotechoices')

        # Deleting model 'TranscriptNote'
        db.delete_table('sis_transcriptnote')

        # Deleting model 'StudentNumber'
        db.delete_table('sis_studentnumber')

        # Deleting model 'StudentFile'
        db.delete_table('sis_studentfile')

        # Deleting model 'StudentHealthRecord'
        db.delete_table('sis_studenthealthrecord')

        # Deleting model 'SchoolYear'
        db.delete_table('sis_schoolyear')

        # Deleting model 'ImportLog'
        db.delete_table('sis_importlog')

        # Deleting model 'MessageToStudent'
        db.delete_table('sis_messagetostudent')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sis.asphistory': {
            'Meta': {'object_name': 'ASPHistory'},
            'asp': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'enroll': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'sis.cohort': {
            'Meta': {'object_name': 'Cohort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Student']", 'null': 'True', 'db_table': "'sis_studentcohort'", 'blank': 'True'})
        },
        'sis.emergencycontact': {
            'Meta': {'ordering': "('primary_contact', 'emergency_only', 'lname')", 'object_name': 'EmergencyContact'},
            'city': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emergency_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'sis.emergencycontactnumber': {
            'Meta': {'object_name': 'EmergencyContactNumber'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.EmergencyContact']"}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'})
        },
        'sis.faculty': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Faculty', '_ormbases': ['sis.MdlUser']},
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        'sis.importlog': {
            'Meta': {'object_name': 'ImportLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'errors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sql_backup': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_note': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'sis.languagechoice': {
            'Meta': {'object_name': 'LanguageChoice'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.mdluser': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'MdlUser'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.messagetostudent': {
            'Meta': {'object_name': 'MessageToStudent'},
            'derp': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('ckeditor.fields.RichTextField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        },
        'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.reportfield': {
            'Meta': {'object_name': 'ReportField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.schoolyear': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'SchoolYear'},
            'active_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'sis.student': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Student', '_ormbases': ['sis.MdlUser']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['sis.Cohort']"}),
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Cohort']", 'symmetrical': 'False', 'through': "orm['sis.StudentCohort']", 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'parent_guardian': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pic': ('ecwsp.sis.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((70, 65), (530, 400))'}),
            'reason_left': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.ReasonLeft']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'sis.studentcohort': {
            'Meta': {'object_name': 'StudentCohort', 'managed': 'False'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Cohort']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'sis.studentfile': {
            'Meta': {'object_name': 'StudentFile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'sis.studenthealthrecord': {
            'Meta': {'object_name': 'StudentHealthRecord'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.TextField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'sis.studentnumber': {
            'Meta': {'object_name': 'StudentNumber'},
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'})
        },
        'sis.transcriptnote': {
            'Meta': {'object_name': 'TranscriptNote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'predefined_note': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.TranscriptNoteChoices']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'sis.transcriptnotechoices': {
            'Meta': {'object_name': 'TranscriptNoteChoices'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {})
        },
        'sis.userpreference': {
            'Meta': {'object_name': 'UserPreference'},
            'additional_report_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.ReportField']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_deleted_students': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'omr_default_number_answers': ('django.db.models.fields.IntegerField', [], {'default': '2', 'blank': 'True'}),
            'omr_default_point_value': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'omr_default_save_question_to_bank': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'prefered_file_format': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': "'1'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['sis']

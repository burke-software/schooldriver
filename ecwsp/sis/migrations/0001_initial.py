# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
	('administration','0001_initial'),
    )	
    def forwards(self, orm):
        # Adding model 'UserPreference'
        db.create_table(u'sis_userpreference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefered_file_format', self.gf('django.db.models.fields.CharField')(default='o', max_length='1')),
            ('include_deleted_students', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('course_sort', self.gf('django.db.models.fields.CharField')(default='department', max_length=64)),
            ('omr_default_point_value', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('omr_default_save_question_to_bank', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('omr_default_number_answers', self.gf('django.db.models.fields.IntegerField')(default=2, blank=True)),
            ('gradebook_preference', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal(u'sis', ['UserPreference'])

        # Adding M2M table for field additional_report_fields on 'UserPreference'
        db.create_table(u'sis_userpreference_additional_report_fields', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userpreference', models.ForeignKey(orm[u'sis.userpreference'], null=False)),
            ('reportfield', models.ForeignKey(orm[u'sis.reportfield'], null=False))
        ))
        db.create_unique(u'sis_userpreference_additional_report_fields', ['userpreference_id', 'reportfield_id'])

        # Adding model 'ReportField'
        db.create_table(u'sis_reportfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'sis', ['ReportField'])

        # Adding model 'MdlUser'
        db.create_table(u'sis_mdluser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=360, blank=True)),
        ))
        db.send_create_signal(u'sis', ['MdlUser'])

        # Adding model 'EmergencyContact'
        db.create_table(u'sis_emergencycontact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('relationship_to_student', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, null=True, blank=True)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('primary_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('emergency_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sync_schoolreach', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'sis', ['EmergencyContact'])

        # Adding model 'EmergencyContactNumber'
        db.create_table(u'sis_emergencycontactnumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.EmergencyContact'])),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['EmergencyContactNumber'])

        # Adding model 'Faculty'
        db.create_table(u'sis_faculty', (
            (u'mdluser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.MdlUser'], unique=True, primary_key=True)),
            ('alt_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('number', self.gf('localflavor.us.models.PhoneNumberField')(max_length=20, blank=True)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['Faculty'])

        # Adding model 'Cohort'
        db.create_table(u'sis_cohort', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['Cohort'])

        # Adding model 'PerCourseCohort'
        db.create_table(u'sis_percoursecohort', (
            (u'cohort_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.Cohort'], unique=True, primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
        ))
        db.send_create_signal(u'sis', ['PerCourseCohort'])

        # Adding model 'ReasonLeft'
        db.create_table(u'sis_reasonleft', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'sis', ['ReasonLeft'])

        # Adding model 'GradeLevel'
        db.create_table(u'sis_gradelevel', (
            ('id', self.gf('django.db.models.fields.IntegerField')(unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
        ))
        db.send_create_signal(u'sis', ['GradeLevel'])

        # Adding model 'LanguageChoice'
        db.create_table(u'sis_languagechoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['LanguageChoice'])

        # Adding model 'ClassYear'
        db.create_table(u'sis_classyear', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('ecwsp.sis.models.IntegerRangeField')(unique=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'sis', ['ClassYear'])

        # Adding model 'Student'
        db.create_table(u'sis_student', (
            (u'mdluser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.MdlUser'], unique=True, primary_key=True)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('grad_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('pic', self.gf('ecwsp.sis.thumbs.ImageWithThumbsField')(blank=True, max_length=100, null=True, sizes=((70, 65), (530, 400)))),
            ('alert', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('bday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('class_of_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.ClassYear'], null=True, blank=True)),
            ('date_dismissed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reason_left', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.ReasonLeft'], null=True, blank=True)),
            ('unique_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=11, null=True, blank=True)),
            ('parent_guardian', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('parent_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('family_preferred_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.LanguageChoice'], null=True, blank=True)),
            ('alt_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cache_cohort', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cache_cohorts', null=True, on_delete=models.SET_NULL, to=orm['sis.Cohort'])),
            ('individual_education_program', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cache_gpa', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'sis', ['Student'])

        # Adding M2M table for field emergency_contacts on 'Student'
        db.create_table(u'sis_student_emergency_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm[u'sis.student'], null=False)),
            ('emergencycontact', models.ForeignKey(orm[u'sis.emergencycontact'], null=False))
        ))
        db.create_unique(u'sis_student_emergency_contacts', ['student_id', 'emergencycontact_id'])

        # Adding M2M table for field siblings on 'Student'
        db.create_table(u'sis_student_siblings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_student', models.ForeignKey(orm[u'sis.student'], null=False)),
            ('to_student', models.ForeignKey(orm[u'sis.student'], null=False))
        ))
        db.create_unique(u'sis_student_siblings', ['from_student_id', 'to_student_id'])

        # Adding model 'ASPHistory'
        db.create_table(u'sis_asphistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('asp', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('enroll', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['ASPHistory'])

        # Adding model 'StudentCohort'
        db.create_table(u'sis_studentcohort', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('cohort', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Cohort'])),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['StudentCohort'])

        # Adding model 'TranscriptNoteChoices'
        db.create_table(u'sis_transcriptnotechoices', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'sis', ['TranscriptNoteChoices'])

        # Adding model 'TranscriptNote'
        db.create_table(u'sis_transcriptnote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('predefined_note', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.TranscriptNoteChoices'], null=True, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
        ))
        db.send_create_signal(u'sis', ['TranscriptNote'])

        # Adding model 'StudentNumber'
        db.create_table(u'sis_studentnumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('ext', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'], null=True, blank=True)),
        ))
        db.send_create_signal(u'sis', ['StudentNumber'])

        # Adding model 'StudentFile'
        db.create_table(u'sis_studentfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
        ))
        db.send_create_signal(u'sis', ['StudentFile'])

        # Adding model 'StudentHealthRecord'
        db.create_table(u'sis_studenthealthrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('record', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'sis', ['StudentHealthRecord'])

        # Adding model 'SchoolYear'
        db.create_table(u'sis_schoolyear', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('grad_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('active_year', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('benchmark_grade', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['SchoolYear'])

        # Adding model 'ImportLog'
        db.create_table(u'sis_importlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('import_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('sql_backup', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('user_note', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('errors', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'sis', ['ImportLog'])

        # Adding model 'MessageToStudent'
        db.create_table(u'sis_messagetostudent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('ckeditor.fields.RichTextField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal(u'sis', ['MessageToStudent'])
        
        # Create proxy model's m2m table
        db.execute('CREATE TABLE `sis_student_family_access_users` ('
            '`id` integer NOT NULL PRIMARY KEY, '
            '`student_id` integer NOT NULL, '
            '`familyaccessuser_id` integer NOT NULL, '
            'UNIQUE (`student_id`, `familyaccessuser_id`));');


    def backwards(self, orm):
        # Deleting model 'UserPreference'
        db.delete_table(u'sis_userpreference')

        # Removing M2M table for field additional_report_fields on 'UserPreference'
        db.delete_table('sis_userpreference_additional_report_fields')

        # Deleting model 'ReportField'
        db.delete_table(u'sis_reportfield')

        # Deleting model 'MdlUser'
        db.delete_table(u'sis_mdluser')

        # Deleting model 'EmergencyContact'
        db.delete_table(u'sis_emergencycontact')

        # Deleting model 'EmergencyContactNumber'
        db.delete_table(u'sis_emergencycontactnumber')

        # Deleting model 'Faculty'
        db.delete_table(u'sis_faculty')

        # Deleting model 'Cohort'
        db.delete_table(u'sis_cohort')

        # Removing M2M table for field students on 'Cohort'
        db.delete_table('sis_studentcohort')

        # Deleting model 'PerCourseCohort'
        db.delete_table(u'sis_percoursecohort')

        # Deleting model 'ReasonLeft'
        db.delete_table(u'sis_reasonleft')

        # Deleting model 'GradeLevel'
        db.delete_table(u'sis_gradelevel')

        # Deleting model 'LanguageChoice'
        db.delete_table(u'sis_languagechoice')

        # Deleting model 'ClassYear'
        db.delete_table(u'sis_classyear')

        # Deleting model 'Student'
        db.delete_table(u'sis_student')

        # Removing M2M table for field family_access_users on 'Student'
        db.delete_table('sis_student_family_access_users')

        # Removing M2M table for field emergency_contacts on 'Student'
        db.delete_table('sis_student_emergency_contacts')

        # Removing M2M table for field siblings on 'Student'
        db.delete_table('sis_student_siblings')

        # Deleting model 'ASPHistory'
        db.delete_table(u'sis_asphistory')

        # Deleting model 'StudentCohort'
        db.delete_table(u'sis_studentcohort')

        # Deleting model 'TranscriptNoteChoices'
        db.delete_table(u'sis_transcriptnotechoices')

        # Deleting model 'TranscriptNote'
        db.delete_table(u'sis_transcriptnote')

        # Deleting model 'StudentNumber'
        db.delete_table(u'sis_studentnumber')

        # Deleting model 'StudentFile'
        db.delete_table(u'sis_studentfile')

        # Deleting model 'StudentHealthRecord'
        db.delete_table(u'sis_studenthealthrecord')

        # Deleting model 'SchoolYear'
        db.delete_table(u'sis_schoolyear')

        # Deleting model 'ImportLog'
        db.delete_table(u'sis_importlog')

        # Deleting model 'MessageToStudent'
        db.delete_table(u'sis_messagetostudent')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'schedule.course': {
            'Meta': {'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'credits': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrollments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sis.MdlUser']", 'null': 'True', 'through': u"orm['schedule.CourseEnrollment']", 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'graded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'homeroom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_grade_submission': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'marking_period': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.MarkingPeriod']", 'symmetrical': 'False', 'blank': 'True'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.Period']", 'symmetrical': 'False', 'through': u"orm['schedule.CourseMeet']", 'blank': 'True'}),
            'secondary_teachers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_teachers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sis.Faculty']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ateacher'", 'null': 'True', 'to': u"orm['sis.Faculty']"})
        },
        u'schedule.courseenrollment': {
            'Meta': {'unique_together': "(('course', 'user', 'role'),)", 'object_name': 'CourseEnrollment'},
            'attendance_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'exclude_days': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.Day']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'Student'", 'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.MdlUser']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        u'schedule.coursemeet': {
            'Meta': {'object_name': 'CourseMeet'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Location']", 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Period']"})
        },
        u'schedule.day': {
            'Meta': {'ordering': "('day',)", 'object_name': 'Day'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'schedule.department': {
            'Meta': {'ordering': "('order_rank', 'name')", 'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'schedule.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'schedule.markingperiod': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'MarkingPeriod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.SchoolYear']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'show_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'})
        },
        u'schedule.period': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Period'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        u'sis.asphistory': {
            'Meta': {'object_name': 'ASPHistory'},
            'asp': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'enroll': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'sis.classyear': {
            'Meta': {'object_name': 'ClassYear'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('ecwsp.sis.models.IntegerRangeField', [], {'unique': 'True'})
        },
        u'sis.cohort': {
            'Meta': {'object_name': 'Cohort'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sis.Student']", 'null': 'True', 'db_table': "'sis_studentcohort'", 'blank': 'True'})
        },
        u'sis.emergencycontact': {
            'Meta': {'ordering': "('primary_contact', 'lname')", 'object_name': 'EmergencyContact'},
            'city': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emergency_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sync_schoolreach': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'sis.emergencycontactnumber': {
            'Meta': {'object_name': 'EmergencyContactNumber'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.EmergencyContact']"}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'})
        },
        u'sis.faculty': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Faculty', '_ormbases': [u'sis.MdlUser']},
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        u'sis.importlog': {
            'Meta': {'object_name': 'ImportLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'errors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sql_backup': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_note': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        u'sis.languagechoice': {
            'Meta': {'object_name': 'LanguageChoice'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.mdluser': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'MdlUser'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.messagetostudent': {
            'Meta': {'object_name': 'MessageToStudent'},
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('ckeditor.fields.RichTextField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        },
        u'sis.percoursecohort': {
            'Meta': {'object_name': 'PerCourseCohort', '_ormbases': [u'sis.Cohort']},
            u'cohort_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.Cohort']", 'unique': 'True', 'primary_key': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"})
        },
        u'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.reportfield': {
            'Meta': {'object_name': 'ReportField'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.schoolyear': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'SchoolYear'},
            'active_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'sis.student': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Student', '_ormbases': [u'sis.MdlUser']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sis.Cohort']"}),
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Cohort']", 'symmetrical': 'False', 'through': u"orm['sis.StudentCohort']", 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'parent_guardian': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pic': ('ecwsp.sis.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((70, 65), (530, 400))'}),
            'reason_left': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ReasonLeft']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'sis.studentcohort': {
            'Meta': {'object_name': 'StudentCohort'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Cohort']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'sis.studentfile': {
            'Meta': {'object_name': 'StudentFile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'sis.studenthealthrecord': {
            'Meta': {'object_name': 'StudentHealthRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.TextField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'sis.studentnumber': {
            'Meta': {'object_name': 'StudentNumber'},
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'})
        },
        u'sis.transcriptnote': {
            'Meta': {'object_name': 'TranscriptNote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'predefined_note': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.TranscriptNoteChoices']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'sis.transcriptnotechoices': {
            'Meta': {'object_name': 'TranscriptNoteChoices'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {})
        },
        u'sis.userpreference': {
            'Meta': {'object_name': 'UserPreference'},
            'additional_report_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sis.ReportField']", 'null': 'True', 'blank': 'True'}),
            'course_sort': ('django.db.models.fields.CharField', [], {'default': "'department'", 'max_length': '64'}),
            'gradebook_preference': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_deleted_students': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'omr_default_number_answers': ('django.db.models.fields.IntegerField', [], {'default': '2', 'blank': 'True'}),
            'omr_default_point_value': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'omr_default_save_question_to_bank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prefered_file_format': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': "'1'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['sis']

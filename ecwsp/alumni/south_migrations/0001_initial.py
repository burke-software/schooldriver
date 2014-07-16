# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'College'
        db.create_table(u'alumni_college', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
        ))
        db.send_create_signal(u'alumni', ['College'])

        # Adding model 'CollegeEnrollment'
        db.create_table(u'alumni_collegeenrollment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('search_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('college', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.College'])),
            ('program_years', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('graduated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('graduation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('degree_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('major', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('alumni', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.Alumni'])),
            ('college_sequence', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'alumni', ['CollegeEnrollment'])

        # Adding model 'AlumniStatus'
        db.create_table(u'alumni_alumnistatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'alumni', ['AlumniStatus'])

        # Adding model 'Withdrawl'
        db.create_table(u'alumni_withdrawl', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('college', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.College'])),
            ('alumni', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.Alumni'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('semesters', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3, blank=True)),
            ('from_enrollment', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alumni', ['Withdrawl'])

        # Adding model 'AlumniNoteCategory'
        db.create_table(u'alumni_alumninotecategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'alumni', ['AlumniNoteCategory'])

        # Adding model 'AlumniNote'
        db.create_table(u'alumni_alumninote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.AlumniNoteCategory'], null=True, blank=True)),
            ('note', self.gf('ckeditor.fields.RichTextField')()),
            ('alumni', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.Alumni'])),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'alumni', ['AlumniNote'])

        # Adding model 'AlumniAction'
        db.create_table(u'alumni_alumniaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'alumni', ['AlumniAction'])

        # Adding M2M table for field alumni on 'AlumniAction'
        m2m_table_name = db.shorten_name(u'alumni_alumniaction_alumni')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('alumniaction', models.ForeignKey(orm[u'alumni.alumniaction'], null=False)),
            ('alumni', models.ForeignKey(orm[u'alumni.alumni'], null=False))
        ))
        db.create_unique(m2m_table_name, ['alumniaction_id', 'alumni_id'])

        # Adding model 'AlumniEmail'
        db.create_table(u'alumni_alumniemail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('alumni', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.Alumni'])),
        ))
        db.send_create_signal(u'alumni', ['AlumniEmail'])

        # Adding model 'AlumniPhoneNumber'
        db.create_table(u'alumni_alumniphonenumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone_number', self.gf('localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('alumni', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.Alumni'])),
        ))
        db.send_create_signal(u'alumni', ['AlumniPhoneNumber'])

        # Adding model 'Alumni'
        db.create_table(u'alumni_alumni', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.Student'], unique=True)),
            ('college', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='college_student', null=True, to=orm['alumni.College'])),
            ('graduated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('graduation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('college_override', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alumni.AlumniStatus'], null=True, blank=True)),
            ('program_years', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('semesters', self.gf('django.db.models.fields.CharField')(max_length='5', blank=True)),
            ('on_track', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alumni', ['Alumni'])


    def backwards(self, orm):
        # Deleting model 'College'
        db.delete_table(u'alumni_college')

        # Deleting model 'CollegeEnrollment'
        db.delete_table(u'alumni_collegeenrollment')

        # Deleting model 'AlumniStatus'
        db.delete_table(u'alumni_alumnistatus')

        # Deleting model 'Withdrawl'
        db.delete_table(u'alumni_withdrawl')

        # Deleting model 'AlumniNoteCategory'
        db.delete_table(u'alumni_alumninotecategory')

        # Deleting model 'AlumniNote'
        db.delete_table(u'alumni_alumninote')

        # Deleting model 'AlumniAction'
        db.delete_table(u'alumni_alumniaction')

        # Removing M2M table for field alumni on 'AlumniAction'
        db.delete_table(db.shorten_name(u'alumni_alumniaction_alumni'))

        # Deleting model 'AlumniEmail'
        db.delete_table(u'alumni_alumniemail')

        # Deleting model 'AlumniPhoneNumber'
        db.delete_table(u'alumni_alumniphonenumber')

        # Deleting model 'Alumni'
        db.delete_table(u'alumni_alumni')


    models = {
        u'alumni.alumni': {
            'Meta': {'object_name': 'Alumni'},
            'college': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'college_student'", 'null': 'True', 'to': u"orm['alumni.College']"}),
            'college_override': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'graduated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'graduation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'on_track': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'program_years': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'semesters': ('django.db.models.fields.CharField', [], {'max_length': "'5'", 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.AlumniStatus']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.Student']", 'unique': 'True'}),
            'withdrawls': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['alumni.College']", 'through': u"orm['alumni.Withdrawl']", 'symmetrical': 'False'})
        },
        u'alumni.alumniaction': {
            'Meta': {'object_name': 'AlumniAction'},
            'alumni': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['alumni.Alumni']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'alumni.alumniemail': {
            'Meta': {'object_name': 'AlumniEmail'},
            'alumni': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.Alumni']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'alumni.alumninote': {
            'Meta': {'object_name': 'AlumniNote'},
            'alumni': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.Alumni']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.AlumniNoteCategory']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('ckeditor.fields.RichTextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'alumni.alumninotecategory': {
            'Meta': {'object_name': 'AlumniNoteCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'alumni.alumniphonenumber': {
            'Meta': {'object_name': 'AlumniPhoneNumber'},
            'alumni': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.Alumni']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'alumni.alumnistatus': {
            'Meta': {'ordering': "['name']", 'object_name': 'AlumniStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'alumni.college': {
            'Meta': {'ordering': "['name']", 'object_name': 'College'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        u'alumni.collegeenrollment': {
            'Meta': {'object_name': 'CollegeEnrollment'},
            'alumni': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.Alumni']"}),
            'begin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'college': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.College']"}),
            'college_sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'degree_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'graduated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'graduation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'major': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'program_years': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'search_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        u'alumni.withdrawl': {
            'Meta': {'object_name': 'Withdrawl'},
            'alumni': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.Alumni']"}),
            'college': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alumni.College']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'from_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semesters': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'})
        },
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sis.classyear': {
            'Meta': {'object_name': 'ClassYear'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('ecwsp.sis.models.IntegerRangeField', [], {'unique': 'True'})
        },
        u'sis.cohort': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Cohort'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'student_cohorts'", 'blank': 'True', 'to': u"orm['sis.Student']"})
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
        u'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        u'sis.languagechoice': {
            'Meta': {'object_name': 'LanguageChoice'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.student': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'Student', '_ormbases': [u'auth.User']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sis.Cohort']"}),
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Cohort']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['alumni']
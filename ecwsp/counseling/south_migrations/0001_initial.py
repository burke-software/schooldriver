# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FollowUpAction'
        db.create_table(u'counseling_followupaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'counseling', ['FollowUpAction'])

        # Adding model 'StudentMeetingCategory'
        db.create_table(u'counseling_studentmeetingcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'counseling', ['StudentMeetingCategory'])

        # Adding model 'StudentMeeting'
        db.create_table(u'counseling_studentmeeting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['counseling.StudentMeetingCategory'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('notes', self.gf('ckeditor.fields.RichTextField')(blank=True)),
            ('follow_up_action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['counseling.FollowUpAction'], null=True, blank=True)),
            ('follow_up_notes', self.gf('django.db.models.fields.CharField')(max_length=2024, blank=True)),
            ('reported_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('referral_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['counseling.ReferralForm'], null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'counseling', ['StudentMeeting'])

        # Adding M2M table for field students on 'StudentMeeting'
        m2m_table_name = db.shorten_name(u'counseling_studentmeeting_students')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentmeeting', models.ForeignKey(orm[u'counseling.studentmeeting'], null=False)),
            ('student', models.ForeignKey(orm[u'sis.student'], null=False))
        ))
        db.create_unique(m2m_table_name, ['studentmeeting_id', 'student_id'])

        # Adding model 'ReferralCategory'
        db.create_table(u'counseling_referralcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'counseling', ['ReferralCategory'])

        # Adding model 'ReferralReason'
        db.create_table(u'counseling_referralreason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['counseling.ReferralCategory'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'counseling', ['ReferralReason'])

        # Adding model 'ReferralForm'
        db.create_table(u'counseling_referralform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('classroom_teacher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='referral_classroom_teacher', to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('referred_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['sis.Student'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'counseling', ['ReferralForm'])

        # Adding M2M table for field referral_reasons on 'ReferralForm'
        m2m_table_name = db.shorten_name(u'counseling_referralform_referral_reasons')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('referralform', models.ForeignKey(orm[u'counseling.referralform'], null=False)),
            ('referralreason', models.ForeignKey(orm[u'counseling.referralreason'], null=False))
        ))
        db.create_unique(m2m_table_name, ['referralform_id', 'referralreason_id'])


    def backwards(self, orm):
        # Deleting model 'FollowUpAction'
        db.delete_table(u'counseling_followupaction')

        # Deleting model 'StudentMeetingCategory'
        db.delete_table(u'counseling_studentmeetingcategory')

        # Deleting model 'StudentMeeting'
        db.delete_table(u'counseling_studentmeeting')

        # Removing M2M table for field students on 'StudentMeeting'
        db.delete_table(db.shorten_name(u'counseling_studentmeeting_students'))

        # Deleting model 'ReferralCategory'
        db.delete_table(u'counseling_referralcategory')

        # Deleting model 'ReferralReason'
        db.delete_table(u'counseling_referralreason')

        # Deleting model 'ReferralForm'
        db.delete_table(u'counseling_referralform')

        # Removing M2M table for field referral_reasons on 'ReferralForm'
        db.delete_table(db.shorten_name(u'counseling_referralform_referral_reasons'))


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
        u'counseling.followupaction': {
            'Meta': {'object_name': 'FollowUpAction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'counseling.referralcategory': {
            'Meta': {'object_name': 'ReferralCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'counseling.referralform': {
            'Meta': {'object_name': 'ReferralForm'},
            'classroom_teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'referral_classroom_teacher'", 'to': u"orm['auth.User']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referral_reasons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['counseling.ReferralReason']", 'null': 'True', 'blank': 'True'}),
            'referred_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['sis.Student']"})
        },
        u'counseling.referralreason': {
            'Meta': {'object_name': 'ReferralReason'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['counseling.ReferralCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'counseling.studentmeeting': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'StudentMeeting'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['counseling.StudentMeetingCategory']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'follow_up_action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['counseling.FollowUpAction']", 'null': 'True', 'blank': 'True'}),
            'follow_up_notes': ('django.db.models.fields.CharField', [], {'max_length': '2024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'referral_form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['counseling.ReferralForm']", 'null': 'True', 'blank': 'True'}),
            'reported_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'student_meeting_set'", 'symmetrical': 'False', 'to': u"orm['sis.Student']"})
        },
        u'counseling.studentmeetingcategory': {
            'Meta': {'object_name': 'StudentMeetingCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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

    complete_apps = ['counseling']
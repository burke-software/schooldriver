# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Company.alternative_contract_template'
        db.add_column(u'work_study_company', 'alternative_contract_template',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Company.alternative_contract_template'
        db.delete_column(u'work_study_company', 'alternative_contract_template')


    models = {
        u'attendance.attendancestatus': {
            'Meta': {'object_name': 'AttendanceStatus'},
            'absent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'excused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'half': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'tardy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'teacher_selectable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'attendance.studentattendance': {
            'Meta': {'ordering': "('-date', 'student')", 'unique_together': "(('student', 'date', 'status'),)", 'object_name': 'StudentAttendance'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'private_notes': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendance.AttendanceStatus']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_attn'", 'to': u"orm['sis.Student']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('primary_contact', 'emergency_only', 'lname')", 'object_name': 'EmergencyContact'},
            'city': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emergency_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
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
        u'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
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
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
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
        u'work_study.attendance': {
            'Meta': {'object_name': 'Attendance'},
            'absence_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'billed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.AttendanceFee']", 'null': 'True', 'blank': 'True'}),
            'half_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'makeup_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'reason': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.AttendanceReason']", 'null': 'True', 'blank': 'True'}),
            'sis_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendance.StudentAttendance']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'tardy': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'tardy_time_in': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'waive': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'work_study.attendancefee': {
            'Meta': {'object_name': 'AttendanceFee'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'work_study.attendancereason': {
            'Meta': {'object_name': 'AttendanceReason'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.clientvisit': {
            'Meta': {'object_name': 'ClientVisit'},
            'ability_to_learn_new_tasks': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'accuracy_and_attention_to_detail': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'attendance_and_punctuality': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'attitude_and_motivation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'cra': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.CraContact']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'dol': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'follow_up_of': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.ClientVisit']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiative_and_self_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'interaction_with_coworkers': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'job_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notify_mentors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'observations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'organizational_skills': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'productivity_and_time_management': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'professional_appearance': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'student_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_worker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']", 'null': 'True', 'blank': 'True'}),
            'supervisor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.Contact']", 'null': 'True', 'blank': 'True'}),
            'supervisor_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'work_environment': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        u'work_study.company': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Company'},
            'alternative_contract_template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'work_study.companyhistory': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('student', 'placement', 'date'),)", 'object_name': 'CompanyHistory'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'fired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"})
        },
        u'work_study.compcontract': {
            'Meta': {'object_name': 'CompContract'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Company']"}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contract_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number_students': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'default': '9999', 'to': u"orm['work_study.PaymentOption']", 'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.SchoolYear']", 'null': 'True', 'blank': 'True'}),
            'signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_desired_skills': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.StudentDesiredSkill']", 'null': 'True', 'blank': 'True'}),
            'student_desired_skills_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_functional_responsibilities': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.StudentFunctionalResponsibility']", 'null': 'True', 'blank': 'True'}),
            'student_functional_responsibilities_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_leave': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_errands': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_lunch': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'work_study.contact': {
            'Meta': {'ordering': "('lname',)", 'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'phone_cell': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'work_study.cracontact': {
            'Meta': {'object_name': 'CraContact'},
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'work_study.handout33': {
            'Meta': {'ordering': "('category', 'like')", 'object_name': 'Handout33'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.messagetosupervisor': {
            'Meta': {'object_name': 'MessageToSupervisor'},
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('ckeditor.fields.RichTextField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        },
        u'work_study.paymentoption': {
            'Meta': {'object_name': 'PaymentOption'},
            'cost_per_student': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'details': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.personality': {
            'Meta': {'ordering': "('type',)", 'object_name': 'Personality'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'})
        },
        u'work_study.pickuplocation': {
            'Meta': {'object_name': 'PickupLocation'},
            'directions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'work_study.presetcomment': {
            'Meta': {'ordering': "('comment',)", 'object_name': 'PresetComment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'work_study.studentdesiredskill': {
            'Meta': {'object_name': 'StudentDesiredSkill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.studentfunctionalresponsibility': {
            'Meta': {'object_name': 'StudentFunctionalResponsibility'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.studentinteraction': {
            'Meta': {'object_name': 'StudentInteraction'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'companies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.WorkTeam']", 'symmetrical': 'False', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preset_comment': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.PresetComment']", 'symmetrical': 'False', 'blank': 'True'}),
            'reported_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.StudentWorker']", 'symmetrical': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'work_study.studentworker': {
            'Meta': {'ordering': "('inactive', 'lname', 'fname')", 'object_name': 'StudentWorker', '_ormbases': [u'sis.Student']},
            'adp_number': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'am_route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'am_student_set'", 'null': 'True', 'to': u"orm['work_study.StudentWorkerRoute']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'handout33': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.Handout33']", 'null': 'True', 'blank': 'True'}),
            'personality_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Personality']", 'null': 'True', 'blank': 'True'}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']", 'null': 'True', 'blank': 'True'}),
            'pm_route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pm_student_set'", 'null': 'True', 'to': u"orm['work_study.StudentWorkerRoute']"}),
            'primary_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Contact']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'school_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'student_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            u'student_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.Student']", 'unique': 'True', 'primary_key': 'True'}),
            'transport_exception': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'work_permit_no': ('ecwsp.sis.helper_functions.CharNullField', [], {'max_length': '10', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'work_study.studentworkerroute': {
            'Meta': {'object_name': 'StudentWorkerRoute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'work_study.survey': {
            'Meta': {'ordering': "('survey', 'student', 'question')", 'object_name': 'Survey'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '510', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'survey': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.timesheet': {
            'Meta': {'object_name': 'TimeSheet'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'cra_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'for_pay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hours': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.TimeSheetPerformanceChoice']", 'null': 'True', 'blank': 'True'}),
            'school_net': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'school_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'show_student_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'student_accomplishment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_net': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'student_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'supervisor_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'supervisor_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'time_in': ('django.db.models.fields.TimeField', [], {}),
            'time_lunch': ('django.db.models.fields.TimeField', [], {}),
            'time_lunch_return': ('django.db.models.fields.TimeField', [], {}),
            'time_out': ('django.db.models.fields.TimeField', [], {})
        },
        u'work_study.timesheetperformancechoice': {
            'Meta': {'ordering': "('rank',)", 'object_name': 'TimeSheetPerformanceChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '1', 'unique': 'True'})
        },
        u'work_study.workteam': {
            'Meta': {'ordering': "('team_name',)", 'object_name': 'WorkTeam'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'am_transport_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workteamset_dropoff'", 'null': 'True', 'db_column': "'dropoff_location_id'", 'to': u"orm['work_study.PickupLocation']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Company']", 'null': 'True', 'blank': 'True'}),
            'company_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.Contact']", 'symmetrical': 'False', 'blank': 'True'}),
            'cras': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.CraContact']", 'null': 'True', 'blank': 'True'}),
            'directions_pickup': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'directions_to': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'funded_by': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'industry_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'job_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'map': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'paying': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'pm_transport_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.PickupLocation']", 'null': 'True', 'db_column': "'pickup_location_id'", 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'stop_location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'time_earliest': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_ideal': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_latest': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'travel_route': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'train_line'", 'blank': 'True'}),
            'use_google_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['work_study']
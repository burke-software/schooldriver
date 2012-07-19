# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Department'
        db.create_table('omr_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('omr', ['Department'])

        # Adding model 'MeasurementTopic'
        db.create_table('omr_measurementtopic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Department'], null=True, blank=True)),
        ))
        db.send_create_signal('omr', ['MeasurementTopic'])

        # Adding unique constraint on 'MeasurementTopic', fields ['name', 'department']
        db.create_unique('omr_measurementtopic', ['name', 'department_id'])

        # Adding model 'Benchmark'
        db.create_table('omr_benchmark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
        ))
        db.send_create_signal('omr', ['Benchmark'])

        # Adding unique constraint on 'Benchmark', fields ['number', 'name']
        db.create_unique('omr_benchmark', ['number', 'name'])

        # Adding M2M table for field measurement_topics on 'Benchmark'
        db.create_table('omr_benchmark_measurement_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('benchmark', models.ForeignKey(orm['omr.benchmark'], null=False)),
            ('measurementtopic', models.ForeignKey(orm['omr.measurementtopic'], null=False))
        ))
        db.create_unique('omr_benchmark_measurement_topics', ['benchmark_id', 'measurementtopic_id'])

        # Adding model 'Theme'
        db.create_table('omr_theme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('omr', ['Theme'])

        # Adding model 'Test'
        db.create_table('omr_test', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'], null=True, blank=True)),
            ('marking_period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'], null=True, blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Department'], null=True, blank=True)),
            ('finalized', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('answer_sheet_pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('queXF_pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('banding', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('omr', ['Test'])

        # Adding M2M table for field teachers on 'Test'
        db.create_table('omr_test_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('test', models.ForeignKey(orm['omr.test'], null=False)),
            ('faculty', models.ForeignKey(orm['sis.faculty'], null=False))
        ))
        db.create_unique('omr_test_teachers', ['test_id', 'faculty_id'])

        # Adding M2M table for field courses on 'Test'
        db.create_table('omr_test_courses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('test', models.ForeignKey(orm['omr.test'], null=False)),
            ('course', models.ForeignKey(orm['schedule.course'], null=False))
        ))
        db.create_unique('omr_test_courses', ['test_id', 'course_id'])

        # Adding model 'TestVersion'
        db.create_table('omr_testversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Test'])),
        ))
        db.send_create_signal('omr', ['TestVersion'])

        # Adding model 'QuestionGroup'
        db.create_table('omr_questiongroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('omr', ['QuestionGroup'])

        # Adding model 'QuestionBank'
        db.create_table('omr_questionbank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('ckeditor.fields.RichTextField')()),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.QuestionGroup'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Multiple Choice', max_length=25)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('is_true', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('network_question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.NetworkQuestionBank'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('omr', ['QuestionBank'])

        # Adding M2M table for field benchmarks on 'QuestionBank'
        db.create_table('omr_questionbank_benchmarks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('questionbank', models.ForeignKey(orm['omr.questionbank'], null=False)),
            ('benchmark', models.ForeignKey(orm['omr.benchmark'], null=False))
        ))
        db.create_unique('omr_questionbank_benchmarks', ['questionbank_id', 'benchmark_id'])

        # Adding M2M table for field themes on 'QuestionBank'
        db.create_table('omr_questionbank_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('questionbank', models.ForeignKey(orm['omr.questionbank'], null=False)),
            ('theme', models.ForeignKey(orm['omr.theme'], null=False))
        ))
        db.create_unique('omr_questionbank_themes', ['questionbank_id', 'theme_id'])

        # Adding model 'NetworkQuestionBank'
        db.create_table('omr_networkquestionbank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('ckeditor.fields.RichTextField')()),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.QuestionGroup'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Multiple Choice', max_length=25)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('is_true', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('school', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal('omr', ['NetworkQuestionBank'])

        # Adding M2M table for field benchmarks on 'NetworkQuestionBank'
        db.create_table('omr_networkquestionbank_benchmarks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('networkquestionbank', models.ForeignKey(orm['omr.networkquestionbank'], null=False)),
            ('benchmark', models.ForeignKey(orm['omr.benchmark'], null=False))
        ))
        db.create_unique('omr_networkquestionbank_benchmarks', ['networkquestionbank_id', 'benchmark_id'])

        # Adding M2M table for field themes on 'NetworkQuestionBank'
        db.create_table('omr_networkquestionbank_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('networkquestionbank', models.ForeignKey(orm['omr.networkquestionbank'], null=False)),
            ('theme', models.ForeignKey(orm['omr.theme'], null=False))
        ))
        db.create_unique('omr_networkquestionbank_themes', ['networkquestionbank_id', 'theme_id'])

        # Adding model 'Question'
        db.create_table('omr_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('ckeditor.fields.RichTextField')()),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.QuestionGroup'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Multiple Choice', max_length=25)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('is_true', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Test'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('omr', ['Question'])

        # Adding M2M table for field benchmarks on 'Question'
        db.create_table('omr_question_benchmarks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['omr.question'], null=False)),
            ('benchmark', models.ForeignKey(orm['omr.benchmark'], null=False))
        ))
        db.create_unique('omr_question_benchmarks', ['question_id', 'benchmark_id'])

        # Adding M2M table for field themes on 'Question'
        db.create_table('omr_question_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['omr.question'], null=False)),
            ('theme', models.ForeignKey(orm['omr.theme'], null=False))
        ))
        db.create_unique('omr_question_themes', ['question_id', 'theme_id'])

        # Adding model 'ErrorType'
        db.create_table('omr_errortype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('omr', ['ErrorType'])

        # Adding model 'AnswerBank'
        db.create_table('omr_answerbank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer', self.gf('ckeditor.fields.RichTextField')()),
            ('error_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.ErrorType'], null=True, blank=True)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.QuestionBank'])),
        ))
        db.send_create_signal('omr', ['AnswerBank'])

        # Adding model 'Answer'
        db.create_table('omr_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer', self.gf('ckeditor.fields.RichTextField')()),
            ('error_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.ErrorType'], null=True, blank=True)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Question'])),
        ))
        db.send_create_signal('omr', ['Answer'])

        # Adding model 'TestInstance'
        db.create_table('omr_testinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'], null=True, blank=True)),
            ('marking_period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'], null=True, blank=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Test'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('results_recieved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('omr', ['TestInstance'])

        # Adding M2M table for field teachers on 'TestInstance'
        db.create_table('omr_testinstance_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testinstance', models.ForeignKey(orm['omr.testinstance'], null=False)),
            ('faculty', models.ForeignKey(orm['sis.faculty'], null=False))
        ))
        db.create_unique('omr_testinstance_teachers', ['testinstance_id', 'faculty_id'])

        # Adding model 'AnswerInstance'
        db.create_table('omr_answerinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.TestInstance'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Question'])),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omr.Answer'])),
            ('points_earned', self.gf('django.db.models.fields.IntegerField')()),
            ('points_possible', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('omr', ['AnswerInstance'])

        # Adding unique constraint on 'AnswerInstance', fields ['test_instance', 'question']
        db.create_unique('omr_answerinstance', ['test_instance_id', 'question_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'AnswerInstance', fields ['test_instance', 'question']
        db.delete_unique('omr_answerinstance', ['test_instance_id', 'question_id'])

        # Removing unique constraint on 'Benchmark', fields ['number', 'name']
        db.delete_unique('omr_benchmark', ['number', 'name'])

        # Removing unique constraint on 'MeasurementTopic', fields ['name', 'department']
        db.delete_unique('omr_measurementtopic', ['name', 'department_id'])

        # Deleting model 'Department'
        db.delete_table('omr_department')

        # Deleting model 'MeasurementTopic'
        db.delete_table('omr_measurementtopic')

        # Deleting model 'Benchmark'
        db.delete_table('omr_benchmark')

        # Removing M2M table for field measurement_topics on 'Benchmark'
        db.delete_table('omr_benchmark_measurement_topics')

        # Deleting model 'Theme'
        db.delete_table('omr_theme')

        # Deleting model 'Test'
        db.delete_table('omr_test')

        # Removing M2M table for field teachers on 'Test'
        db.delete_table('omr_test_teachers')

        # Removing M2M table for field courses on 'Test'
        db.delete_table('omr_test_courses')

        # Deleting model 'TestVersion'
        db.delete_table('omr_testversion')

        # Deleting model 'QuestionGroup'
        db.delete_table('omr_questiongroup')

        # Deleting model 'QuestionBank'
        db.delete_table('omr_questionbank')

        # Removing M2M table for field benchmarks on 'QuestionBank'
        db.delete_table('omr_questionbank_benchmarks')

        # Removing M2M table for field themes on 'QuestionBank'
        db.delete_table('omr_questionbank_themes')

        # Deleting model 'NetworkQuestionBank'
        db.delete_table('omr_networkquestionbank')

        # Removing M2M table for field benchmarks on 'NetworkQuestionBank'
        db.delete_table('omr_networkquestionbank_benchmarks')

        # Removing M2M table for field themes on 'NetworkQuestionBank'
        db.delete_table('omr_networkquestionbank_themes')

        # Deleting model 'Question'
        db.delete_table('omr_question')

        # Removing M2M table for field benchmarks on 'Question'
        db.delete_table('omr_question_benchmarks')

        # Removing M2M table for field themes on 'Question'
        db.delete_table('omr_question_themes')

        # Deleting model 'ErrorType'
        db.delete_table('omr_errortype')

        # Deleting model 'AnswerBank'
        db.delete_table('omr_answerbank')

        # Deleting model 'Answer'
        db.delete_table('omr_answer')

        # Deleting model 'TestInstance'
        db.delete_table('omr_testinstance')

        # Removing M2M table for field teachers on 'TestInstance'
        db.delete_table('omr_testinstance_teachers')

        # Deleting model 'AnswerInstance'
        db.delete_table('omr_answerinstance')


    models = {
        'omr.answer': {
            'Meta': {'object_name': 'Answer'},
            'answer': ('ckeditor.fields.RichTextField', [], {}),
            'error_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.ErrorType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Question']"})
        },
        'omr.answerbank': {
            'Meta': {'object_name': 'AnswerBank'},
            'answer': ('ckeditor.fields.RichTextField', [], {}),
            'error_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.ErrorType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.QuestionBank']"})
        },
        'omr.answerinstance': {
            'Meta': {'unique_together': "(('test_instance', 'question'),)", 'object_name': 'AnswerInstance'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Answer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points_earned': ('django.db.models.fields.IntegerField', [], {}),
            'points_possible': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Question']"}),
            'test_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.TestInstance']"})
        },
        'omr.benchmark': {
            'Meta': {'ordering': "('number', 'name')", 'unique_together': "(('number', 'name'),)", 'object_name': 'Benchmark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['omr.MeasurementTopic']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        'omr.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'omr.errortype': {
            'Meta': {'object_name': 'ErrorType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'omr.measurementtopic': {
            'Meta': {'ordering': "('department', 'name')", 'unique_together': "(('name', 'department'),)", 'object_name': 'MeasurementTopic'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'})
        },
        'omr.networkquestionbank': {
            'Meta': {'object_name': 'NetworkQuestionBank'},
            'benchmarks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Benchmark']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.QuestionGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_true': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'question': ('ckeditor.fields.RichTextField', [], {}),
            'school': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Theme']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Multiple Choice'", 'max_length': '25'})
        },
        'omr.question': {
            'Meta': {'ordering': "['order']", 'object_name': 'Question'},
            'benchmarks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Benchmark']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.QuestionGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_true': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'question': ('ckeditor.fields.RichTextField', [], {}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Test']"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Theme']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Multiple Choice'", 'max_length': '25'})
        },
        'omr.questionbank': {
            'Meta': {'object_name': 'QuestionBank'},
            'benchmarks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Benchmark']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.QuestionGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_true': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'network_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.NetworkQuestionBank']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'question': ('ckeditor.fields.RichTextField', [], {}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omr.Theme']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Multiple Choice'", 'max_length': '25'})
        },
        'omr.questiongroup': {
            'Meta': {'object_name': 'QuestionGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'omr.test': {
            'Meta': {'object_name': 'Test'},
            'answer_sheet_pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'banding': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Department']", 'null': 'True', 'blank': 'True'}),
            'finalized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'queXF_pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']", 'null': 'True', 'blank': 'True'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Student']", 'null': 'True', 'through': "orm['omr.TestInstance']", 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Faculty']", 'null': 'True', 'blank': 'True'})
        },
        'omr.testinstance': {
            'Meta': {'object_name': 'TestInstance'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'results_recieved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Faculty']", 'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Test']"})
        },
        'omr.testversion': {
            'Meta': {'object_name': 'TestVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Test']"})
        },
        'omr.theme': {
            'Meta': {'object_name': 'Theme'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'schedule.course': {
            'Meta': {'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'credits': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrollments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.MdlUser']", 'null': 'True', 'through': "orm['schedule.CourseEnrollment']", 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'graded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'homeroom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_grade_submission': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'marking_period': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.MarkingPeriod']", 'symmetrical': 'False', 'blank': 'True'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Period']", 'symmetrical': 'False', 'through': "orm['schedule.CourseMeet']", 'blank': 'True'}),
            'secondary_teachers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_teachers'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['sis.Faculty']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ateacher'", 'null': 'True', 'to': "orm['sis.Faculty']"})
        },
        'schedule.courseenrollment': {
            'Meta': {'unique_together': "(('course', 'user', 'role'),)", 'object_name': 'CourseEnrollment'},
            'attendance_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'exclude_days': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Day']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'Student'", 'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.MdlUser']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        'schedule.coursemeet': {
            'Meta': {'object_name': 'CourseMeet'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Location']", 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Period']"})
        },
        'schedule.day': {
            'Meta': {'ordering': "('day',)", 'object_name': 'Day'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schedule.department': {
            'Meta': {'ordering': "('order_rank', 'name')", 'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'schedule.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'schedule.markingperiod': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'MarkingPeriod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'show_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'schedule.period': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Period'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
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
        'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
        }
    }

    complete_apps = ['omr']
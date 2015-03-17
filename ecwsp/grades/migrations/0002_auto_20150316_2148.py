# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LetterGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('letter', models.CharField(max_length=50)),
                ('is_passing', models.BooleanField(default=True, help_text=b'True means this counts as a Passing or 100% grade.')),
                ('affects_grade', models.BooleanField(default=True, help_text=b'True means this has an affect on grade calculations')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='finalgrade',
            name='letter_grade',
            field=models.ForeignKey(blank=True, to='grades.LetterGrade', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grade',
            name='letter_grade',
            field=models.ForeignKey(blank=True, to='grades.LetterGrade', null=True),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='LetterGradeChoices',
        ),
    ]

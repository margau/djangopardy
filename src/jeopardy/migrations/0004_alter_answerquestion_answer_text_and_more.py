# Generated by Django 4.2.20 on 2025-04-18 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeopardy', '0003_answerquestion_answer_media_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerquestion',
            name='answer_text',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='answerquestion',
            name='question_text',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]

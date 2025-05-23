# Generated by Django 4.2.20 on 2025-04-18 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jeopardy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerquestionasked',
            name='player_correct',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='right_answer', to='jeopardy.player'),
        ),
        migrations.AlterField(
            model_name='answerquestionasked',
            name='player_wrong',
            field=models.ManyToManyField(blank=True, related_name='wrong_answers', to='jeopardy.player'),
        ),
    ]

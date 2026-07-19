# Generated manually - rename id_card to student_id, preserve data
from django.db import migrations, models
import random


def copy_and_generate_student_ids(apps, schema_editor):
    """将所有身份证号替换为学号：有身份证的生成新学号，没有的也生成"""
    UserProfile = apps.get_model('day21', 'UserProfile')
    import random
    used_ids = set()
    for p in UserProfile.objects.all():
        if p.student_id and p.student_id.startswith('STU'):
            used_ids.add(p.student_id)
    for p in UserProfile.objects.all():
        if p.student_id and p.student_id.startswith('STU'):
            continue
        # 有值（旧身份证号）或为空：都生成新学号
        while True:
            sid = 'STU' + str(random.randint(100000, 999999))
            if sid not in used_ids:
                used_ids.add(sid)
                p.student_id = sid
                break
        p.save(update_fields=['student_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('day21', '0013_add_q_type_to_quiz'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='id_card',
            new_name='student_id',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='学号'),
        ),
        migrations.RunPython(copy_and_generate_student_ids, reverse_code=migrations.RunPython.noop),
    ]

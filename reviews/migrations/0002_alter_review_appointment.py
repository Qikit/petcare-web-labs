import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_alter_medicalrecord_options_medicalrecord_date_and_more'),
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='appointment',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='review',
                to='appointments.appointment',
                verbose_name='запись',
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard_services", "0003_add_dashboardcustomproject"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardteams",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="team_images/"),
        ),
    ]

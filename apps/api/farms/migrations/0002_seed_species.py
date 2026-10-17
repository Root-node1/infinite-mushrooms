from django.db import migrations


def seed_species(apps, schema_editor):
    Species = apps.get_model("farms", "Species")
    for name in ("Oyster", "Reishi"):
        Species.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [("farms", "0001_initial")]

    operations = [migrations.RunPython(seed_species, migrations.RunPython.noop)]

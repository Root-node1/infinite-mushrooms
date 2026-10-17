from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Batch, Farm, Species, StageTemplate
from .services import NoStageTemplates, generate_stages

User = get_user_model()


class BatchTimelineTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            "0712345678", password="pw", full_name="Amina"
        )
        self.farm = Farm.objects.create(name="Test Farm", owner=self.owner)
        self.species = Species.objects.create(name="Test species")

    def make_batch(self, name="B1"):
        return Batch.objects.create(
            farm=self.farm,
            species=self.species,
            name=name,
            start_date=date(2026, 1, 1),
            quantity=50,
        )

    def add_templates(self):
        StageTemplate.objects.create(
            species=self.species, order=2, name="Colonization", duration_days=14
        )
        StageTemplate.objects.create(
            species=self.species, order=1, name="Inoculation", duration_days=3
        )

    def test_timeline_follows_template_order_and_dates(self):
        self.add_templates()
        stages = generate_stages(self.make_batch())
        self.assertEqual([s.name for s in stages], ["Inoculation", "Colonization"])
        self.assertEqual(stages[0].starts_on, date(2026, 1, 1))
        self.assertEqual(stages[0].due_on, date(2026, 1, 4))
        self.assertEqual(stages[1].starts_on, date(2026, 1, 4))
        self.assertEqual(stages[1].due_on, date(2026, 1, 18))

    def test_no_templates_raises(self):
        with self.assertRaises(NoStageTemplates):
            generate_stages(self.make_batch())

    def test_generating_twice_raises(self):
        self.add_templates()
        batch = self.make_batch()
        generate_stages(batch)
        with self.assertRaises(ValueError):
            generate_stages(batch)

    def test_batch_name_unique_per_farm(self):
        self.make_batch("B1")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_batch("B1")

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Farm(models.Model):
    name = models.CharField(max_length=150)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_farms",
    )
    location = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(max_length=80, unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "species"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StageTemplate(models.Model):
    """One stage in a species' growing cycle. Numbers come from the farmer."""

    species = models.ForeignKey(
        Species, on_delete=models.CASCADE, related_name="stage_templates"
    )
    order = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)
    duration_days = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="How many days this stage normally lasts",
    )
    conditions = models.TextField(
        blank=True,
        help_text="Target temperature, humidity, CO2 and light for this stage",
    )
    alert_before_days = models.PositiveSmallIntegerField(
        default=1, help_text="Warn this many days before the stage is due"
    )
    overdue_after_days = models.PositiveSmallIntegerField(
        default=1, help_text="Flag as overdue this many days after the due date"
    )

    class Meta:
        ordering = ["species", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["species", "order"], name="unique_stage_order_per_species"
            )
        ]

    def __str__(self):
        return f"{self.species} #{self.order}: {self.name}"


class Batch(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        HARVESTED = "harvested", "Harvested"
        DISCARDED = "discarded", "Discarded"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="batches")
    species = models.ForeignKey(
        Species, on_delete=models.PROTECT, related_name="batches"
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    quantity = models.PositiveIntegerField(help_text="Number of bags or blocks")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "batches"
        ordering = ["-start_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["farm", "name"], name="unique_batch_name_per_farm"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.species})"


class BatchStage(models.Model):
    """A dated stage on one batch's timeline, copied from a StageTemplate."""

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="stages")
    template = models.ForeignKey(
        StageTemplate, on_delete=models.PROTECT, related_name="+"
    )
    order = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)
    starts_on = models.DateField()
    due_on = models.DateField()
    completed_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["batch", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "order"], name="unique_stage_order_per_batch"
            )
        ]

    def __str__(self):
        return f"{self.batch.name}: {self.name} (due {self.due_on})"

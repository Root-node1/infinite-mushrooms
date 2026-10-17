from datetime import timedelta

from django.db import transaction

from .models import BatchStage


class NoStageTemplates(Exception):
    pass


@transaction.atomic
def generate_stages(batch):
    """Build a batch's dated timeline from its species' stage templates."""
    if batch.stages.exists():
        raise ValueError("This batch already has a stage timeline")

    templates = list(batch.species.stage_templates.order_by("order"))
    if not templates:
        raise NoStageTemplates(f"{batch.species} has no stage templates yet")

    stages = []
    starts_on = batch.start_date
    for template in templates:
        due_on = starts_on + timedelta(days=template.duration_days)
        stages.append(
            BatchStage.objects.create(
                batch=batch,
                template=template,
                order=template.order,
                name=template.name,
                starts_on=starts_on,
                due_on=due_on,
            )
        )
        starts_on = due_on
    return stages

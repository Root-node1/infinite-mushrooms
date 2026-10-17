from django.contrib import admin, messages

from .models import Batch, BatchStage, Farm, Species, StageTemplate
from .services import NoStageTemplates, generate_stages


class StageTemplateInline(admin.TabularInline):
    model = StageTemplate
    extra = 0


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    inlines = [StageTemplateInline]


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location", "created_at")
    search_fields = ("name", "location")


class BatchStageInline(admin.TabularInline):
    model = BatchStage
    extra = 0
    fields = ("order", "name", "starts_on", "due_on", "completed_on")
    readonly_fields = ("order", "name", "starts_on", "due_on")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "species", "start_date", "quantity", "status")
    list_filter = ("status", "species", "farm")
    search_fields = ("name",)
    inlines = [BatchStageInline]

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        if not change:
            try:
                generate_stages(obj)
            except NoStageTemplates as exc:
                self.message_user(
                    request,
                    f"Batch saved without a timeline: {exc}",
                    messages.WARNING,
                )

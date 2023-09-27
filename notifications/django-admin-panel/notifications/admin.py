from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    EmailTemplate,
    EmailNotificationTask,
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    search_fields = ("name", "template", "created", )
    ordering = ('created',)
    list_display = ("name", "template", "created", "modified")


@admin.register(EmailNotificationTask)
class EmailNotificationTaskAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("created", "scheduled_datetime", "sending_datetime")
    list_filter = ("priority_level", "status", "user_roles")
    list_display = (
        "name",
        "priority_level",
        "status",
        "scheduled_datetime",
        "sending_datetime",
        "template",
        "user_roles"
    )

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class EmailTemplate(UUIDMixin, TimeStampedMixin):
    template = models.TextField(_('template'))
    name = models.CharField(_('name'), max_length=255, unique=True)

    class Meta:
        db_table = "content\".\"emailtemplate"
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')


class EmailNotificationTask(UUIDMixin, TimeStampedMixin):
    class PriorityLevels(models.TextChoices):
        LOW = "low", _("low")
        MID = "mid", _("mid")
        HIGH = "high", _("high")

    class Status(models.TextChoices):
        CREATED = "created", _("created")
        IN_PROCESS = "in_process", _("in process")
        DELIVERED = "delivered", _("delivered")

    priority_level = models.CharField(
        _('priority level'),
        max_length=4,
        choices=PriorityLevels.choices,
    )
    status = models.TextField(
        _('status'),
        choices=Status.choices,
        default=Status.CREATED
    )
    # время, после которого отправляем (на сколько отложить отправку)
    scheduled_datetime = models.DateTimeField(_("scheduled timestamp"), blank=True, null=True)
    # время начала передачи
    sending_datetime = models.DateTimeField(_("sending timestamp"), blank=False, auto_now=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    # роли пользователей, кому доставим через " "
    user_roles = models.TextField(_('user roles'))

    class Meta:
        db_table = "content\".\"emailnotificationtask"
        verbose_name = _('email notification task')
        verbose_name_plural = _('email notification tasks')

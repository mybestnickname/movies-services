from rest_framework import serializers

from notifications.models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailTemplate
        fields = ("id", "created", "modified", "name", "template")

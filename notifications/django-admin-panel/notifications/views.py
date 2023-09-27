from rest_framework import generics

from notifications.models import EmailTemplate
from notifications.serializers import EmailTemplateSerializer


class EmailTemplateView(generics.RetrieveAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'template_name'

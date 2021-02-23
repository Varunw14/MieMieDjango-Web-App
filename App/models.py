from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json


class JSONField(models.TextField):
    """
    JSONField es un campo TextField que serializa/deserializa objetos JSON.
    Django snippet #1478

    Ejemplo:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)

        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()
    """

    def to_python(self, value):
        if value == "":
            return None

        try:
            if isinstance(value, str):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def from_db_value(self, value, *args):
        return self.to_python(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return value

# Create your models here.
class Module(models.Model):
    Department_Name = models.CharField(max_length=200)
    Department_ID = models.CharField(max_length=100)
    Module_Name = models.CharField(max_length=200)
    Module_ID = models.CharField(max_length=100)
    Faculty = models.CharField(max_length=200)
    Credit_Value = models.IntegerField(default=0)
    Module_Lead = models.CharField(max_length=100, null=True, blank=True)
    Catalogue_Link = models.CharField(max_length=200)
    Description = models.CharField(max_length=1000, null=True, blank=True)
    Last_Updated = models.DateTimeField

    def __str__(self):
        return self.Module_ID + ': ' + self.Module_Name

    def get_absolute_url(self):
        return f"/module/{self.pk}"
    
class Publication(models.Model):
    title = models.CharField(max_length=200, blank=True)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/publication/{self.pk}"

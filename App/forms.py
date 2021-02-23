from django import forms
from .models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["Department_Name", "Department_ID", "Module_Name", "Module_ID", "Faculty",
                  "Credit_Value", "Module_Lead", "Catalogue_Link", "Description"]


class CheckBoxForm(forms.Form):
    Modules = forms.BooleanField()
    Publications = forms.BooleanField()

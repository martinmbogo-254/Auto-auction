from django import forms

class CommaSeparatedIntegerWidget(forms.TextInput):
    def format_value(self, value):
        if value is None:
            return ''
        return "{:,}".format(value)

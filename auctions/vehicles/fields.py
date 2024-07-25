from django import forms

class CommaSeparatedIntegerField(forms.IntegerField):
    def prepare_value(self, value):
        if value is None:
            return ''
        return "{:,}".format(value)
    
    def to_python(self, value):
        if value is None:
            return None
        # Remove commas before converting to int
        value = value.replace(',', '')
        return super().to_python(value)

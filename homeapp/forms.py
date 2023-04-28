from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Name*'}))
    subject = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Subject*'}))
    email = forms.EmailField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Email Address*'}))
    message = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'formfield', 'placeholder': 'Message*'}), required=True)

class RoutePlannerForm(forms.Form):
    origin = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Origin*'}))
    endpoint = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'End Location*'}))
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Name*'}))
    subject = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Subject*'}))
    email = forms.EmailField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Email Address*'}))
    message = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'formfield', 'placeholder': 'Message*'}), required=True)

class RoutePlannerForm(forms.Form):
    origin = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Origin*', 'id': 'origin'}))
    endpoint = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'End Location*', 'id': 'endpoint'}))
    date = forms.DateField(label="Date of Travel", required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    friends = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Friends to travel with (use friend emails)*'}))

class BudgetSetterForm(forms.Form):
    car = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Name of car*'}))
    budget = forms.DecimalField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Budget*'}))
    mpg = forms.DecimalField(label="", required=True, widget=forms.TextInput(attrs={'class': 'formfield', 'placeholder': 'Miles per Gallon*'}))
    #startDate = forms.DateField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    endDate = forms.DateField(label="End Date", required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
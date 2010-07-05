from django import forms
from django.utils.translation import ugettext_lazy as _

# requires django-contact-form
from contact_form.views import contact_form
from contact_form.forms import ContactForm, attrs_dict
from django.conf import settings


class SCContactForm(ContactForm):
    """simple spam prevention for contact form- reject message body with 'http:'
    All the spam I have through contact emails has links in it.
    """
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=_('Your name'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=200)),
                             label=_('Your email address'))
    body = forms.CharField(widget=forms.Textarea(attrs=attrs_dict),
                              label=_('Your message'))
    recipient_list = [mail_tuple[1] for mail_tuple in settings.CONTACT_EMAILS]

    def clean_body(self):
        data = self.cleaned_data['body']
        if data.find('http:') > -1:
            raise forms.ValidationError("Please remove any links in your message.")

        return data
    

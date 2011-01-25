from django import forms
from django.utils.translation import ugettext_lazy as _

# requires django-contact-form
# from contact_form.views import contact_form
from contact_form.forms import ContactForm, attrs_dict
from django.conf import settings

# from bleach import Bleach


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
    

class SimpleStaticSiteContactForm(ContactForm):
    """Used to allow external static sites to send mail from a simple form.
    No error checking.
    Bleach used to clean up content.
    """
    name = forms.CharField(max_length=100, required=False)
    email = forms.CharField(max_length=200, required=False)
    body = forms.CharField(max_length=600, required=False)
    success_url = forms.CharField(max_length=200)
    fail_url = forms.CharField(max_length=200)
    subject_txt = 'contact message'
                            
    def subject(self):
        """
        Render the subject of the message to a string.
        
        """
        # subject = loader.render_to_string(self.subject_template_name,
        #                                   self.get_context())
        return self.subject_txt
    
    # def clean_name(self):
    #     """docstring for clean_name"""
    #     data = self.cleaned_data['name']
    #     return Bleach().clean(self.cleaned_data['name'])
    # 
    # def clean_email(self):
    #     data = self.cleaned_data['email']
    #     return Bleach().clean(self.cleaned_data['email'])
    # 
    # def clean_body(self):
    #     data = self.cleaned_data['body']
    #     return Bleach().clean(self.cleaned_data['body'])
    # 
    # def clean(self):
    #         cleaned_data = self.cleaned_data
    #         addr = self.request.META['SERVER_ADDR']
    #         origin = self.request.META['HTTP_REFERER']
    #         from urlparse import urlparse
    #         h = urlparse(origin)
    #         origin = h.netloc
    #                 
    #         cred = settings.EXT_CONTACTMAIL.get(origin, None)
    #     
    #         if cred and addr in cred.get('ip', []):
    #             # #     EXT_CONTACTMAIL = {
    #             #         # HTTP_ORIGIN, REMOTE_ADDR
    #             #         'http://www.ganzie.com': {'ip': ['127.0.0.1'], 'send_to': ['derek.hoy@gmail.com', 'derek@rarebits']},
    #         
    #             self.recipient_list = cred['send_to']
    #             self.subject_txt = cred['subject']
    #             return cleaned_data
    #                     
    #         raise forms.ValidationError('failed validation against settings')

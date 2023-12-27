# instagram_downloader_app/forms.py
from django import forms

class InstagramDownloadForm(forms.Form):
    post_url = forms.CharField(label='Enter Instagram Post URL')

from django import forms


class CommentForm(forms.Form):
    contents = forms.CharField(widget=forms.Textarea)


class RoomForm(forms.Form):
    subject = 
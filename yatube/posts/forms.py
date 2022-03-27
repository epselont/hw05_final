from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        text_post = self.cleaned_data['text']
        if not text_post:
            raise forms.ValidationError(
                'А кто посты за тебя писать будет, Пушкин?'
            )
        return text_post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text_comment = self.cleaned_data['text']
        if not text_comment:
            raise forms.ValidationError(
                'Автор так старался, а ты и слова написать не можешь?!'
            )
        return text_comment

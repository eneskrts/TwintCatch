from django import forms





class SearchForm(forms.Form):
    search_date = [
        ("all","Tüm Tweetler"),
        ("yil", "Son 1 Yıl"),
        ("ay", "Son 1 Ay"),
        ("hafta", "Son 1 Hafta")
    ]
    search_key = forms.CharField(label='Aranacak İfade', max_length=100)
    date_filter = forms.CharField(label="Zaman Aralığı",widget=forms.Select(choices=search_date))
    field_tweet = forms.BooleanField(label="Tweet",initial=True)
    field_hashtag = forms.BooleanField(label="Hashtag",initial=True)
    field_username = forms.BooleanField(label="Username",initial=True)
    field_name = forms.BooleanField(label="Name",initial=True)
    field_link = forms.BooleanField(label="Link",initial=True)

    field_kapsamli_arama = forms.BooleanField(label="Detay")
    field_and_vs_or = forms.BooleanField(label="Veya Sorgusu")

    def __init__(self,*args,**kwargs):
        super(SearchForm, self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].required = False
            if field in ["field_tweet","field_hashtag","field_username","field_name","field_link","field_kapsamli_arama","field_and_vs_or"]:
                self.fields[field].widget.attrs = {'class': 'form-check-input'}
                continue
            self.fields[field].widget.attrs = {'class':'form-control'}
            if field == 'search_key':
                self.fields[field].required = True


class AddAlertForm(forms.Form):
    list_aralik = [
        ("ten_minute","10 Dakikada Bir"),
        ("one_hour","Saatte Bir"),
        ("two_hour","2 Saatte Bir"),
        ("every_day","Günde Bir"),
        ("every_week","Haftada Bir")
    ]
    aranacak_ifade = forms.CharField(label="Aranacak İfade",max_length=200,required=True)
    surekli_alarm = forms.BooleanField(initial=True,label="Keyword Sürekli Taransın",required=False)
    aralik = forms.CharField(label="Zaman Aralığı",widget=forms.Select(choices=list_aralik))
    def __init__(self,*args,**kwargs):
        super(AddAlertForm, self).__init__(*args,**kwargs)
        for field in self.fields:

            if field == 'surekli_alarm':
                self.fields[field].widget.attrs = {'class': 'form-check-input'}
                continue
            else:
                self.fields[field].widget.attrs = {'class':'form-control'}
    def cleaned_surekli_alarm(self):
        cleaned = self.cleaned_data
        if cleaned.get("surekli_alarm"):
            return True
        return False
    def cleaned_aralik(self):
        cleaned = self.cleaned_data
        switcher = {
        "ten_minute":10*60,
        "one_hour":60*60,
        "two_hour":120*60,
        "every_day":24*60*60,
        "every_week":7*24*60*60
        }
 
        intervalInt = switcher.get(cleaned.get("aralik"))
        print(intervalInt)
        return intervalInt
from django import forms
from .models import Match,Player



players_obj = Player.objects.all();
players =[]
for player in players_obj:
	players.append(player.name)


class MatchForm(forms.Form):

	player1 = forms.ModelChoiceField(queryset=players_obj,label=" Player1",required=True,empty_label="Player 1",widget=forms.Select(attrs ={'class':'form-control'}))
	player2 = forms.ModelChoiceField(queryset=players_obj,label=" Player2",required=True,empty_label="Player 2",widget=forms.Select(attrs={'class':'form-control'}))
	# attrs={'class': "input-field",'data-icon'="images/sample-1.jpg"}
	GS_by_1 = forms.IntegerField(label =" GOAL SCORED BY P1",required=True,initial =0,widget = forms.NumberInput(attrs ={'class':'form-control'}))
	GS_by_2 = forms.IntegerField(label =" GOAL SCORED BY P2",required=True,initial= 0,widget = forms.NumberInput(attrs ={'class':'form-control'}))

	pin =forms.IntegerField(label ="2FA ",required=True,widget=forms.PasswordInput())

	# player_names = forms.ChoiceField(choices = players ,label ="naam ")

	
class MatchEditForm(forms.Form):

	MID = forms.IntegerField(required = True ,label="Match ID ")

	player1 = forms.ModelChoiceField(queryset =players_obj,label=" Player1",required=True,empty_label="Player 1",widget=forms.Select(attrs ={'class':'form-control'}))
	player2 = forms.ModelChoiceField(queryset=players_obj,label=" Player2",required=True,empty_label="Player 2",widget=forms.Select(attrs ={'class':'form-control'}))

	GS_by_1 = forms.IntegerField(label =" GOAL SCORED BY P1",required=True,initial =0,widget = forms.NumberInput(attrs ={'class':'form-control'}))
	GS_by_2 = forms.IntegerField(label =" GOAL SCORED BY P2",required=True,initial= 0,widget = forms.NumberInput(attrs ={'class':'form-control'}))

	pin =forms.IntegerField(label ="2FA ",required=True ,widget = forms.PasswordInput())
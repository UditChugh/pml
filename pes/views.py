from django.shortcuts import render,redirect
from django.http import HttpResponse , Http404
from .models import Player ,Match
from .forms import MatchForm,MatchEditForm
from django.contrib import messages
import json
from django.db.models import F
# Create your views here.

def home(request):

	players = Player.objects.all().order_by('-total_points' , '-total_goal_diff','-total_wins')
	

	matches = Match.objects.all().order_by('-id')[:4]
	


	return render(request , "pes/home.html",{ "players":players,"matches":matches})


def add_match(request):

	if request.method =="POST":
		form = MatchForm(request.POST)
		if form.is_valid():
			pin = form.cleaned_data.get('pin')
			if(pin != 1007):
				messages.error(request,"You Are Unauthorized To Add A Match")
				messages.error(request,"Hey Buddy Don't Do This ,This is Not Cool")
				return redirect("pes:home")


			player1_pk = form.cleaned_data.get('player1').pk
			player2_pk = form.cleaned_data.get('player2').pk

			if(player1_pk == player2_pk):
				messages.error(request,"khud ko  khudi se bhida lo ")	
				return redirect("pes:home")

			gs_by1 = form.cleaned_data.get('GS_by_1')
			gs_by2 = form.cleaned_data.get('GS_by_2')
			if(gs_by2<0 or gs_by1<0):
				messages.warning(request,"goli beta masti nai ")	
				return redirect("pes:home")

			player1 = Player.objects.get(pk = player1_pk)
			player2 = Player.objects.get(pk = player2_pk)

			win = True;
			draw =False;
			if gs_by2 > gs_by1:
				win=False
			if 	gs_by2 == gs_by1:
				draw =True
				win =False

			
			# match add krna hai , player update krne hai 1 and 2 

			m = Match(player1 = player1 ,player2 =player2 , GS_by_1 = gs_by1 ,GS_by_2=gs_by2)	
			m.save()

			player1.total_match = player1.total_match + 1
			player1.total_goal_scored = player1.total_goal_scored + gs_by1
			player1.total_goal_conceded = player1.total_goal_conceded + gs_by2
			player1.total_goal_diff = player1.total_goal_scored - player1.total_goal_conceded 


			player2.total_match = player2.total_match + 1
			player2.total_goal_scored = player2.total_goal_scored + gs_by2
			player2.total_goal_conceded = player2.total_goal_conceded + gs_by1
			player2.total_goal_diff = player2.total_goal_scored - player2.total_goal_conceded


			if win :
				player1.total_wins = player1.total_wins+1
				player1.total_points = player1.total_points +3
				player2.total_loss = player2.total_loss + 1
				messages.info(request,f"Well Done {player1.name} ")

			elif draw :
				player1.total_draw = player1.total_draw+1
				player1.total_points = player1.total_points +1
				player2.total_draw = player2.total_draw + 1	
				player2.total_points = player2.total_points +1	
				messages.info(request,f"dono ne equally haga")		

			else:
				player2.total_wins = player2.total_wins+1
				player2.total_points = player2.total_points +3
				player1.total_loss = player1.total_loss + 1
				messages.info(request,f"Well Done {player2.name} ")
			
			player1.save()
			player2.save()
			messages.success(request ,f"MATCH ADDED SUCCESFULLY ")

			return redirect ("pes:home")
		
	form = MatchForm()
	players =Player.objects.all()
	title ="ADD MATCH"
	return render(request , "pes/try.html",{ "players":players, "form":form,"title":title,"iseditform":False})

	
def matches(request):
	
	all_matches = 	Match.objects.all().order_by('-id')


	return render(request , "pes/includes/match.html",{ "all_matches":all_matches})
			
def edit_match(request):

	if request.method =="POST":
		form = MatchEditForm(request.POST)
		if form.is_valid():
			pin = form.cleaned_data.get('pin')
			if(pin != 5302):
				messages.error(request,"You Are Unauthorized To EDIT A Match")
				messages.error(request,"Hey Buddy Don't Do This ,This is Not Cool")
				return redirect("pes:home")

			mid = form.cleaned_data.get('MID')

			m = list(Match.objects.filter(id = mid ))

			if (len(m ) == 0):
				messages.error(request,"koi esa match hi nai hai ")
				return redirect("pes:home")

			m = m[0]
			
			# match subtract krna hai , player update krne hai 1 and 2 
			

			m_player1 = m.player1
			m_player2 = m.player2
			m_gs_by1 = m.GS_by_1 
			m_gs_by2 =m.GS_by_2

			m_win = True;
			m_draw =False;
			if m_gs_by2 > m_gs_by1:
				m_win=False
			if 	m_gs_by2 == m_gs_by1:
				m_draw =True
				m_win =False

			m_player1.total_match = m_player1.total_match - 1
			m_player1.total_goal_scored = m_player1.total_goal_scored - m_gs_by1
			m_player1.total_goal_conceded = m_player1.total_goal_conceded - m_gs_by2
			m_player1.total_goal_diff = m_player1.total_goal_scored - m_player1.total_goal_conceded 

			m_player2.total_match = m_player2.total_match - 1
			m_player2.total_goal_scored = m_player2.total_goal_scored - m_gs_by2
			m_player2.total_goal_conceded = m_player2.total_goal_conceded - m_gs_by1
			m_player2.total_goal_diff = m_player2.total_goal_scored - m_player2.total_goal_conceded 

			if m_win :
				m_player1.total_wins = m_player1.total_wins-1
				m_player1.total_points = m_player1.total_points -3
				m_player2.total_loss = m_player2.total_loss - 1
				

			elif m_draw :
				m_player1.total_draw = m_player1.total_draw-1
				m_player1.total_points = m_player1.total_points -1
				m_player2.total_draw = m_player2.total_draw - 1	
				m_player2.total_points = m_player2.total_points -1	
					

			else:
				m_player2.total_wins = m_player2.total_wins-1
				m_player2.total_points = m_player2.total_points -3
				m_player1.total_loss = m_player1.total_loss - 1
				
			m_player1.save()
			m_player2.save()


			player1_pk = form.cleaned_data.get('player1').pk
			player2_pk = form.cleaned_data.get('player2').pk

			if(player1_pk == player2_pk):
				messages.error(request,"khud ko  khudi se bhida lo ")	
				return redirect("pes:home")

			gs_by1 = form.cleaned_data.get('GS_by_1')
			gs_by2 = form.cleaned_data.get('GS_by_2')
			if(gs_by2<0 or gs_by1<0 or gs_by1 >20 or gs_by2>20):
				messages.warning(request,"goli beta masti nai ")	
				return redirect("pes:home")

			if(gs_by1>4 or gs_by2 >4):
				messages.info(request,"ranjan khel rha tha kya itne goal pdwa lie")

			player1 = Player.objects.get(pk = player1_pk)
			player2 = Player.objects.get(pk = player2_pk)

			win = True;
			draw =False;
			if gs_by2 > gs_by1:
				win=False
			if 	gs_by2 == gs_by1:
				draw =True
				win =False

			player1.total_match = player1.total_match + 1
			player1.total_goal_scored = player1.total_goal_scored + gs_by1
			player1.total_goal_conceded = player1.total_goal_conceded + gs_by2
			player1.total_goal_diff = player1.total_goal_scored - player1.total_goal_conceded 


			player2.total_match = player2.total_match + 1
			player2.total_goal_scored = player2.total_goal_scored + gs_by2
			player2.total_goal_conceded = player2.total_goal_conceded + gs_by1
			player2.total_goal_diff = player2.total_goal_scored - player2.total_goal_conceded


			if win :
				player1.total_wins = player1.total_wins+1
				player1.total_points = player1.total_points +3
				player2.total_loss = player2.total_loss + 1
				messages.info(request,f"Well Done {player1.name} ")

			elif draw :
				player1.total_draw = player1.total_draw+1
				player1.total_points = player1.total_points +1
				player2.total_draw = player2.total_draw + 1	
				player2.total_points = player2.total_points +1	
				messages.info(request,f"dono ne equally haga")		

			else:
				player2.total_wins = player2.total_wins+1
				player2.total_points = player2.total_points +3
				player1.total_loss = player1.total_loss + 1
				messages.info(request,f"Well Done {player2.name} ")
			
			player1.save()
			player2.save()
			messages.success(request ,f"MATCH EDITED SUCCESFULLY ")
			m.player1 = player1
			m.player2 =player2
			m.GS_by_1 =gs_by1
			m.GS_by_2 = gs_by2 
			m.save()
			return redirect ("pes:home")
		
	form = MatchEditForm()
	players =Player.objects.all()
	title ="EDIT MATCH"
	return render(request , "pes/try.html",{ "players":players, "form":form ,"title":title,"iseditform":True})

def player(request,id):

	try:
		curr_player = Player.objects.get(id =id)
	except Player.DoesNotExist:
		raise Http404("PLAYER does not exist")


	matches_p1 = Match.objects.filter(player1 = curr_player)

	matches_p2 = Match.objects.filter(player2 = curr_player)

	players = Player.objects.exclude(id = id).order_by('-total_points')
	# players = Player.objects.filter(id = 2)

	records ={}

	for player in players:

		as_p1 = matches_p1.filter(player2 = player)
		as_p2 = matches_p2.filter(player1 = player)
		tm = len(as_p1) + len(as_p2)
		wins =0
		winp =0
		loss =0
		
		if(tm > 0):

			wins =  as_p1.filter(GS_by_1__gt = F('GS_by_2')).count()+as_p2.filter(GS_by_2__gt = F('GS_by_1') ).count() 
			loss =as_p1.filter(GS_by_1__lt = F('GS_by_2')).count()+as_p2.filter(GS_by_2__lt = F('GS_by_1') ).count()
			winp =  (wins/tm) *100

		records[player] = {
				'm':tm,
				'w':wins,
				'd':tm - wins - loss,
				'l':loss,
				'wp': round(winp,2),


		}

	matches = matches_p1.union(matches_p2)



	matches = matches.order_by('-id')[:6]

	ids = [match.id for match in matches]

	matches = Match.objects.filter(pk__in=ids).order_by('-id')

	matches_p1 =matches.filter(player1 = curr_player)

	matches_p2 = matches.filter(player2 = curr_player)

	tm = len(matches_p1) + len(matches_p2)
	wins =0
	winp =0
	loss =0
		
	if(tm > 0):

		wins =  matches_p1.filter(GS_by_1__gt = F('GS_by_2')).count()+matches_p2.filter(GS_by_2__gt = F('GS_by_1') ).count() 
		loss =matches_p1.filter(GS_by_1__lt = F('GS_by_2')).count()+matches_p2.filter(GS_by_2__lt = F('GS_by_1') ).count()
		winp =  (wins/tm) *100

	draws = tm -wins -loss
	
	form =0


	if tm >0: 

		form =(wins*3 + draws)/(tm*3)

		form_class = 'GOOD'


	if(form <= 0.4):
		form_class = 'NOT GREAT'
	elif (form < 0.7):
		form_class ='DESCENT'	



	rank = 1;
	players = Player.objects.all().order_by('-total_points' , '-total_goal_diff','-total_wins')

	for player in players:
		if player.id == curr_player.id:
			break
		rank +=1 	
	winp =0
	if curr_player.total_match >0:
		winp = (curr_player.total_wins /curr_player.total_match)*100
		
	mydict ={"curr_player":curr_player,"players":players ,
	'records':records ,'matches':matches,
	'form_class':form_class,'form':form,
	'rank':rank,'winp':round(winp,2),
	}
	



	return render(request , "pes/player.html" ,mydict)
	# return HttpResponse(json.dumps({"lat":player.id, "lng":player.name}), content_type="application/json")

def clubs(request):
	players = list( Player.objects.all().order_by('-total_points' , '-total_goal_diff','-total_wins') )

	curr_champion = players[0]

	return render(request , "pes/clubs.html",{'players':players , 'curr_champion':curr_champion})
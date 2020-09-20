from django.shortcuts import render,redirect
from django.http import HttpResponse , Http404
from .models import Player ,Match
from .forms import MatchForm,MatchEditForm,MatchPredictForm
from django.contrib import messages
import json
from django.db.models import F
import pandas as pd
import queue 
import pickle






def data_for_predict(player1_pred ,id_p1,player2_pred,id_p2):


	data_dict_pred = {

		'p1':[]
		,'matches_played_p1':[]
		,'avg_gs_p1':[]
		,'avg_gc_p1':[]
		,'form_p1':[]
		,'winper_p1':[]
		,'lossper_p1':[]
		,'drawper_p1':[]
		,'l5avg_gs_p1':[]
		,'l5avg_gc_p1':[]
		,'p2':[]
		,'matches_played_p2':[]
		,'avg_gs_p2':[]
		,'avg_gc_p2':[]
		,'form_p2':[]
		,'winper_p2':[]
		,'lossper_p2':[]
		,'drawper_p2':[]
		,'l5avg_gs_p2':[]
		,'l5avg_gc_p2':[],
		





	}

	p1 =player1_pred
	p2 =player2_pred
	avggs_l5 = 0
	avggc_l5 =0 
	form =0 
	for i in p1.gslist[-5:]:
		avggs_l5 +=i
	for i in p1.gclist[-5:]:
		avggc_l5 +=i	

	for i in p1.pointslist[-5:]:
		form +=i
		
	print("matches " ,p1.matches_played ," ",p1.Name)	

	data_dict_pred['p1'].append(id_p1 )
	data_dict_pred['matches_played_p1'].append(p1.matches_played)
	data_dict_pred['avg_gs_p1'].append(round(p1.goal_scored  / p1.matches_played ,2) )
	data_dict_pred['avg_gc_p1'].append(round(p1.goal_conceded / p1.matches_played ,2) )
	data_dict_pred['form_p1'].append(form)
	data_dict_pred['winper_p1'].append(round(p1.wins / p1.matches_played ,2) )
	data_dict_pred['lossper_p1'].append(round(p1.loss / p1.matches_played ,2))
	data_dict_pred['drawper_p1'].append(round(p1.draws / p1.matches_played ,2))
	data_dict_pred['l5avg_gs_p1'].append(avggs_l5)
	data_dict_pred['l5avg_gc_p1'].append(avggc_l5)



	avggs_l5 = 0
	avggc_l5 =0 
	form =0 
	for i in p2.gslist[-5:]:
		avggs_l5 +=i
	for i in p2.gclist[-5:]:
		avggc_l5 +=i
	for i in p1.pointslist[-5:]:
		form +=i	

	data_dict_pred['p2'].append(id_p2)
	data_dict_pred['matches_played_p2'].append(p2.matches_played)
	data_dict_pred['avg_gs_p2'].append(round(p2.goal_scored  / p2.matches_played  ,2))
	data_dict_pred['avg_gc_p2'].append(round(p2.goal_conceded / p2.matches_played ,2) )
	data_dict_pred['form_p2'].append(form)
	data_dict_pred['winper_p2'].append(round(p2.wins / p2.matches_played ,2) )
	data_dict_pred['lossper_p2'].append(round(p2.loss / p2.matches_played ,2))
	data_dict_pred['drawper_p2'].append(round(p2.draws / p2.matches_played ,2))
	data_dict_pred['l5avg_gs_p2'].append(round(avggs_l5 ,2))
	data_dict_pred['l5avg_gc_p2'].append(round(avggc_l5 ,2))



	

	df = pd.DataFrame(data_dict_pred)

	# pd.get_dummies(df['p1'])
	# df = pd.concat([df,pd.get_dummies(df['p1'], prefix='p1')],axis=1)
	# pd.get_dummies(df['p2'])
	# df = pd.concat([df,pd.get_dummies(df['p2'], prefix='p2')],axis=1)
	# now drop the original 'country' column (you don't need it anymore)

	for i in range(1,7):
		col ='p1_'+str(i)
		df[col]=0;
		if(i == id_p1):
			df[col] =1
	for i in range(1,7):
		col ='p2_'+str(i)
		df[col]=0;
		if(i == id_p2):
			df[col] =1



	df.drop(['p1'],axis=1,inplace =True)
	df.drop(['p2'],axis=1,inplace =True)

	
	return  df.to_numpy()

# Create your views here.







def home(request):

	players = Player.objects.all().order_by('-total_points' , '-total_goal_diff','-total_wins')
	

	matches = Match.objects.all().order_by('-id')[:4]

	print("hello")

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


def dataset(request):
	
	print(lop[1].goal_scored ," goal scored")
	print("matches " ,lop[0].matches_played ," ",lop[0].Name)
	if request.method =="POST":
		form = MatchPredictForm(request.POST)
		if form.is_valid():


			player1 = form.cleaned_data.get('player1')
			player2 = form.cleaned_data.get('player2')
			id_p1 =player1.id
			id_p2 =player2.id
			if(id_p1 == id_p2):
				messages.error(request,"Yaar ese to na kro please ")	


				return redirect("pes:home")

			player1 = lop[id_p1 -1]
			player2 = lop[id_p2 -1]

			
			data =  data_for_predict(player1 , id_p1 ,player2,id_p2)

			# scaled_data = scaler.fit_transform(data)
			rf = pickle.load(open('rf_model.sav','rb'))
			lr = pickle.load(open('lr_model.sav','rb'))
			rf_1 = pickle.load(open('rf_model_1.sav','rb'))
			scaler = pickle.load(open('scaler1.sav','rb'))
			print(data.shape ," this is the shape of data ")

			data = scaler.transform(data)
			prediction = rf.predict(data)

			prediction_1 =rf_1.predict(data)
			winner = 'draw'

			if prediction == 1:
				winner = player1.Name
				winner =Player.objects.get(id = id_p1)
			if prediction == 0:
				winner = player2.Name
				winner =Player.objects.get(id = id_p2)

			return render(request , "pes/ml.html",{'form':form , 'data':data,'Winner':winner ,'prediction_1':prediction_1})


	form = MatchPredictForm()

	return render(request , "pes/ml.html",{'form':form})	


# def update_csv(request):
# 	update_data()
# 	return HttpResponse("updated csv fro  database")

	
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





class PLAYER:
		
		def __init__(self ,Name ,goal_scored,goal_conceded ,matches_played,form_tn,wins,loss,draws,pts):
				self.Name = Name
				self.goal_scored = goal_scored
				self.goal_conceded = goal_conceded
				self.matches_played = matches_played
				self.form_tn = form_tn
				self.wins = wins

				self.loss = loss
				self.draws = draws
				self.pts = pts
				self.draws = matches_played - wins - loss 

				self.winper = wins
				self.gslist =list()
				self.l5gs = 0
				self.gclist =list()
				self.l5gc = 0
				self.pointslist=list()

				self.l5points =0

data_dict = {

			'p1':[]
			,'matches_played_p1':[]
			,'avg_gs_p1':[]
			,'avg_gc_p1':[]
			,'form_p1':[]
			,'winper_p1':[]
			,'lossper_p1':[]
			,'drawper_p1':[]
			,'l5avg_gs_p1':[]
			,'l5avg_gc_p1':[]
			,'p2':[]
			,'matches_played_p2':[]
			,'avg_gs_p2':[]
			,'avg_gc_p2':[]
			,'form_p2':[]
			,'winper_p2':[]
			,'lossper_p2':[]
			,'drawper_p2':[]
			,'l5avg_gs_p2':[]
			,'l5avg_gc_p2':[],
			'winner':[]
}

lop =[]


for players in Player.objects.all().order_by('id'):

		lop.append(PLAYER(Name = players.name ,goal_scored =0 ,goal_conceded=0 ,matches_played =0
			,form_tn =0 ,wins=0,loss =0 ,draws = 0,pts =0  ))
count_1 =0
count_0 =0
count_tm = 0	
for match in Match.objects.all():

			
		player1 = match.player1
		player2 = match.player2 

		p1_gs = match.GS_by_1
		p2_gs = match.GS_by_2

		p1 = lop[player1.id-1]
		p2 = lop[player2.id-1]

		p1.goal_scored = p1.goal_scored + p1_gs
		p1.goal_conceded = p1.goal_conceded +p2_gs
		p1.matches_played = p1.matches_played +1


		p2.goal_scored = p2.goal_scored + p2_gs
		p2.goal_conceded = p2.goal_conceded +p1_gs
		p2.matches_played = p2.matches_played +1

		win = True;
		draw =False;
		if p2_gs > p1_gs:
			win=False
		if 	p2_gs ==  p1_gs:
			draw =True
			win =False

				
		if (abs(count_1 -count_0) > 3 ):
			player1,player2 = player2,player1
			p1,p2 =p2,p1
			p1_gs,p2_gs =p2_gs,p1_gs
			win =False

		if win:
			count_1+=1
		elif draw:
			pass
		else:
			count_0+=1
		
		# check  whether our data is balanced till now or not and balance it accordingly

		



		
		# draw = 2 ;;;;;; p1_wins = 1 ;;;;; p2_wins = 0

		if win :
			p1.wins = p1.wins+1
			p1.pts = p1.pts +3
			p1.pointslist.append(3)
			p2.loss = p2.loss+1
			data_dict['winner'].append(1)


				

				
		elif draw :
			p1.draws = p1.draws +1 
			p1.pts =p1.pts+1
			p2.draws = p2.draws +1 
			p2.pts =p2.pts +1
			p1.pointslist.append(1)
			p1.pointslist.append(1)
			data_dict['winner'].append(2)


				
				

		else:
			p2.wins = p2.wins+1
			p2.pts = p2.pts +3
			p1.loss = p1.loss+1
			p2.pointslist.append(3)
			data_dict['winner'].append(0)
				
				


		

		p1.gslist.append(p1_gs)
		p2.gslist.append(p2_gs)
		p1.gclist.append(p2_gs)
		p2.gclist.append(p1_gs)

		avggs_l5 = 0
		avggc_l5 =0 
		form =0 
		for i in p1.gslist[-5:]:
			avggs_l5 +=i
		for i in p1.gclist[-5:]:
			avggc_l5 +=i	

		for i in p1.pointslist[-5:]:
			form +=i
			
			

		data_dict['p1'].append(player1.id)
		data_dict['matches_played_p1'].append(p1.matches_played)
		data_dict['avg_gs_p1'].append(round(p1.goal_scored  / p1.matches_played ,2) )
		data_dict['avg_gc_p1'].append(round(p1.goal_conceded / p1.matches_played ,2) )
		data_dict['form_p1'].append(form)
		data_dict['winper_p1'].append(round(p1.wins / p1.matches_played ,2) )
		data_dict['lossper_p1'].append(round(p1.loss / p1.matches_played ,2))
		data_dict['drawper_p1'].append(round(p1.draws / p1.matches_played ,2))
		data_dict['l5avg_gs_p1'].append(avggs_l5)
		data_dict['l5avg_gc_p1'].append(avggc_l5)


			

		avggs_l5 = 0
		avggc_l5 =0 
		form =0 
		for i in p2.gslist[-5:]:
			avggs_l5 +=i
		for i in p2.gclist[-5:]:
			avggc_l5 +=i
		for i in p1.pointslist[-5:]:
			form +=i	

		data_dict['p2'].append(player2.id)
		data_dict['matches_played_p2'].append(p2.matches_played)
		data_dict['avg_gs_p2'].append(round(p2.goal_scored  / p2.matches_played  ,2))
		data_dict['avg_gc_p2'].append(round(p2.goal_conceded / p2.matches_played ,2) )
		data_dict['form_p2'].append(form)
		data_dict['winper_p2'].append(round(p2.wins / p2.matches_played ,2) )
		data_dict['lossper_p2'].append(round(p2.loss / p2.matches_played ,2))
		data_dict['drawper_p2'].append(round(p2.draws / p2.matches_played ,2))
		data_dict['l5avg_gs_p2'].append(round(avggs_l5 ,2))
		data_dict['l5avg_gc_p2'].append(round(avggc_l5 ,2))
df = pd.DataFrame.from_dict(data_dict)
print("hello inside ml ")
print(df.head())
df.to_csv('mydata.csv')	 	





from django.db import models
from django.db.models import Count
# Create your models here.


# class Season(models.Model):
# 	no = models.IntegerField(default = 0)
# 	curr_champian = models.ForeignKey(Player , on_delete=models.CASCADE ,related_name='player1')
# 	tmp= models.IntegerField(default = 0)
# 	no_of_players= models.IntegerField(default = 0)


	# def __str__ (self):
	# 	return self.no




class Player(models.Model):
	name = models.CharField(max_length = 30)
	logo =models.ImageField(upload_to='pictures' ,null =True , blank =True ,default ='default.jpg' )
	abbr = models.CharField(max_length = 7 ,default ="FCB" )
	manager = models.CharField(max_length = 30 ,default = 'unknown')


	total_match = models.IntegerField()
	total_points = models.IntegerField(default = 0)
	
	total_wins = models.IntegerField()
	total_loss = models.IntegerField()
	total_draw = models.IntegerField()

	total_goal_scored = models.IntegerField()
	total_goal_conceded = models.IntegerField()
	total_goal_diff = models.IntegerField(default =0)

	# def ranking(self):
	# 	aggregate = Player.objects.filter(total_points__gt=self.total_points).aggregate(ranking=Count('total_points'))
	# 	return aggregate['ranking'] + 1



	def __str__ (self):
		return self.name

class Match(models.Model):
#	season = models.ForeignKey(Seasom ,on_delete=models.CASCADE ,related_name='season' ,)
	player1 = models.ForeignKey(Player , on_delete=models.CASCADE ,related_name='player1' )
	player2 = models.ForeignKey(Player , on_delete=models.CASCADE ,related_name='player2' )

	GS_by_1 = models.IntegerField()
	GS_by_2 = models.IntegerField()



	def __str__ (self):
		return f"match no  {self.id}"




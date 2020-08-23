from django.db import models

# Create your models here.


class Player(models.Model):
	name = models.CharField(max_length = 30)

	total_match = models.IntegerField()
	total_points = models.IntegerField(default = 0)
	
	total_wins = models.IntegerField()
	total_loss = models.IntegerField()
	total_draw = models.IntegerField()

	total_goal_scored = models.IntegerField()
	total_goal_conceded = models.IntegerField()
	total_goal_diff = models.IntegerField(default =0)





	def __str__ (self):
		return self.name

class Match(models.Model):

	player1 = models.ForeignKey(Player , on_delete=models.CASCADE ,related_name='player1' )
	player2 = models.ForeignKey(Player , on_delete=models.CASCADE ,related_name='player2' )

	GS_by_1 = models.IntegerField()
	GS_by_2 = models.IntegerField()


	def __str__ (self):
		return f"match no  {self.id}"




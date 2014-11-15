import json, random, math
from communication import Communication
class Algorithm():
	def run(self):
		self.com.receive(Communication.Origin.PublishSocket)
		a = json.loads(self.com.receive(Communication.Origin.PublishSocket))
		if a['comm_type'] == 'GAME_END': print "Game ended"
		if a['comm_type'] != 'GAMESTATE': return
		token = self.gameinfo.client_token
		player = [x for x in a[u'players'] if x['name']=='teamasdf'][0]
		opponent = [x for x in a[u'players'] if x['name']!='teamasdf'][0]
		print "Us: %3d Them: %3d Time remaining: %5d" % (player['score'], opponent['score'], a['timeRemaining'])
		for tank in player['tanks'] + opponent['tanks']:
			if tank['projectiles']:
				self.bulletSpeed = tank['projectiles'][0]['speed']
		for tank in player['tanks']:
			tank_id = tank['id']
			self.send({'comm_type':'MOVE','client_token':token,'direction':'FWD','distance':random.random() * 10,'tank_id':tank_id})
			if not random.randint(0,25):
				self.send({'comm_type':'ROTATE','client_token':token,'direction':'CCW' if random.randint(0,100) else 'CW','rads':random.random() * 3,'tank_id':tank_id})
			
			closest_opponent_pos = [float("inf"),float("inf")]
			should_shoot = False
			for enemy in opponent['tanks']:
				if not enemy['alive']: continue
				# Get closest enemy
				dist_enemy = (enemy['position'][0]-tank['position'][0])**2+(enemy['position'][1]-tank['position'][1])**2
				closest_enemy = (closest_opponent_pos[0]-tank['position'][0])**2+(closest_opponent_pos[1]-tank['position'][1])**2
				if(dist_enemy < closest_enemy):
					closest_opponent_pos = enemy['position']
					closest_tank_id = enemy['id']
				# Check if we should shoot
				angle = self.atan2positive(enemy['position'][1]-tank['position'][1], enemy['position'][0]-tank['position'][0])-tank['turret']
				# Only shoot if we are within 9 degrees of an opponent
				if math.fabs(angle) < math.pi/20.0:
					should_shoot = True
			if closest_opponent_pos[0] != float("inf") and hasattr(self, 'bulletSpeed'):
				if hasattr(self, 'last_opponent'):
					prevpos = [x for x in self.last_opponent['tanks'] if x['id']==closest_tank_id]
					if prevpos:
						prevpos = prevpos[0]['position']
						dt = 0.001 * (a['timestamp'] - self.last_a['timestamp'])
						v = [(closest_opponent_pos[0] - prevpos[0]) / dt,(closest_opponent_pos[1] - prevpos[1]) / dt]
						bt = math.sqrt(math.pow(closest_opponent_pos[0]-tank['position'][0], 2)+ math.pow(closest_opponent_pos[1]-tank['position'][1], 2))/self.bulletSpeed
						interpolate = [closest_opponent_pos[0]+bt*v[0], closest_opponent_pos[1]+bt*v[1]]
						#print closest_opponent_pos, interpolate
						closest_opponent_pos = interpolate
				calc = self.atan2positive(closest_opponent_pos[1]-tank['position'][1], closest_opponent_pos[0]-tank['position'][0])
				diff = calc-tank['turret']
				self.send({'comm_type':'ROTATE_TURRET','client_token':token,'direction':'CCW' if diff>0 else 'CW','rads':math.fabs(diff),'tank_id':tank_id})
				if should_shoot:
					self.send({'comm_type':'FIRE','client_token':token,'tank_id':tank_id})
		self.last_opponent = opponent
		self.last_a = a
				
	def __init__(self,client):
		self.com = client.comm
		self.gameinfo = client.game_info
		while 1: self.run()
	def send(self, stuff):
		self.com.send(json.dumps(stuff))
	def atan2positive(self, a, b):
		c = math.atan2(a, b)
		if c < 0: c += 2*math.pi
		return c

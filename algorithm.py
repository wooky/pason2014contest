from communication import Communication
import json,random,math
class Algorithm():
	def __init__(self,client):
		self.com = client.comm
		self.gameinfo = client.game_info
		while 1: self.run()

	def run(self):
		self.com.receive(Communication.Origin.PublishSocket)
		a = json.loads(self.com.receive(Communication.Origin.PublishSocket))
		if a['comm_type'] != 'GAMESTATE': return
		token = self.gameinfo.client_token
		player = [x for x in a[u'players'] if x['name']=='teamasdf'][0]
		opponent = [x for x in a[u'players'] if x['name']!='teamasdf'][0]
		for tank in player['tanks']:
			tank_id = tank['id']
			cmd = {'comm_type':'FIRE','client_token':token,'tank_id':tank_id}
			self.com.send(json.dumps(cmd))
			cmd = {'comm_type':'MOVE','client_token':token,'direction':'FWD' if random.randint(0,50) else 'REV','distance':random.random() * 10,'tank_id':tank_id}
			self.com.send(json.dumps(cmd))
			if not random.randint(0,25):
				cmd = {'comm_type':'ROTATE','client_token':token,'direction':'CCW' if random.randint(0,100) else 'CW','rads':random.random() * 3,'tank_id':tank_id}
				self.com.send(json.dumps(cmd))
			
			closest_opponent_pos = [float("inf"),float("inf")]
			for enemy in opponent['tanks']:
				dist_enemy = (enemy['position'][0]-tank['position'][0])**2+(enemy['position'][1]-tank['position'][1])**2
				closest_enemy = (closest_opponent_pos[0]-tank['position'][0])**2+(closest_opponent_pos[1]-tank['position'][1])**2
				if(dist_enemy < closest_enemy): closest_opponent_pos = enemy['position']
			#TODO: if no enemy don't do anything
			calc = math.atan2(closest_opponent_pos[1]-tank['position'][1], closest_opponent_pos[0]-tank['position'][0])
			if calc < 0: calc += 2*math.pi
			diff = calc-tank['turret']
			cmd = {'comm_type':'ROTATE_TURRET','client_token':token,'direction':'CCW' if diff>0 else 'CW','rads':math.fabs(diff),'tank_id':tank_id}
			self.com.send(json.dumps(cmd))
				

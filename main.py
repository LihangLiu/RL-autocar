import numpy as np
import subprocess as sp
import math
import time
from random import randint, random


STOP = 0
UP = 1
DOWN = 2
RIGHT1STEP = 3
RIGHT2STEP = 4
RIGHT3STEP = 5
LEFT1STEP = 6
LEFT2STEP = 7
LEFT3STEP = 8

class Pos:
	def __init__(self, x, y, W=15, H=4):
		self.x = x
		self.y = y
		self.W = W
		self.H = H
	def move(self, action):
		if action == STOP:
			return [self]
		elif action == UP:
			return self.up()
		elif action == DOWN:
			return self.down()
		elif action == RIGHT1STEP:
			return self.right(1)
		elif action == RIGHT2STEP:
			return self.right(2)
		elif action == RIGHT3STEP:
			return self.right(3) 
		elif action == LEFT1STEP:
			return self.left(1)
		elif action == LEFT2STEP:
			return self.left(2)
		elif action == LEFT3STEP:
			return self.left(3)
		else:
			print 'wrong action ', action
			exit(0)
	def up(self):
		if self.y <= 0:
			return [Pos(self.x, 0)]
		return [Pos(self.x, self.y-1)]

	def down(self):
		if self.y+1 >= self.H:
			return [Pos(self.x, self.H-1)]
		return [Pos(self.x, self.y+1)]

	def right(self, offset):
		if self.x+1 >= self.W:
			return [Pos(self.W-1, self.y)]
		trajt = []
		for off in range(1,1+offset):
			if self.x+off < self.W:
				trajt.append(Pos(self.x+off, self.y))
		return trajt

	def left(self, offset):
		if self.x-1 < 0:
			return [Pos(0, self.y)]
		trajt = []
		for off in range(1,1+offset):
			if self.x-off >= 0:
				trajt.append(Pos(self.x-off, self.y))
		return trajt

	def toInt(self):
		return self.x + self.y*self.W
	def cout(self):
		print '(%d,%d)' % (self.x, self.y)


EMPTY = 0
MY_CAR = 1
LEFT_CAR = 2
RIGHT_CAR = 3
PARKING = 4
PEDESTRIAN = 5
YELLOW = 6
RED = 7
GREEN = 8 
COLLISION = 9
symbol_dict = {EMPTY: '_',
				MY_CAR: 'o',
				LEFT_CAR: '<',
				RIGHT_CAR: '>',
				PARKING: 'X',
				PEDESTRIAN: 'I',
				YELLOW: 'Y',
				RED: 'R',
				GREEN: 'G',
				COLLISION: 'Q'}

class Object:
	def __init__(self, W=15, H=4):
		self.W = W
		self.H = H

	def getPos(self):
		assert (len(self.trajt)>0), self.trajt
		return self.trajt[-1]

	def randomMove(self):
		self.trajt = self.ntrajt
		self._preMove()

	def _preMove(self):
		action = self.action_list[randint(0,len(self.action_list)-1)]
		self.ntrajt = self.getPos().move(action)

class Parking(Object):
	def __init__(self):
		Object.__init__(self)
		self.id = PARKING
		self.trajt = [Pos(randint(0,self.W-1),randint(0,self.H-1))]
		self.action_list = [STOP]
		self._preMove()

class LeftCar(Object):
	def __init__(self):
		Object.__init__(self)
		self.id = LEFT_CAR
		self.trajt = [Pos(randint(0,self.W-1),randint(0,1))]
		self._preMove()

	def _preMove(self):
		assert self.getPos().y in [0,1]
		if self.getPos().y == 1:
			self.action_list = [STOP,UP,LEFT1STEP,LEFT2STEP]
		elif self.getPos().y == 0:
			self.action_list = [STOP,DOWN,LEFT1STEP,LEFT2STEP]
		else:
			print "leftcar error", self.getPos().y
			exit(0)
		Object._preMove(self)
		self.check()

	def check(self):
		if self.getPos().x == 0:
			self.ntrajt = [Pos(self.W-1,randint(0,1))]

class RightCar(Object):
	def __init__(self):
		Object.__init__(self)
		self.id = RIGHT_CAR
		self.trajt = [Pos(randint(0,self.W-1),randint(2,3))]
		self._preMove()

	def _preMove(self):
		assert self.getPos().y in [2,3]
		if self.getPos().y == 3:
			self.action_list = [STOP,UP,RIGHT1STEP,RIGHT2STEP]
		elif self.getPos().y == 2:
			self.action_list = [STOP,DOWN,RIGHT1STEP,RIGHT2STEP]
		else:
			print "rightcar error", self.getPos().y
			exit(0)
		Object._preMove(self)
		self.check()

	def check(self):
		if self.getPos().x == self.W-1:
			self.ntrajt = [Pos(0,randint(2,3))]

class Pedestrian(Object):
	def __init__(self):
		Object.__init__(self)
		self.id = PEDESTRIAN
		self.trajt = [Pos(randint(0,self.W-1),0)]
		self.action_list = [STOP,DOWN]
		self._preMove()

	def _preMove(self):
		Object._preMove(self)
		self.check()

	def check(self):
		if self.getPos().y == self.H-1:
			self.ntrajt = [Pos(randint(0,self.W-1),0)]

class Brain:
	def getQAction(self, s):
		qactions = self.Q[s,:]
		if random() < self.epsilon:
			maxaction = self.getRandomAction()
		else:
			maxaction = np.argmax(qactions)
		maxQ = qactions[maxaction]
		return maxaction, maxQ

	def getRandomAction(self):
		return my_car_action_list[randint(0,len(my_car_action_list)-1)]

	def updateQ(self, s, a, s_, a_, r):
		self.Q[s,a] += self.alpha*(r+self.gamma*self.Q[s_,a_]-self.Q[s,a])

class LocalBrain(Brain):
	def __init__(self):
		self.alpha = 0.7
		self.gamma = 0.4
		self.epsilon = 0.1
		self.Q = np.random.rand(64, len(my_car_action_list))*0.1-0.05

	def getState(self, agent, cpos):
		lanes = agent.nextTrajtLanes()
		pos_list = []
		for a in my_car_action_list:
			pos_list.append(cpos.move(a)[-1])
		f = []
		for p in pos_list:
			if agent.getLane(lanes, p) not in [EMPTY,MY_CAR]:
				f.append(1)
			else:
				f.append(0)
		return agent.bin_2_int(f)

	def getReward(self, cpos, a, nextTrajt, all_obj_trajts, ifHit):
		r = 0
		if ifHit:
			r += -10
		return r

class ImproveLocalBrain(LocalBrain):
	def getReward(self, cpos, a, nextTrajt, all_obj_trajts, ifHit):
		r = 0
		if a == STOP:
			r += -3
		elif a in [UP,DOWN]:
			r += -1
		elif a in [RIGHT1STEP, RIGHT2STEP, RIGHT3STEP]:
			r += len(nextTrajt)
		else:
			print 'wrong a', a
		if ifHit:
			r += -10
		return r

class GlobalBrain(Brain):
	def __init__(self):
		self.alpha = 0.4
		self.gamma = 0.7
		self.epsilon = 0.1
		self.Q = np.random.rand(64, len(my_car_action_list))*0.1-0.05

	def getState(self, agent, cpos):
		return cpos.toInt()

	def getReward(self, cpos, a, nextTrajt, all_obj_trajts, ifHit):
		r = 0
		# if a == STOP:
		# 	r += -2
		# elif a in [UP,DOWN]:
		# 	r += -1
		# elif a in [RIGHT1STEP, RIGHT2STEP, RIGHT3STEP]:
		# 	r += len(nextTrajt)
		# else:
		# 	print 'wrong a', a
		# if ifHit:
		# 	r += -10
		if nextTrajt[-1].x == W-1:
			r += 20
		return r


my_car_action_list = [STOP, UP, DOWN, RIGHT1STEP, RIGHT2STEP, RIGHT3STEP]

METHOD_LOCAL = 0
METHOD_GLOGAL = 1
METHOD_LOCAL_GLOGAL = 2
METHOD_IMPROVED_LOCAL = 3

class Agent:
	def __init__(self, method = METHOD_IMPROVED_LOCAL):
		assert (method in [METHOD_LOCAL,METHOD_GLOGAL, METHOD_LOCAL_GLOGAL, METHOD_IMPROVED_LOCAL]), method
		self.H = 4
		self.W = 15
		self.method = method
		self.objects = []
		self.objects += [Parking() for i in range(2)]
		self.objects += [LeftCar() for i in range(3)]
		self.objects += [RightCar() for i in range(3)]
		self.objects += [Pedestrian() for i in range(2)]
		# brains
		self.lbrain = LocalBrain()
		self.gbrain = GlobalBrain()
		self.ilbrain = ImproveLocalBrain()
		

	def train(self, n):
		for i in range(n):
			self.pos = self.getInitPos()
			ls = self.lbrain.getState(self, self.pos)
			gs = self.gbrain.getState(self, self.pos)
			ils = self.ilbrain.getState(self, self.pos)
			self.a = self.getQAction(ls, gs, ils)
			while self.pos.x != self.W-1:
				# do a
				pos_, lr, gr, ilr, _ = self.move(self.pos, self.a)
				# choose a_
				ls_ = self.lbrain.getState(self, pos_)
				gs_ = self.gbrain.getState(self, pos_)
				ils_ = self.ilbrain.getState(self, pos_)
				a_ = self.getQAction(ls_, gs_, ils_)
				# update Q
				self.lbrain.updateQ(ls, self.a, ls_, a_, lr)
				self.gbrain.updateQ(gs, self.a, gs_, a_, gr)
				self.ilbrain.updateQ(ils, self.a, ils_, a_, ilr)

				self.pos = pos_
				ls = ls_
				gs = gs_
				ils = ils_
				self.a = a_

	def evaluate(self, n):
		stat = {'steps':0, 'accident':0}
		for i in range(n):
			self.pos = self.getInitPos()
			ls = self.lbrain.getState(self, self.pos)
			gs = self.gbrain.getState(self, self.pos)
			ils = self.ilbrain.getState(self, self.pos)
			self.a = self.getQAction(ls, gs, ils)
			while self.pos.x != self.W-1:
				# do a
				pos_, lr, gr, ilr, ifHit = self.move(self.pos, self.a)
				# choose a_
				ls_ = self.lbrain.getState(self, pos_)
				gs_ = self.gbrain.getState(self, pos_)
				ils_ = self.ilbrain.getState(self, pos_)
				a_ = self.getQAction(ls_, gs_, ils_)

				self.pos = pos_
				ls = ls_
				gs = gs_
				ils = ils_
				self.a = a_
				# stat
				stat['steps'] += 1
				if ifHit:
					stat['accident'] += 1

		stat['steps'] /= float(n)
		stat['accident'] /= float(n)
		# print stat
		return stat

	def test(self, ini_pos):
		self.epsilon = 0.0
		self.pos = ini_pos
		ls = self.lbrain.getState(self, self.pos)
		gs = self.gbrain.getState(self, self.pos)
		ils = self.ilbrain.getState(self, self.pos)
		self.a = self.getQAction(ls, gs, ils)
		self.draw()
		while self.pos.x != self.W-1:
			# do a
			pos_, lr, gr, ilr, _ = self.move(self.pos, self.a)
			# choose a_
			ls_ = self.lbrain.getState(self, pos_)
			gs_ = self.gbrain.getState(self, pos_)
			ils_ = self.ilbrain.getState(self, pos_)
			a_ = self.getQAction(ls_, gs_, ils_)

			self.pos = pos_
			ls = ls_
			gs = gs_
			ils = ils_
			self.a = a_
			self.draw()

	def bin_2_int(self,bin):
		res = 0
		for i,v in enumerate(bin):
			res += v*math.pow(2,i)
		return res

	def nextTrajtLanes(self):
		lanes = np.zeros((self.H,self.W)) 
		for obj in self.objects:
			self.setLane(lanes, obj.getPos(), obj.id)	# current pos
			for p in obj.ntrajt:
				self.setLane(lanes, p, obj.id)			# next trajt
		return lanes

	def lanes(self):
		lanes = np.zeros((self.H,self.W)) 
		for obj in self.objects:
			self.setLane(lanes, obj.getPos(), obj.id)
		return lanes

	def getLane(self, lanes, pos):
		return lanes[pos.y, pos.x]

	def setLane(self, lanes, pos, value):
		lanes[pos.y, pos.x] = value

	def move(self, pos, a):
		# self.draw()
		# mycar move
		trajt_ = pos.move(a)
		pos_ = trajt_[-1]
		# other objects move
		all_obj_trajts = []
		for obj in self.objects:
			all_obj_trajts.append(obj.getPos())	# current pos
			obj.randomMove()					# perform move
			all_obj_trajts += obj.trajt 		# next trajt

		ifHit = self.ifTrajtIsect(trajt_, all_obj_trajts)
		
		# get reward
		lr = self.lbrain.getReward(pos, a, trajt_, all_obj_trajts, ifHit)
		gr = self.gbrain.getReward(pos, a, trajt_, all_obj_trajts, ifHit)
		ilr = self.ilbrain.getReward(pos, a, trajt_, all_obj_trajts, ifHit)

		return pos_, lr, gr, ilr, ifHit

	def ifTrajtIsect(self, trajt1, trajt2):
		trajt_ids = [pos.toInt() for pos in trajt2]
		for pos in trajt1:
			id = pos.toInt()
			if id in trajt_ids:
				return True
		return False

	def getQAction(self, ls, gs, ils):
		lq_list = self.lbrain.Q[ls,:]
		gq_list = self.gbrain.Q[gs,:]
		ilq_list = self.ilbrain.Q[ils,:]
		if self.method == METHOD_LOCAL:
			sumq_list = lq_list
		elif self.method == METHOD_GLOGAL:
			sumq_list = gq_list
		elif self.method == METHOD_LOCAL_GLOGAL:	
			sumq_list = lq_list + gq_list
		elif self.method == METHOD_IMPROVED_LOCAL:
			sumq_list = ilq_list
		else:
			print 'wrong method', self.method
			exit(0)
		if random() < 0.1:
			maxaction = self.lbrain.getRandomAction()
		else:
			maxaction = np.argmax(sumq_list)
		return maxaction


	def getInitPos(self):
		return Pos(0,randint(0,self.H-1))

	def getRandomPos(self):
		return Pos(randint(0,self.W-1),randint(0,self.H-1))

	def drawLane(self, lanes):
		self.setLane(lanes, self.pos, MY_CAR) 
		for y in range(self.H):
			for x in range(self.W):
				print symbol_dict[self.getLane(lanes,Pos(x,y))],
			print ''

	def draw(self):
		lanes = self.lanes()
		if self.getLane(lanes, self.pos) == EMPTY:
			self.setLane(lanes, self.pos, MY_CAR) 
		else:
			self.setLane(lanes, self.pos, COLLISION) 
		sp.call('clear',shell=True)	# linux
		print 'RL autocar'
		self.printLegand()
		for y in range(self.H):
			for x in range(self.W):
				print symbol_dict[self.getLane(lanes,Pos(x,y))],
			print ''

		# print 'r:', self.r
		# print '\nQ matrix'
		# print str(self.lbrain.Q[:10,:])
		# print self.gbrain.Q[:7,:]
		# print 'a:', self.a
		time.sleep(1.0)

	def printLegand(self):
		print 'EMPTY', symbol_dict[EMPTY]
		print 'MY_CAR', symbol_dict[MY_CAR]
		print 'LEFT_CAR', symbol_dict[LEFT_CAR]
		print 'RIGHT_CAR', symbol_dict[RIGHT_CAR]
		print 'PARKING', symbol_dict[PARKING]
		print 'PEDESTRIAN', symbol_dict[PEDESTRIAN]
		print 'RED', symbol_dict[RED]
		print 'YELLOW', symbol_dict[YELLOW]
		print 'GREEN', symbol_dict[GREEN]
		print 'COLLISION', symbol_dict[COLLISION]

def run(method):
	print '########################'
	print '###training on method', method
	print '########################'
	print 'iters steps accidents'
	train_iter_list = [10,50,100,200,500,1000,2000,5000,10000]
	train_time = 10
	for train_iter in train_iter_list:
		stat_list = {'steps':[], 'accident':[]}
		for t in range(train_time):
			agent = Agent(method)
			agent.train(train_iter)
			cstat = agent.evaluate(100)
			stat_list['steps'].append(cstat['steps'])
			stat_list['accident'].append(cstat['accident'])

		steps_mean = np.mean(stat_list['steps'])
		accident_mean = np.mean(stat_list['accident'])
		print train_iter, steps_mean, accident_mean

def run_test():
	print 'demo on Improve Local'
	agent = Agent(METHOD_IMPROVED_LOCAL)
	agent.train(5000)
	for y in [1,2,3,2,3]:
		agent.test(Pos(0,y))
	

if __name__ == '__main__':
	W = 15
	H = 4
	for method in [METHOD_LOCAL,METHOD_GLOGAL,METHOD_LOCAL_GLOGAL,METHOD_IMPROVED_LOCAL]:
		run(method)
	run_test()
	# run_test()

	


################ 
# local
# 10 11.274 3.016
# 50 11.2 1.392
# 100 11.883 1.121
# 200 12.234 0.871
# 500 11.626 0.652
# 1000 12.22 0.667
# 2000 12.263 0.71
# 5000 13.131 0.689
# 10000 11.912 0.665


### local, only hit reward
# 10 20.416 3.347
# 50 18.58 1.564
# 100 20.205 1.64
# 200 29.38 1.513
# 500 23.179 1.027
# 1000 22.347 0.902
# 2000 20.827 0.868
# 5000 21.403 0.828
# 10000 26.912 1.115
### global, only destination reward
# 10 24.484 7.501
# 50 9.224 3.357
# 100 8.382 3.242
# 200 8.156 3.048
# 500 7.019 2.913
# 1000 7.062 3.089
# 2000 6.626 2.911
# 5000 5.86 2.655
# 10000 5.652 2.594
### combine
# 10 16.149 3.087
# 50 13.79 2.172
# 100 15.624 1.88
# 200 13.135 1.232
# 500 13.171 0.965
# 1000 12.582 0.932
# 2000 12.14 0.879
# 5000 12.049 0.726
# 10000 11.774 0.773






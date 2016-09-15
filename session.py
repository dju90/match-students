#!/usr/bin/python

from collections import deque

class Session:
	def __init__(self, name, space):
		"""
		Creates a new Session object
		:param name: name of the class
		:param space: total space available in the session
		"""
		self._name = name.strip().lower()
		self.space = int(space)
		self.left = self.space
		self.roster = []
		# self.roster = deque(maxlen=int(space))
		self.score = 0

	def get_name(self):
		"""
		:return: the name of this Session object
		"""
		return self._name

	def get_space(self):
		return self.space
		# return self.roster.maxlen

	def add_student(self, student, preference):
		"""
		Adds a Student object and adjusts the session statistics accordingly
		:param student: a Student object
		:param preference: preference index of student's choice of this session
		:return:
		"""
		if self.has_space():
			self.roster.append(student)
			self.left -= 1
			self.score += preference + 1
			return True
		else:
			return False

	def has_space(self):
		"""
		:return: whether or not there is space left in this session
		"""
		return self.left > 0
		# return len(self.roster) < self.roster.maxlen

	def get_score(self):
		"""
		:return: the score of the class (best = 1.0)
		"""
		# sum = 0
		# invalids = 0
		# for student in self.roster:
		# 	choice_index = student.get_choice_index(self.get_name())
		# 	if choice_index > -1:
		# 		sum += choice_index + 1
		# 	else:
		# 		invalids += 1
		# return sum / (1.0 * (len(self.roster) - invalids))
		return self.score / max(1, self.space - self.left);

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self.space - self.left) + \
			   "/" + str(self.space) + " full, score = " + str(round(self.get_score(),2))
		# return str(self.roster.maxlen - len(self.roster)) + \
		# 		"/" + str(self.roster.maxlen) + " full, score = " + str(round(self.get_score(), 2))

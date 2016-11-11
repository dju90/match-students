#!/usr/bin/python

# native imports
import queue


# TODO: inheritance removed - reimplement basic methods
class SmartSession():
	def __init__(self, name, space, all_students):
		self._name = name.strip().lower()
		self.roster = queue.PriorityQueue(maxsize=int(space))
		self.order_counter = 0

	def pop(self):
		smart_student = self.roster.get()
		smart_student.incr_current_choice()
		return smart_student

	def has_space(self):
		return not self.roster.full()

	def register(self, smart_student):
		smart_student.set_order(self.order_counter)
		self.roster.put(smart_student)
		self.order_counter -= 1

	def get_num_students(self, choice_index):
		count = 0
		temp_roster = []
		while not self.roster.empty():
			student = self.roster.get()
			if student.get_current_choice() == choice_index:
				count += 1
			temp_roster.append(student)
		for student in temp_roster:
			self.roster.put(student)
		return count

	def get_score(self):
		score_sum = 0
		num_students = self.roster.qsize()
		temp_roster = []
		while not self.roster.empty():
			student = self.roster.get()
			score_sum += student.get_current_choice() + 1
			temp_roster.append(student)
		for student in temp_roster:
			self.roster.put(student)
		return score_sum / max(1, 1.0 * num_students)

	def get_total_students(self):
		return self.roster.qsize()

	def get_roster_as_set(self):
		temp_roster = []
		retset = set([])
		while not self.roster.empty():
			student = self.roster.get()
			temp_roster.append(student)
			retset.add(student)
		for student in temp_roster:
			self.roster.put(student)
		return retset

	def get_name(self):
		return self._name

	def get_space(self):
		return self.roster.maxsize

	# def get_preference(self, smart_student):
	# 	return self.preferences[smart_student.get_id()]

	# def define_preferences(self, all_students):
	# 	preferences = {}
	# 	for smart_student in all_students:
	# 		preferences[smart_student.get_id()] = smart_student.grade
	# 	return preferences

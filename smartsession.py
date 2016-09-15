#!/usr/bin/python

# native imports
import queue


# TODO: inheritance removed - reimplement basic methods
class SmartSession():
	def __init__(self, name, space, all_students):
		self._name = name.strip().lower()
		# self.preferences = self.define_preferences(all_students)
		self.roster = queue.PriorityQueue(maxsize=int(space))
		self.order_counter = 0

	def pop(self):
		if not self.roster.empty():
			smart_student = self.roster.get()
			smart_student.incr_current_choice()
			return smart_student

	def add_student(self, smart_student):
		if not self.roster.full():
			# smart_student.set_rank(self.get_preference(smart_student))
			smart_student.set_order(self.order_counter)
			self.roster.put(smart_student)
			self.order_counter -= 1
			return True
		else:
			return False

	# def get_preference(self, smart_student):
	# 	return self.preferences[smart_student.get_id()]

	# def define_preferences(self, all_students):
	# 	preferences = {}
	# 	for smart_student in all_students:
	# 		preferences[smart_student.get_id()] = smart_student.grade
	# 	return preferences

#!/usr/bin/python

from functools import total_ordering

from student import Student


@total_ordering
class SmartStudent(Student):
	def __init__(self, sid, grade, choices):
		super(SmartStudent, self).__init__(sid, grade, choices)
		self.order = 1
		self.current_choice = 0

	def set_order(self, order):
		self.order = order

	def get_current_choice(self):
		return self.current_choice

	def incr_current_choice(self):
		self.current_choice += 1

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self.get_id())

	def __hash__(self):
		return hash(self._id)

	def __eq__(self, other):
		return self.grade == other.grade and self.order == other.order and self._id == other.get_id()

	def __lt__(self, other):
		if self.grade == other.grade:
			return self.order < other.order
		else:
			return self.grade < other.grade

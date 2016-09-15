#!/usr/bin/python

# native imports
import argparse
import csv
import os
from pprint import PrettyPrinter
import sys

# local imports
from smartstudent import SmartStudent
from smartsession import SmartSession


class SmartMatch:
	def __init__(self, classes_csv, students_csv):
		self.students = self.define_students(students_csv)
		self.sessions = self.define_sessions(classes_csv)
		self.unassigned = set([])

	def define_students(self, filename):
		"""Returns a dictionary of SmartStudent objects
		:requires: students have a unique identifier
				   student data is in csv format, one student per line:
				   SID, GRADE_LEVEL, CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5
		"""
		selections = set([])
		with open(filename, 'r') as input:
			reader = csv.reader(input)
			for row in reader:
				sid = row[0]
				try:
					grade = int(row[1])
				except ValueError:
					continue
				student = SmartStudent(sid, grade, row[2:])
				selections.add(student)
		return selections

	def define_sessions(self, filename):
		"""
		Returns SmartSessions in dictionary form, keyed by session name
		:param filename: name of the file to be processed
		:return: dictionary of SmartSession objects
		:requires: class data is in csv format, one class per line:
				   CLASSNAME, NUM_SPACES
		"""
		sessions = {}
		with open(filename, 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				name = row[0].strip().lower()
				try:
					space = int(row[1])
				except ValueError:
					continue
				sessions[name] = SmartSession(name, space, self.students)
		return sessions

	def match(self):
		"""
		Performs the national medical school residency matching algorithm.
		:return:
		"""
		while self.students:  # while there are unplaced students
			student = self.students.pop()
			# get the student's current top choice number
			pref = student.get_current_choice()
			if pref <= 5:  # if the student still has preferenced sessions
				choice = student.get_choice(pref)
				try:
					smart_session = self.sessions[choice]
					added = smart_session.add_student(student)
					if not added:
						worst_match = smart_session.pop()
						# if the current student is preferred by the session over the worst match in the session
						#if smart_session.get_preference(student) > smart_session.get_preference(worst_match):
						if student.grade > worst_match.grade:
							# replace the worst match with the current student
							smart_session.add_student(student)
							worst_match.incr_current_choice()
							self.students.add(worst_match)
						else:
							# otherwise, increment the current student's current choice and re-add to the pool
							student.incr_current_choice()
							self.students.add(student)
				except KeyError:
					student.incr_current_choice()
					self.students.add(student)
			else:
				self.unassigned.add(student)

	def results_to_file(self, file):
		"""Writes the result dictionary to a file in csv format.
		   File format:
			   SID, CLASSNAME
		:param sessions: sessions with assigned rosters
		:param file: output file
		"""
		overwrite = "yes"
		if os.path.isfile(file):
			overwrite = input("File already exists! Overwrite? (yes/no) (q to quit): ").strip().lower()
			while not overwrite == "yes" and not overwrite == "no":
				if overwrite == "q":
					sys.exit(0)
				overwrite = input("Please type 'yes', 'no', or 'q': ").strip().lower()
		written = False
		while not written and overwrite == "yes":
			try:
				with open(file, 'w', newline='') as write_file:
					writer = csv.writer(write_file)
					writer.writerow(["SID", "Ticket Type"])
					for session in self.sessions:
						student_queue = self.sessions[session].roster
						processed = []
						while not student_queue.empty():
							student = student_queue.get()
							processed.append(student)
							line = [student.get_id()] + [session]
							writer.writerow(line)
						for student in processed:
							student_queue.put(student)
				written = True
			except IOError:
				quit = input("Please close the file first (Press Enter to continue...) ")

	def stats(self):
		printer = PrettyPrinter(indent=2)
		grade_stats = self.summarize_assigned_stats()
		unassigned_stats = self.summarize_unassigned_stats(grade_stats)
		total_stats, total_students = self.summarize_total_stats(grade_stats, unassigned_stats)

		print()
		print("### Overall statistics ###")
		total = sum_dictionary(total_stats)
		for key in total_stats:
			print(choice_str(key) + ": " + str(total_stats[key]) + "/" + str(total) +
				  " ({}%)".format(round(total_stats[key]/(1.0*total)*100, 2)))
		print()

		print("### Breakdown by grade ###")
		for grade in grade_stats:
			print(str(grade) + "TH GRADE:")
			grade_choices = grade_stats[grade]
			for key in grade_choices:
				print("\t" + choice_str(key) + ": " + str(grade_choices[key]) + "/" + str(total_students[grade]) +
					  " ({}%)".format(round(grade_choices[key]/(1.0*total_students[grade])*100, 2)))
		print()

		print(str(len(self.unassigned)) + " total unassigned students.")
		for grade in unassigned_stats:
			print(str(grade) + "th grade: " + str(unassigned_stats[grade]))

	def summarize_total_stats(self, assigned_stats, unassigned_stats):
		total_stats = {}
		total_students = {}
		for grade in assigned_stats:
			total_grade_students = 0
			for placement in assigned_stats[grade]:
				num_students = assigned_stats[grade][placement]
				total_grade_students += num_students
				if placement not in total_stats:
					total_stats[placement] = 0
				total_stats[placement] += num_students
			total_students[grade] = total_grade_students
			# for placement in assigned_stats[grade]:
			# 	num_students = assigned_stats[grade][placement]
			# 	assigned_stats[grade][placement] = str(num_students) + " students " + \
			# 									   " (" + \
			# 									   str(round(num_students / (1.0 * total_grade_students) * 100)) + \
			# 									   "%)"
		return total_stats, total_students

	def summarize_unassigned_stats(self, assigned_stats):
		unassigned_stats = {}
		for student in self.unassigned:
			grade_key = student.grade
			if grade_key not in unassigned_stats:
				unassigned_stats[grade_key] = []
			if grade_key not in assigned_stats:
				assigned_stats[grade_key] = {}
			if "unassigned" not in assigned_stats[grade_key]:
				assigned_stats[grade_key]["unassigned"] = 0
			assigned_stats[grade_key]["unassigned"] += 1
			unassigned_stats[grade_key].append(student)
		return unassigned_stats

	def summarize_assigned_stats(self):
		assigned_stats = {}
		for session in self.sessions:
			student_queue = self.sessions[session].roster
			processed = []
			while not student_queue.empty():
				student = student_queue.get()
				grade_key = student.grade
				if grade_key not in assigned_stats:
					assigned_stats[grade_key] = {}
				choice = student.get_choice_index(session)
				# if choice == 0:
				# 	choice_str = "1st choice"
				# elif choice == 1:
				# 	choice_str = "2nd choice"
				# elif choice == 2:
				# 	choice_str = "3rd choice"
				# else:
				# 	choice_str = str(choice + 1) + "th choice"
				choice_str = choice
				if choice_str not in assigned_stats[grade_key]:
					assigned_stats[grade_key][choice_str] = 0
				assigned_stats[grade_key][choice_str] += 1
			for student in processed:
				student_queue.put(student)
		return assigned_stats


def choice_str(choice):
	try:
		num = int(choice)
	except ValueError:
		return choice
	if num == 0:
		retval = "1st choice"
	elif num == 1:
		retval = "2nd choice"
	elif num == 2:
		retval = "3rd choice"
	else:
		retval = str(num + 1) + "th choice"
	return retval


def sum_dictionary(dict):
	sum = 0
	for key in dict:
		try:
			sum += int(dict[key])
		except ValueError:
			continue
	return sum


def main():
	parser = argparse.ArgumentParser(description="Sort n students into m sessions with x slots per class and 5 ordered selections per student." +
												 " Heuristic finds optimal solution, with seniors favored over juniors over sophomores over freshmen.")
	parser.add_argument("-v", "--verbose", help="output placement round session statistics and unplaced student SIDs to console", action="store_true")
	parser.add_argument("classes_csv", help="name of the class data csv file to use (relative path)")
	parser.add_argument("students_csv", help="name of the student data csv file to use (relative path)")
	parser.add_argument("output_csv", help="name of the (new) csv file to write to (relative path)")
	args = parser.parse_args()

	smart_match = SmartMatch(args.classes_csv, args.students_csv)
	smart_match.match()
	smart_match.results_to_file(args.output_csv)
	if args.verbose:
		smart_match.stats()

if __name__ == "__main__":
	main()
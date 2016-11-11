#!/usr/bin/python

# native imports
import argparse
import copy
import csv
import os
from pprint import PrettyPrinter
import random
import sys

# local imports
from smartstudent import SmartStudent
from smartsession import SmartSession
from common import choice_str, sum_dictionary


class SmartMatch:
	def __init__(self, students, sessions, integer_class_names):
		self.class_numbers = integer_class_names
		self.students = students
		self.sessions = sessions
		self.unassigned = set([])
		self.tallies = None

	def match(self):
		"""
		Performs the national medical school residency matching algorithm.
		:return:
		"""
		while self.students:  # while there are unplaced students
			student = self.students.pop()
			# get the student's current top choice number
			pref = student.get_current_choice()
			if pref < len(student.choices):  # if the student still has preferenced sessions
				choice = student.get_choice(pref)
				try:
					smart_session = self.sessions[choice]
					if smart_session.has_space():
						smart_session.register(student)
					else:
						worst_match = smart_session.pop()
						# if the current student is preferred by the session over the worst match in the session
						# if smart_session.get_preference(student) > smart_session.get_preference(worst_match):
						if student.grade > worst_match.grade:
							# replace the worst match with the current student
							smart_session.register(student)
							worst_match.incr_current_choice()
							self.students.add(worst_match)
						else:
							# put back the worst match, increment the current student's preference
							smart_session.register(worst_match)
							student.incr_current_choice()
							self.students.add(student)
				except KeyError:
					student.incr_current_choice()
					self.students.add(student)
			else:
				self.unassigned.add(student)
		# best = least number of higher-grade students left unmatched
		match_success = 0
		for student in self.unassigned:
			match_success += student.grade
		return match_success

	def prematch(self, top_n):
		"""Pre-sort students into classes whose capacity is greater than
			the total number of choices in the top n choices of each student
		:param top_n: top n choices of each student to tally up
		:return:
		"""
		# tally all choices
		top_n_tallies = {}
		session_tallies = dict.fromkeys(self.sessions.keys(), 0)
		for student in self.students:
			for pref in range(0, len(student.choices)):
				choice = student.get_choice(pref)
				if choice in self.sessions:
					if pref < top_n:
						if choice not in top_n_tallies:
							top_n_tallies[choice] = []
						top_n_tallies[choice].append(student)
					session_tallies[choice] += 1

		pre_placement_students = set([])
		pre_placement_sessions = {}
		for session in top_n_tallies:
			session_object = self.sessions[session]
			space = session_object.get_space()
			total_choices = len(top_n_tallies[session])
			if space >= total_choices:
				pre_placement_students.update(top_n_tallies[session])
				if session_object.get_name() not in pre_placement_sessions:
					pre_placement_sessions[session_object.get_name()] = session_object
		while pre_placement_students:
			student = pre_placement_students.pop()
			pref = 0
			placed = False
			while not placed and pref < top_n:
				choice = student.get_choice(pref)
				if choice in pre_placement_sessions:
					pre_placement_sessions[choice].register(student)
					self.students.remove(student)
					placed = True
				pref += 1
		self.tallies = session_tallies

	def results_to_file(self, file, best):
		"""Writes the result dictionary to a file in csv format.
		   File format:
			   SID, CLASSNAME
		:param file: output file
		"""
		overwrite = "yes"
		if os.path.isfile(file):
			overwrite = input("File already exists! " + str(best) +
							  " students unassigned for this run. Overwrite? (yes/no) (q to quit): ").strip().lower()
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
					num_written = 0
					for session in self.sessions:
						student_queue = self.sessions[session].roster
						processed = []
						while not student_queue.empty():
							student = student_queue.get()
							processed.append(student)
							line = [student.get_id()] + [session]
							writer.writerow(line)
							num_written += 1
						for student in processed:
							student_queue.put(student)
					for student in self.unassigned:
						line = [student.get_id()] + ["UNASSIGNED"]
						writer.writerow(line)
						num_written += 1
					print("Number of student rows written: " + str(num_written))
				written = True
			except IOError:
				quit = input("Please close the file first (Press Enter to continue...) ")

	def stats(self):
		printer = PrettyPrinter(indent=2)
		grade_stats = self.summarize_assigned_stats()
		unassigned_stats = self.summarize_unassigned_stats(grade_stats)
		total_stats, total_students = self.summarize_total_stats(grade_stats)
		print()

		print("### Selection statistics (class name: total number of student votes ###")
		sorted_sessions = sorted(self.tallies.keys(), key=lambda x: int(x) if self.class_numbers else x)
		most_popular = max(self.tallies.values())
		max_class_name_len = len(sorted_sessions[len(sorted_sessions)-1])
		for session in sorted_sessions:
			count = self.tallies[session]
			print(str(session).rjust(max_class_name_len) + ": ", end="")
			for star in range(0, round(count/(1.0*most_popular)*100)):
				print("█", end="")
			print(" " + str(count))
		print()

		print("### Overall results ###")
		total = sum_dictionary(total_stats)
		for key in total_stats:
			print(choice_str(key) + ": " + str(total_stats[key]).rjust(4) + "/" + str(total) +
				  " ({}%)".format(round(total_stats[key] / (1.0 * total) * 100, 2)))
		print()

		print("### Breakdown by grade ###")
		for grade in grade_stats:
			print(str(grade) + "TH GRADE:")
			grade_choices = grade_stats[grade]
			for key in grade_choices:
				print("\t" + choice_str(key) + ": " + str(grade_choices[key]).rjust(3) + "/" + str(
					total_students[grade]) +
					  " ({}%)".format(round(grade_choices[key] / (1.0 * total_students[grade]) * 100, 2)))
		print()

		print("### Breakdown by class ### Notes: score of 1.0 is best")
		sessions = sorted(self.sessions.keys(), key=float) if self.class_numbers else sorted(self.sessions.keys())
		for sesh in sessions:
			session = self.sessions[sesh]
			score = session.get_score()
			stars = "***" if score >= 2 else ""
			total = session.get_total_students()
			space = session.get_space()
			print(session.get_name().rjust(2) + ": "
				  + str(total).rjust(2) + "/" + str(space) + ", "
				  + "score = " + (stars + str(round(score, 2)) + stars).ljust(10) +
				  (" FULL" if total==space else ""))
		# space = session.get_space()
		# for key in total_stats:
		# 	num_students = session.get_num_students(key)
		# 	if num_students != 0:
		# 		print(choice_str(key) + "s: " + str(num_students).rjust(3) + "/" + str(space) +
		# 			  "({})%".format(round(num_students/max(1,(1.0*space))*100, 2)))
		# print("Spots full: " + str(session.get_total_students()) + "/" + str(session.get_space()))
		print()

		print("### " + str(len(self.unassigned)) + " total unassigned students ###")
		for grade in unassigned_stats:
			unassigned = len(unassigned_stats[grade])
			total = total_students[grade]
			print(str(grade).rjust(2) + "th grade: " +
				  str(len(unassigned_stats[grade])).rjust(3) + "/" + str(total_students[grade]) +
				  " (" + str(round(unassigned/(1.0*total)*100,2)) + "%)")

	def summarize_total_stats(self, assigned_stats):
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
		assigned = 0
		for session in self.sessions:
			student_queue = self.sessions[session].roster
			processed = []
			while not student_queue.empty():
				student = student_queue.get()
				processed.append(student)
				grade_key = student.grade
				if grade_key not in assigned_stats:
					assigned_stats[grade_key] = {}
				choice = student.get_choice_index(session)
				choice_str = choice
				if choice_str not in assigned_stats[grade_key]:
					assigned_stats[grade_key][choice_str] = 0
				assigned_stats[grade_key][choice_str] += 1
				assigned += 1
			for student in processed:
				student_queue.put(student)
		return assigned_stats


def define_students(filename, integer_class_names):
		"""Returns a set of SmartStudent objects
		:requires: students have a unique identifier
				   student data is in csv format, one student per line:
				   SID, GRADE_LEVEL, CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5
		"""
		selections = []
		with open(filename, 'r') as input_file:
			reader = csv.reader(input_file)
			for row in reader:
				sid = row[0]
				try:
					grade = int(row[1])
				except ValueError:
					continue
				if integer_class_names:
					student = SmartStudent(sid, grade, [str(int(x)) for x in row[2:]])
				else:
					student = SmartStudent(sid, grade, row[2:])
				selections.append(student)
		random.shuffle(selections)
		return set(selections)


def define_sessions(filename):
	"""
	Returns SmartSessions in dictionary form, keyed by session name
	:return:
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
			if space > 0:
				sessions[name] = SmartSession(name, space)
	return sessions


# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def main():
	parser = argparse.ArgumentParser(
		description="Sort k students into m sessions with x slots per class and y ordered selections per student." +
					" Heuristic finds optimal solution, w/ seniors favored over juniors over sophomores over freshmen.")
	parser.add_argument("-v", "--verbose",
						help="output placement round session statistics and unplaced student SIDs to console",
						action="store_true")
	parser.add_argument("-n", "--numeric",
						help="classes are integer numbered instead of named", action="store_true")
	parser.add_argument("--iterate", help="perform the algorithm ITERATE times", type=int, default=1)
	parser.add_argument("--presort", help="pre-sort students into classes whose capacity is greater than " +
						"the total number of choices in the first PRESORT choices of each student", type=int)
	parser.add_argument("classes_csv", help="name of the class data csv file to use (relative path)")
	parser.add_argument("students_csv", help="name of the student data csv file to use (relative path)")
	parser.add_argument("output_csv", help="name of the (new) csv file to write to (relative path)")
	args = parser.parse_args()

	best_match = None
	best_result = float('Inf')
	for i in range(0, args.iterate):
		students = define_students(args.students_csv, args.numeric)
		sessions = define_sessions(args.classes_csv)
		smart_match = SmartMatch(students, sessions, args.numeric)
		if args.presort:
			smart_match.prematch(args.presort)
		result = smart_match.match()
		printProgress(i+1, args.iterate, prefix = 'Progress:', suffix = 'Complete')
		if result < best_result:
			best_result = result
			best_match = smart_match

	print()
	best_match.results_to_file(args.output_csv, len(best_match.unassigned))
	if args.verbose:
		best_match.stats()


if __name__ == "__main__":
	main()

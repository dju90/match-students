#!/usr/bin/python

"""Sorting n students into m classes with x slots per class and 3 ordered selections per students"""

import argparse
import copy
import csv
import os.path
import pprint
import random
import sys

from session import Session
from student import Student

def define_sessions(filename):
	"""
	Returns sessions and associated information from a csv file in dictionary form
	:param filename: name of the file to be processed
	:return: dictionary of Session objects
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
			# session_code = re.search("\(([a-zA-Z0-9]+)\)", name).group(1)
			sessions[name] = Session(name, space)
	return sessions


def define_students(filename):
	"""Returns a dictionary of Student objects
	:requires: students have a unique identifier
			   student data is in csv format, one student per line:
			   SID, GRADE_LEVEL, CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5
	"""
	selections = {}
	with open(filename, 'r') as input:
		reader = csv.reader(input)
		for row in reader:
			sid = row[0]
			try:
				grade = int(row[1])
			except ValueError:
				continue
			student = Student(sid, grade, row[2:])
			if grade not in selections:
				selections[grade] = []
			selections[grade].append(student)
	return selections


def match(sessions, selections):
	"""
	Algorithm: place students in reverse grade order: shuffle students, then place as many first choices as possible,
			   then repeat for 2nd, 3rd, 4th, and 5th choices.
			   Modifies sessions dictionary parameter in-place.
	:param sessions:
	:param selections:
	:return: a list of unplaced student identifiers
	"""
	unplaced = []
	grades = sorted(selections.keys(), key=lambda grade: -grade)
	for grade in grades:
		random.shuffle(selections[grade])
		for student in selections[grade]:
			preference = 0
			placed = False
			while preference < len(student.choices) and not placed:
				try:
					placed = sessions[student.get_choice(preference)].register(student, preference)
				except KeyError:
					pass
				preference += 1
			if not placed:
				unplaced.append(student.get_id())
	return unplaced


def match_n_times(sessions, students, iterations):
	"""
	Runs match function <iterations> times, with random shuffle of student keys each iteration
	:param sessions: dictionary of Session objects
	:param students: dictionry of Student objects keyed by grade level
	:param iterations: number of times to run the algorithm
	:return:
	"""
	best_match = {}
	best_unplaced = []
	fewest_unmatched = float('Inf')
	iteration = -1
	for i in range(0, iterations):
		iteration = i
		if iterations == 1:
			copy_classes = sessions
		else:
			copy_classes = copy.deepcopy(sessions)
		res = match(copy_classes, students)
		if len(res) < fewest_unmatched:
			fewest_unmatched = len(res)
			best_unplaced = res
			best_match = copy_classes
			if len(res) == 0:
				break
	return iteration+1, best_match, best_unplaced

def write_results_to_file(sessions, file):
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
				for session in sessions:
					for student in sessions[session].roster:
						line = [student.get_id()] + [session]
						writer.writerow(line)
			written = True
		except IOError:
			quit = input("Please close the file first (Press Enter to continue...) ")


def stats(iterations, best_matching, unplaced):
	"""
	Prints statistics for the result set
	:param iterations: number of runs to find the best match
	:param best_matching: the best outcome out of all the runs
	:param unplaced: student ids of unplaced students
	"""
	printer = pprint.PrettyPrinter(indent=2)
	printer.pprint(best_matching)
	print("Out of " + str(iterations) + ", best result:")
	print(str(len(unplaced)) + " unplaced students: " + str(unplaced))

def main():
	"""
	Attempts ITERATIONS iterations of the algorithm to determine the best session assignment
	:return:
	"""
	parser = argparse.ArgumentParser(description="Sort n students into m sessions with x slots per class and 3 ordered selections per student. Heuristic purely weights fewest unplaced students (according to their selections) as best.")
	parser.add_argument("-v", "--verbose", help="output placement round session statistics and unplaced student SIDs to console", action="store_true")
	parser.add_argument("--iterate", help="perform i matchings and keep the best run (default is 1)", type=int, default=1)
	parser.add_argument("classes_csv", help="name of the class data csv file to use (relative path)")
	parser.add_argument("students_csv", help="name of the student data csv file to use (relative path)")
	parser.add_argument("output_csv", help="name of the (new) csv file to write to (relative path)")
	args = parser.parse_args()

	sessions = define_sessions(args.classes_csv)
	students = define_students(args.students_csv)

	total_space = sum([sessions[session].get_space() for session in sessions])
	num_students = sum([len(students[grade]) for grade in students])
	if total_space < num_students:
		print("not enough space for all students! Attempting to place " + num_students + " students in " + total_space + " spaces.")
	else:
		iterations, best_matching, fewest_unmatched = match_n_times(sessions, students, args.iterate)
		write_results_to_file(best_matching, args.output_csv)
		if args.verbose:
			stats(iterations, best_matching, fewest_unmatched)

if __name__ == '__main__':
	main()

#!/usr/bin/python

# native imports
import argparse
import csv
import os
import random
import sys

# local imports
import match


class TestInputGenerator:
	def __init__(self, classes_csv):
		self.sessions = match.define_sessions(classes_csv)

	def generate_input_from(self, students_csv, output_csv, verbose=True, random_grade=False):
		overwrite = "yes"
		if os.path.isfile(output_csv):
			overwrite = input("File already exists! Overwrite? (yes/no) (q to quit): ").strip().lower()
			while not overwrite == "yes" and not overwrite == "no":
				if overwrite == "q":
					sys.exit(0)
				overwrite = input("Please type 'yes', 'no', or 'q': ").strip().lower()
		choices = self.sessions.keys()
		grades = [9, 10, 11, 12]
		with open(students_csv, 'r') as in_file:
			with open(output_csv, 'w', newline='') as out_file:
				reader = csv.reader(in_file)
				writer = csv.writer(out_file)
				i = 1
				for row in reader:
					try:
						grade = [int(row[1])]
					except ValueError:
						writer.writerow(row)
						continue
					else:
						if random_grade:
							grade = random.sample(grades, 1)
						chosen = random.sample(choices, 5)
						writer.writerow(row[:1] + grade + chosen)
						if verbose:
							if i % 100 == 0:
								print("Choosing 5 random classes for the " + str(i) + "th student: " + str(chosen))
							i += 1
		print("Finished! See " + output_csv + " for your new randomly-generated input file.")


def main():
	parser = argparse.ArgumentParser(description="Generates 5 random student choices for each student across the given collection of classes and student IDs.")
	parser.add_argument("-v", "--verbose", help="output progress to console", action="store_true")
	parser.add_argument("--randomgrades", help="choose a random grade for each student", action="store_false")
	parser.add_argument("classes_csv", help="name of the class data csv file to use (relative path)")
	parser.add_argument("students_csv", help="name of the student data csv file to use (relative path)")
	parser.add_argument("output_csv", help="name of the (new) csv file to write to (relative path)")
	args = parser.parse_args()

	generator = TestInputGenerator(args.classes_csv)
	generator.generate_input_from(args.students_csv, args.output_csv, args.verbose, args.randomgrades)


if __name__ == '__main__':
	main()
#!/usr/bin/python

def choice_str(choice):
	try:
		num = int(choice)
	except ValueError:
		return choice
	if num == 0:
		return "1st choice"
	elif num == 1:
		return "2nd choice"
	elif num == 2:
		return "3rd choice"
	else:
		return str(num + 1) + "th choice"


def sum_dictionary(dict):
	sum = 0
	for key in dict:
		try:
			sum += int(dict[key])
		except ValueError:
			continue
	return sum
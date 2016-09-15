#!/usr/bin/python


class Student:
    def __init__(self, sid, grade, choices):
        """
        Creates a new student object
        :param sid: student id
        :param grade: grade level (int)
        :param choices: session choices in order of preference
        """
        self._id = sid
        self.grade = grade
        self.choices = [choice.strip().lower() for choice in choices]

    def get_id(self):
        """
        :return: id of this Student object
        """
        return self._id

    def get_choice_index(self, preference):
        """
        :param preference: name of the session
        :return: preference number for that session; -1 if not found
        """
        try:
            return self.choices.index(preference)
        except ValueError:
            return -1

    def get_choice(self, preference):
        """
        Gets the Student's choice at position PREFERENCE
        :param preference:
        :return: name of the session at the specified preference position;
                 if preference index is higher than number of choices, returns empty string
        """
        if preference < len(self.choices):
            return self.choices[preference]
        else:
            return ""

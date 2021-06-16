# GOAL: from 4 csv files given as command line args, parse them into a json file as specified.

from os import error
import sys
import csv
import json


# class defs

class Course:
  def __init__(self, id, name, teacher):
    self.id = id
    self.name = name
    self.teacher = teacher

class Student:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
        # dictionary of averages to be deliminated by course
        self.course_averages = {}
        self.total_average = -1

class Test:
    def __init__(self, id, course_id, weight):
        self.id = id
        self.course_id = course_id
        self.weight = weight

class Mark:
    def __init__(self, test_id, student_id, mark):
        self.test_id = test_id
        self.student_id = student_id
        self.mark = mark

# ---

# function defs

# given a path to a csv, parse the data from that csv into the intermmediate data structure provided
def parse_csv(input_path, data, type):

    with open(input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                entry = None
                if(type == 'courses'):
                    entry = Course(row[0], row[1], row[2])
                elif type == 'students':
                    entry = Student(row[0], row[1])
                elif type == 'tests':
                    entry = Test(row[0], row[1], row[2])
                elif type == 'marks':
                    entry = Mark(row[0], row[1], row[2])
                    #print(f'{row[0]}')
                data.append(entry)
            line_count += 1



# assign additional data:
#     - set additional references for students to help with parsing to json
#     - calculate course averages and total averages for students

def process_data(courses, students, tests, marks):

    weights = {}
    tests_applied_weight = []
    for mark in marks:
        test = find_test(tests, mark.test_id)
        student = find_student(students, mark.student_id)
        course = find_course(courses, test.course_id)
        score = mark.mark
        weight = test.weight
        course_averages = student.course_averages
        if course not in course_averages:
            course_averages[course] = []
        course_averages[course].append(float(score) * float(weight))
        if course not in weights:
            weights[course] = []
        if(test not in tests_applied_weight):
            weights[course].append(weight)
            tests_applied_weight.append(test)

    
    return check_weights(weights)



def calculate_averages(students):

    for student in students:

        course_averages = student.course_averages

        total_cumulative = 0
        scores_cumulative = 0

        for course in course_averages:
            total_course = 0
            scores_course = 0
            for score in course_averages[course]:
                total_course += score
                scores_course += 1
            average_course = total_course / 100
            course_averages[course] = average_course
            total_cumulative += average_course
            scores_cumulative += 1
    
        average_cumulative = total_cumulative / scores_cumulative
        student.total_average = average_cumulative

        # TODO: exception when weights don't add up


# helper functions

def find_course(courses, course_id):
    for course in courses:
        if course.id == course_id:
            return course
    print("Course lookup unsuccessful")
    return None

def find_student(students, student_id):
    for student in students:
        if student.id == student_id:
            return student
    print("Student lookup unsuccessful")
    return None

def find_test(tests, test_id):
    for test in tests:
        if test.id == test_id:
            return test
    print("Test lookup unsuccessful")
    return None

def check_weights(weights):
    for course in weights:
        total = 0
        for weight in weights[course]:
            total += float(weight)
        if total != 100:
            return False
    return True
# ---

# parse data from students provided and output to the specified path as a json file
def write_json(students, output_path):
    
    students_dict = {"students":[]}

    for student in students:

        content = []
        content.append(f'id: {student.id}')
        content.append(f'name: {student.name}')
        content.append(f'totalAverage: {str(round(student.total_average, 2))}')

        course_info = {"courses":[]}
        for course in student.course_averages.keys():
            course_content = []
            course_content.append(f'id: {course.id}')
            course_content.append(f'name: {course.name}')
            course_content.append(f'teacher: {course.teacher}')
            course_content.append(f'courseAverage: {str(round(student.course_averages[course], 2))}')
            course_info["courses"].append(course_content)

        content.append(course_info)
    
        students_dict["students"].append(content)

        
    with open(output_path, 'w') as json_file:
        json.dump(students_dict, json_file, indent=2)


# write an error message to the json file
def write_json_error(error_msg, output_path):
    print(error_msg)
    with open(output_path, 'w') as json_file:
        json.dump({error_msg:[]}, json_file, indent=2)


def main():

    # structures to contain the data parsed from csv files
    courses = []
    students = []
    tests = []
    marks = []

    # get input paths from command line args
    args = sys.argv
    path_courses = args[1]
    path_students = args[2]
    path_tests = args[3]
    path_marks = args[4]
    path_json = args[5]

    # parse the csv file data into our intermmediate data
    parse_csv(path_courses, courses, 'courses')
    parse_csv(path_students, students, 'students')
    parse_csv(path_tests, tests, 'tests')
    parse_csv(path_marks, marks, 'marks')

    # fill student data with necessary references to draw from for when we write the json, while checking to see if the course weights add up
    data_processed = process_data(courses, students, tests, marks)

    # if an error occured, write to the json file and exit
    if not data_processed:
        write_json_error("error: Invalid course weights", path_json)
        exit()

    # else, calculate the averages and write to the json file from our students data
    calculate_averages(students)
    write_json(students, path_json)


if __name__ == "__main__":
    main()

import classes
import csv
from operator import itemgetter
from tabulate import tabulate

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMESTRINGS = ["9-11", "11-13", "13-15", "15-17"]
PERIODS = len(TIMESTRINGS)
DATA_OFFSET = 3
TIMESLOTS = 20

def read(path, sort=False, sort_column=1):
    """
    Reads csv file from path and returns a list, stripping the first row
    if it contains no digits (if it is a header).
    """
    with open(path, "r", encoding="utf-8") as f:
        result = list(csv.reader(f))

    # strip the first row if it is a header
    if not any(item.isdigit() for item in result[0]):
        result = result[1:]

    if sort:
        for item in result:
            item[sort_column] = int(item[sort_column])
        result.sort(key=itemgetter(sort_column))

    return result


def create_course_list(course_list, student_list):
    """
    Returns a list of Course objects, each
    containing students following the course.
    """
    courses = [classes.Course(data, []) for data in course_list]

    # assign students to corresponding Course objects
    for student_object in student_list:
        for course_name in student_object.courses:
            for course in courses:
                if course_name == course.name:
                    course.students.append(student_object)
                    break

    return courses

def create_teachings(courses):
    """
    Returns a list of teachings corresponding to
    the Course object list courses.
    """
    teachings = []

    for course in courses:
        for _ in range(course.lectures):
            # assign students to lecture
            teachings.append(classes.Teaching("lecture",
                course, course.students))

        if course.seminars:
            # assign students to seminar groups (in alphabetical order)
            for i in range(course.get_group_count("seminar")):
                group = course.students[i * course.s_cap:(i+1) * course.s_cap]
                teachings.append(classes.Teaching("seminar",
                    course, group, ALPHABET[i]))

        if course.practicals:
            # assign students to practical groups (in alphabetical order)
            for i in range(course.get_group_count("practical")):
                group = course.students[i * course.p_cap:(i+1) * course.p_cap]
                teachings.append(classes.Teaching("practical",
                    course, group, ALPHABET[i]))

    return teachings

def create_schedule(teachings, hall_list):
    """
    Creates a schedule, filling all halls from hall_list with
    teachings from teachings.
    Returns a list of lists containing Teaching objects.
    """
    schedule = [[None for i in range(TIMESLOTS)] for j in range(len(hall_list))]

    tracker = [0] * len(hall_list)
    for teaching in teachings:
        for i,hall in enumerate(hall_list):
            if len(teaching.students) <= hall.capacity:
                if tracker[i] < TIMESLOTS:
                    schedule[i][tracker[i]] = teaching

                    # add hall to teaching object
                    teaching.hall = hall_list[i]
                    tracker[i] += 1
                    break

    return schedule

def print_schedule(hall_list, schedule):
    """
    Prints a table containing a schedule with lists from hall_list.
    """
    headers = [hall.name for hall in hall_list]
    headers.insert(0,"")
    printable_schedule = []

    for i,t in enumerate(zip(*schedule)):
        if not i % PERIODS:
            day_row = [WEEKDAYS[i // PERIODS]]
            day_row.extend([None] * len(hall_list))
            printable_schedule.append(day_row)

        schedule_row = list(t)
        schedule_row.insert(0, TIMESTRINGS[i % PERIODS])
        printable_schedule.append(schedule_row)

    print(tabulate(printable_schedule, headers))

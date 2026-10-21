import csv
from pathlib import Path


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def split_items(text):
    return [item.strip() for item in (text or "").split(";") if item.strip()]


def listed_rooms(text):
    names = []
    for part in split_items(text):
        if "/" in part and " " in part:
            first, *extra_numbers = part.split("/")
            names.append(first)
            prefix = first.rsplit(" ", 1)[0]
            names.extend(prefix + " " + number for number in extra_numbers)
        else:
            names.append(part)
    return names


def load_data(data_dir):
    folder = Path(data_dir)
    names = ["courses", "rooms", "time_slots", "instructors", "student_cohorts", "constraints"]
    data = {name: read_csv(folder / (name + ".csv")) for name in names}

    if not data["courses"] or not data["rooms"] or not data["time_slots"]:
        raise ValueError("The course, room, and time slot files cannot be empty.")

    courses = {row["course_id"].strip(): row for row in data["courses"]}
    rooms = {row["room_id"].strip(): row for row in data["rooms"]}
    slots = {row["slot_id"].strip(): row for row in data["time_slots"]}
    if len(courses) != len(data["courses"]):
        raise ValueError("Duplicate course IDs in courses.csv")
    if len(rooms) != len(data["rooms"]):
        raise ValueError("Duplicate room IDs in rooms.csv")
    if len(slots) != len(data["time_slots"]):
        raise ValueError("Duplicate time slot IDs in time_slots.csv")

    cohorts_for_course = {course_id: [] for course_id in courses}
    cohort_sizes = {}
    for row in data["student_cohorts"]:
        cohort_sizes[row["cohort_id"]] = int(row["size"])
        for course_id in split_items(row.get("mandatory_courses", "")):
            if course_id not in courses:
                raise ValueError("Mandatory course missing from courses.csv: " + course_id)
            cohorts_for_course[course_id].append(row["cohort_id"])

    instructor_ids = {row["instructor_name"].strip(): row["instructor_id"].strip()
                      for row in data["instructors"]}
    instructor_rows = {row["instructor_id"].strip(): row for row in data["instructors"]}

    preferred_rooms = {}
    for row in data["constraints"]:
        rule = row.get("rule", "")
        if row.get("constraint_type", "").lower() == "preferred" and "preferred_room = '" in rule:
            room_id = rule.split("preferred_room = '", 1)[1].split("'", 1)[0]
            for course_id in split_items(row.get("applies_to", "")):
                preferred_rooms[course_id] = room_id

    for course_id, row in courses.items():
        row["cohort_ids"] = cohorts_for_course[course_id]
        row["suggested_rooms"] = listed_rooms(row.get("rooms_mentioned", ""))
        teachers = split_items(row.get("instructors", ""))
        row["instructor_id"] = row.get("instructor_id", "").strip() or (
            instructor_ids.get(teachers[0], teachers[0]) if teachers else ""
        )
        declared = row.get("enrollment", "").strip() or row.get("expected_enrollment", "").strip()
        if declared:
            row["enrollment_count"] = int(declared)
            row["estimated_enrollment"] = False
        elif row["cohort_ids"]:
            row["enrollment_count"] = max(cohort_sizes[cohort_id] for cohort_id in row["cohort_ids"])
            row["estimated_enrollment"] = False
        else:
            row["enrollment_count"] = 30
            row["estimated_enrollment"] = True

    data.update(courses_by_id=courses, rooms_by_id=rooms, slots_by_id=slots,
                instructors_by_id=instructor_rows, preferred_rooms=preferred_rooms)
    return data
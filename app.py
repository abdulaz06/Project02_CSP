"""Project 2: University Class Scheduling & Timetable Optimizer."""

import csv
from pathlib import Path

from data_loader import load_data
from constraints_engine import check_schedule, soft_penalty
from solver import TimetableSolver


def studentscheduler(data_dir="data", output_dir="data", student_id=None):
    data = load_data(data_dir)
    solver = TimetableSolver(data)
    schedule, original_penalty = solver.solve()

    errors = check_schedule(schedule, data)
    if errors:
        raise ValueError("Invalid timetable:\n" + "\n".join(errors))

    output_folder = Path(output_dir)
    output_folder.mkdir(parents=True, exist_ok=True)
    name = str(student_id).strip() if student_id is not None else "student"
    output_file = output_folder / (name + "_timetable.csv")

    columns = ["course_id", "room_id", "slot_id", "instructor_id",
               "cohort_id", "day", "start_time", "end_time"]
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        ordered = sorted(schedule.items(), key=lambda item: (
            weekdays.index(data["slots_by_id"][item[1][1]]["day"])
            if data["slots_by_id"][item[1][1]]["day"] in weekdays else 5,
            data["slots_by_id"][item[1][1]]["start_time"],
            item[1][0], item[0]
        ))
        for course_id, (room_id, slot_id) in ordered:
            course = data["courses_by_id"][course_id]
            slot = data["slots_by_id"][slot_id]
            writer.writerow({
                "course_id": course_id,
                "room_id": room_id,
                "slot_id": slot_id,
                "instructor_id": course["instructor_id"],
                "cohort_id": "; ".join(course["cohort_ids"]),
                "day": slot["day"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"],
            })

    print("Courses scheduled:", len(schedule))
    print("Hard constraint violations:", len(errors))
    print("Soft penalty before local search:", original_penalty)
    print("Soft penalty after local search:", soft_penalty(schedule, data))
    print("Backtracking nodes:", solver.nodes_expanded)
    print("Backtracks:", solver.backtracks)
    print("Saved timetable:", output_file)
    return str(output_file)


if __name__ == "__main__":
    studentscheduler()
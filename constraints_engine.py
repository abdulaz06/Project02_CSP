from collections import defaultdict


def minutes(value):
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def overlap(a, b):
    return (a["day"] == b["day"] and
            minutes(a["start_time"]) < minutes(b["end_time"]) and
            minutes(b["start_time"]) < minutes(a["end_time"]))


def suitable_room(course, room):
    if room.get("available_for_regular_classes", "").strip().lower() != "yes":
        return False
    if int(room["scheduling_capacity"]) < course["enrollment_count"]:
        return False

    room_type = room.get("room_type", "").lower()
    features = room.get("features_or_constraints", "").lower()
    requirement = course.get("required_room_type", "").lower().strip()
    if "computer lab" in requirement:
        return "computer lab" in room_type or "workstations" in features
    if requirement == "lab":
        return "lab" in room_type or "workstations" in features
    if requirement and requirement not in room_type:
        return False

    return True


def check_schedule(schedule, data):
    courses = data["courses_by_id"]
    rooms = data["rooms_by_id"]
    slots = data["slots_by_id"]
    errors = []

    if set(schedule) != set(courses):
        errors.append("Some courses are missing or not in the input data")

    for course_id, (room_id, slot_id) in schedule.items():
        if course_id not in courses or room_id not in rooms or slot_id not in slots:
            errors.append("Unknown course, room, or time slot: " + course_id)
        elif not suitable_room(courses[course_id], rooms[room_id]):
            errors.append("Room capacity, availability, or type problem: " + course_id)
        else:
            instructor_id = courses[course_id]["instructor_id"]
            inst = data["instructors_by_id"].get(instructor_id, {})
            unavailable = [x.strip() for x in inst.get("unavailable_slots", "").split(";") if x.strip()]
            if any(overlap(slots[slot_id], slots[unavailable_id])
                   for unavailable_id in unavailable if unavailable_id in slots):
                errors.append("Instructor unavailable: " + course_id)

    ids = list(schedule)
    for i in range(len(ids)):
        a = ids[i]
        if a not in courses or schedule[a][1] not in slots:
            continue
        for b in ids[i + 1:]:
            if b not in courses or schedule[b][1] not in slots:
                continue
            room_a, slot_a = schedule[a]
            room_b, slot_b = schedule[b]
            if not overlap(slots[slot_a], slots[slot_b]):
                continue
            if room_a == room_b:
                errors.append("Room double-booked: " + a + " and " + b)
            instructor = courses[a]["instructor_id"]
            if instructor and instructor == courses[b]["instructor_id"]:
                errors.append("Instructor double-booked: " + a + " and " + b)
            if set(courses[a]["cohort_ids"]) & set(courses[b]["cohort_ids"]):
                errors.append("Student cohort double-booked: " + a + " and " + b)
    return errors


def soft_penalty(schedule, data):
    courses, rooms, slots = data["courses_by_id"], data["rooms_by_id"], data["slots_by_id"]
    penalty = 0.0
    by_cohort = defaultdict(list)

    for course_id, (room_id, slot_id) in schedule.items():
        course = courses[course_id]
        room = rooms[room_id]
        slot = slots[slot_id]
        instructor = data["instructors_by_id"].get(course["instructor_id"], {})
        preferred = [x.strip() for x in instructor.get("preferred_slots", "").split(";") if x.strip()]
        if preferred and slot_id not in preferred:
            penalty += 10  # S1: Instructor preference

        extra_seats = int(room["scheduling_capacity"]) - course["enrollment_count"]
        if extra_seats > 30:
            penalty += 5 * (extra_seats - 30) / 30  # S2: Oversized room

        requested = data["preferred_rooms"].get(course_id)
        if requested in rooms and suitable_room(course, rooms[requested]) and room_id != requested:
            penalty += 8  # Explicit preferred room request

        if course.get("scheduling_context", "").lower().startswith("lab/section"):
            if "lab" not in room.get("room_type", "").lower() and "workstations" not in room.get("features_or_constraints", "").lower():
                penalty += 2  # Prefer a lab when the activity is lab/section

        suggested_rooms = course["suggested_rooms"]
        if room_id not in suggested_rooms and any(
            r in rooms and suitable_room(course, rooms[r]) for r in suggested_rooms
        ):
            penalty += 2  # C011: prefer previously mentioned rooms if suitable

        for cohort_id in course["cohort_ids"]:
            by_cohort[(cohort_id, slot["day"])].append((slot, room))

    for sessions in by_cohort.values():
        sessions.sort(key=lambda pair: minutes(pair[0]["start_time"]))
        streak = 1
        for (prev, old_room), (nxt, new_room) in zip(sessions, sessions[1:]):
            gap = minutes(nxt["start_time"]) - minutes(prev["end_time"])
            if gap > 20:
                penalty += 8 * (gap // 60)  # S3: Dead hours
            if 0 <= gap <= 15:
                streak += 1
                if streak > 2:
                    penalty += 12  # S4: Long consecutive run
                if old_room["building"] != new_room["building"]:
                    penalty += 6  # S5: Building transit
            else:
                streak = 1
    return round(penalty, 2)
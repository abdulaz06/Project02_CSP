import random
from collections import defaultdict

from constraints_engine import overlap, suitable_room, soft_penalty


class TimetableSolver:
    def __init__(self, data):
        self.data = data
        self.courses = data["courses_by_id"]
        self.rooms = data["rooms_by_id"]
        self.slots = data["slots_by_id"]
        self.assignment = {}
        self.nodes_expanded = 0
        self.backtracks = 0

        self.overlapping_slots = {
            slot_id: [other for other, entry in self.slots.items() if overlap(slot, entry)]
            for slot_id, slot in self.slots.items()
        }
        self.room_busy = defaultdict(int)
        self.teacher_busy = defaultdict(int)
        self.cohort_busy = defaultdict(int)

        self.domains = {}
        for course_id, course in self.courses.items():
            possible_rooms = [room_id for room_id, room in self.rooms.items()
                              if suitable_room(course, room)]
            instructor = self.data["instructors_by_id"].get(course["instructor_id"], {})
            unavailable = [s.strip() for s in instructor.get("unavailable_slots", "").split(";") if s.strip()]
            possible_slots = [slot_id for slot_id in self.slots
                              if not any(overlap(self.slots[slot_id], self.slots[u])
                                         for u in unavailable if u in self.slots)]
            choices = [(room, slot) for room in possible_rooms for slot in possible_slots]
            if not choices:
                raise ValueError("No valid room/time options for " + course_id)
            self.domains[course_id] = choices

        self.degree = {}
        for a in self.courses:
            count = 0
            for b in self.courses:
                if a == b:
                    continue
                same_teacher = (self.courses[a]["instructor_id"] and
                                self.courses[a]["instructor_id"] == self.courses[b]["instructor_id"])
                same_cohort = bool(set(self.courses[a]["cohort_ids"]) &
                                   set(self.courses[b]["cohort_ids"]))
                if same_teacher or same_cohort:
                    count += 1
            self.degree[a] = count

    def allowed(self, course_id, choice):
        room_id, slot_id = choice
        if self.room_busy[(room_id, slot_id)]:
            return False
        course = self.courses[course_id]
        teacher = course["instructor_id"]
        if teacher and self.teacher_busy[(teacher, slot_id)]:
            return False
        for cohort_id in course["cohort_ids"]:
            if self.cohort_busy[(cohort_id, slot_id)]:
                return False
        return True

    def put(self, course_id, choice):
        room_id, slot_id = choice
        self.assignment[course_id] = choice
        course = self.courses[course_id]
        for blocked in self.overlapping_slots[slot_id]:
            self.room_busy[(room_id, blocked)] += 1
            if course["instructor_id"]:
                self.teacher_busy[(course["instructor_id"], blocked)] += 1
            for cohort_id in course["cohort_ids"]:
                self.cohort_busy[(cohort_id, blocked)] += 1

    def take_out(self, course_id):
        room_id, slot_id = self.assignment.pop(course_id)
        course = self.courses[course_id]
        for blocked in self.overlapping_slots[slot_id]:
            self.room_busy[(room_id, blocked)] -= 1
            if course["instructor_id"]:
                self.teacher_busy[(course["instructor_id"], blocked)] -= 1
            for cohort_id in course["cohort_ids"]:
                self.cohort_busy[(cohort_id, blocked)] -= 1

    def legal_values(self, course_id):
        return [choice for choice in self.domains[course_id] if self.allowed(course_id, choice)]

    def mrv(self):
        variable = None
        smallest = None
        choices_for_variable = []
        for course_id in self.courses:
            if course_id in self.assignment:
                continue
            choices = self.legal_values(course_id)
            key = (len(choices), -self.degree[course_id])
            if smallest is None or key < smallest:
                smallest = key
                variable = course_id
                choices_for_variable = choices
            if not choices:
                break
        return variable, choices_for_variable

    def lcv(self, course_id, values):
        course = self.courses[course_id]
        requested = self.data["preferred_rooms"].get(course_id)
        teacher = course["instructor_id"]
        preferred = self.data["instructors_by_id"].get(teacher, {}).get("preferred_slots", "")
        preferred_slots = [s.strip() for s in preferred.split(";") if s.strip()]

        others = []
        for other_id, other in self.courses.items():
            if other_id == course_id or other_id in self.assignment:
                continue
            same_teacher = bool(teacher and teacher == other["instructor_id"])
            same_cohort = bool(set(course["cohort_ids"]) & set(other["cohort_ids"]))
            other_rooms = {room for room, slot in self.domains[other_id]}
            other_slots = {slot for room, slot in self.domains[other_id]}
            others.append((same_teacher or same_cohort, other_rooms, other_slots))

        def score(choice):
            room_id, slot_id = choice
            room = self.rooms[room_id]
            extra = int(room["scheduling_capacity"]) - course["enrollment_count"]
            cost = max(0, extra - 30) / 6
            if requested in self.rooms and suitable_room(course, self.rooms[requested]) and room_id != requested:
                cost += 8
            if preferred_slots and slot_id not in preferred_slots:
                cost += 10
            if course.get("scheduling_context", "").lower().startswith("lab/section"):
                if "lab" not in room.get("room_type", "").lower() and "workstations" not in room.get("features_or_constraints", "").lower():
                    cost += 2
            listed = course["suggested_rooms"]
            if room_id not in listed and any(
                r in self.rooms and suitable_room(course, self.rooms[r]) for r in listed
            ):
                cost += 2

            lost_choices = 0
            for related, other_rooms, other_slots in others:
                time_count = sum(s in other_slots for s in self.overlapping_slots[slot_id])
                if related:
                    lost_choices += time_count * len(other_rooms)
                elif room_id in other_rooms:
                    lost_choices += time_count
            cost += lost_choices * 0.01

            start_hour = int(self.slots[slot_id]["start_time"].split(":")[0])
            cost += abs(start_hour - 11) * 0.02
            cost += 0.05 * sum(current_slot in self.overlapping_slots[slot_id]
                               for current_room, current_slot in self.assignment.values())
            return cost

        return sorted(values, key=score)

    def forward_checking(self):
        for course_id in self.courses:
            if course_id not in self.assignment:
                if not any(self.allowed(course_id, choice) for choice in self.domains[course_id]):
                    return False
        return True

    def backtracking(self):
        self.nodes_expanded += 1
        if len(self.assignment) == len(self.courses):
            return True

        course_id, options = self.mrv()
        if not options:
            self.backtracks += 1
            return False

        for choice in self.lcv(course_id, options):
            self.put(course_id, choice)
            if self.forward_checking() and self.backtracking():
                return True
            self.take_out(course_id)
        self.backtracks += 1
        return False

    def min_conflicts_improvement(self, passes=2, seed=11):
        rng = random.Random(seed)
        for _ in range(passes):
            improved = False
            course_ids = list(self.courses)
            rng.shuffle(course_ids)
            for course_id in course_ids:
                old = self.assignment[course_id]
                before = soft_penalty(self.assignment, self.data)
                self.take_out(course_id)

                choices = self.legal_values(course_id)
                ordered = self.lcv(course_id, choices)
                candidates = ordered[:12] + rng.sample(choices, min(25, len(choices)))
                if old not in candidates:
                    candidates.append(old)

                best = old
                best_score = before
                for choice in candidates:
                    self.assignment[course_id] = choice
                    score = soft_penalty(self.assignment, self.data)
                    if score < best_score:
                        best_score = score
                        best = choice
                del self.assignment[course_id]
                self.put(course_id, best)
                if best_score < before:
                    improved = True
            if not improved:
                break
        return dict(self.assignment)

    def solve(self):
        if not self.backtracking():
            raise ValueError("No timetable could be found with these constraints.")
        initial_score = soft_penalty(self.assignment, self.data)
        self.min_conflicts_improvement()
        return dict(self.assignment), initial_score
# Project 2 Report: University Class Scheduling & Timetable Optimization

> [!IMPORTANT]
> **AUTOGRADER COMPLIANCE INSTRUCTIONS:**
> This report is parsed automatically by the autograder. To ensure you receive full credit for your work:
> 1. **Do not modify** the section headers (`## ...`) or bold field keys (e.g., `**Name:**`, `**Total Courses Configured:**`, `**Video Presentation Link:**`, etc.).
> 2. **Write your answers directly after** the colon `:` of each field, replacing the placeholder text completely (including the outer brackets `[` and `]`).
> 3. **Maintain the file structure**. Changing headers, bold titles, or deleting lines can cause the autograder to miss your responses and award 0 marks.

---

## Student Information 
- **Name:** Abdul Azeem Asharaf Ali
- **UID (netID):** aasha4
- **UIN:** 667352085

---

## Section 1: Dataset & University Configuration
- **Total Courses Configured:** [Write total number of courses here, must be 15 or more]
- **Total Rooms Configured:** [Write total number of rooms here, must be 6 or more]
- **Total Time Slots Configured:** [Write total number of time slots here, must be 15 or more]

---

## Section 2: Local Verification & Implemented Solvers
*Check the algorithms and features you successfully ran and verified by placing an `x` in the brackets (e.g., `[x]`):*
- [x] DataLoader & CSV Parsing
- [x] Hard Constraint Validation Engine
- [x] Soft Penalty & Quality Evaluation Engine
- [x] CSP Backtracking with MRV + LCV + Forward Checking
- [x] Min-Conflicts CSP Local Search
- [x] Timetable CSV Export (<studentid>_timetable.csv)

---

## Section 3: Video Presentation & Project Structure
- **Video Presentation Link:** [Provide an accessible link to your 5–7 minute video presentation]
- **Project Directory Structure:** `app.py` is the entry point and exports the timetable. `data_loader.py` reads and connects the CSV datasets, including the course/cohort and instructor information. `constraints_engine.py` checks hard rules and calculates soft penalties. `solver.py` has the backtracking solver with MRV, Degree, LCV, Forward Checking, and local search to improve the schedule. The `data/` folder contains the input CSV files and generated timetable. The original project guidelines and README are kept in the main folder.

---

## Section 4: Discussion & Problem Formulation
*Provide your written analysis for each point by replacing the bracket placeholders below:*
- **How did you formulate the variables, domains, and constraints for this scheduling problem?**
    I used each course as a CSP variable. Its domain contains possible pairs of rooms and time slots. I removed options that break single-course rules, like room capacity, unavailable rooms, explicitly required room types, or a recorded instructor's unavailable time slots. When comparing two courses, I check whether their times overlap. They cannot use the same room, the same assigned instructor, or the same mandatory student cohort at overlapping times. All 65 courses need to be assigned. Once a valid schedule is found, I calculate soft penalties for instructor preferences (when they are provided), oversized rooms, gaps, long consecutive schedules, building changes, and requested rooms. The provided CSV does not include enrollment for electives or instructor preferences, so I used an assumed enrollment of 30 for those courses and did not invent unavailable/preferred slots.
- **Compare CSP Backtracking (with heuristics) vs Local Search (Min-Conflicts) in terms of scalability, completeness, and solution quality.**
    Backtracking builds a timetable one course at a time and can backtrack if a choice stops the remaining courses from being scheduled. MRV chooses the course with the fewest legal choices, Degree breaks ties using connected courses, LCV prefers choices that restrict other courses less, and Forward Checking detects empty domains before going deeper. Backtracking can find a complete answer if one exists, but it may get slow for larger problems. Min-Conflicts usually starts with a complete assignment and changes values to reduce conflicts; it can be faster for big problems but does not guarantee a solution. In my project I start local search from the valid backtracking timetable and try legal moves that lower the soft penalty, so the hard constraints stay satisfied.
- **How can modern AI / LLM techniques be combined with CSP solvers for real-world automated university scheduling?**
    An LLM could help staff turn written requests, such as needing a room with computers or avoiding a certain time, into structured scheduling inputs. The CSP solver would still be responsible for checking the hard constraints and finding an actual valid timetable. Afterward, AI could explain why a course got a certain room or suggest which preferences need to change if there is no solution. I would still want a person to review the suggestions, since an LLM can misunderstand requirements and should not be trusted as the final rule checker.

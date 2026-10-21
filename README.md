# Project 2: University Class Scheduling & Timetable Optimizer (CSP)

## Project Overview

In this assignment, you will model and implement an automated intelligent class scheduling system for university Computer Science courses. You will formulate the scheduling problem as a **Constraint Satisfaction Problem (CSP)**, enforce hard constraints (zero double-bookings, room capacity limits, instructor availability, cohort clash prevention), optimize soft constraints using heuristics and local search (MRV, LCV, Forward Checking, Min-Conflicts), and generate an academic timetable exported as `<studentid>_timetable.csv`.

The datasets are provided in the `data/` directory. You will implement the main entry point `studentscheduler()` inside `app.py`. You have full freedom in how you organize your internal classes, modules, and folder structure.

### Learning Objectives

1. **CSP Formulation:** Formulate a real-world scheduling problem into Variables ($X$), Domains ($D$), and Hard/Soft Constraints ($C$).
2. **Constraint Engine & Validation:** Model and enforce hard constraints and calculate soft constraint penalty scores.
3. **Heuristic CSP Search:** Implement CSP Backtracking enhanced with Minimum Remaining Values (MRV), Degree Heuristic, Least Constraining Value (LCV), and Forward Checking.
4. **Local Search:** Implement Min-Conflicts local search for soft constraint optimization.
5. **Dynamic Timetable Export:** Read relational datasets dynamically and export the generated schedule to `<studentid>_timetable.csv`.

---

## Submission Guidelines

### 1. Preparation Checklist
Before submitting, verify that:
* [x] You have implemented your scheduler in or called from `studentscheduler()` in `app.py`.
* [x] Running `studentscheduler()` dynamically reads from `data/` and generates `<studentid>_timetable.csv` in `data/`.
* [x] Your code works dynamically when datasets are updated.
* [x] You have completed the AI Student Declaration on [PETRA AI](https://www.petraai.org/student) and saved it as `AI_declaration.png` in the repository root.
* [x] You have completed all sections in `report.md` (with your Name, UID (netID), UIN, video presentation link, directory structure explanation, and discussion). Do not alter the structure of `report.md`.
* [ ] You have recorded a 5–7 minute video presentation (.mp4, face visible) explaining your project directory structure, problem formulation, and demonstration of `studentscheduler()`, and uploaded it to YouTube, Google Drive, or Dropbox (with accessible view permission).

### 2. How to Submit
Submit all required files (including `app.py`, `report.md`, `AI_declaration.png`, and `data/`) to **Gradescope** under **Project 2**.

---

## Running and Testing Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Local Autograder
```bash
pytest tests/
```
A scorecard summarizing your earned marks will be output directly in the terminal under the section **"AUTOGRADING SCORECARD"**.

---

## Grading Scheme (100 Marks Total)

* **Autograder Evaluation (70 Marks Maximum):**
  - Project Implementation & Datasets (`app.py`, `data/*.csv`, `studentscheduler()`, `<studentid>_timetable.csv`): **40 marks**
  - Report Completion (`report.md`): **30 marks**
* **Manual Evaluation (30 Marks Total):**
  - Schedule Correctness & Hard Constraints: **15 marks**
  - Soft Constraint Optimization & Solution Quality: **5 marks**
  - Video Presentation: **10 marks**

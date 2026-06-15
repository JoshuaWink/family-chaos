# Family Chaos — Scheduling Puzzle Game

A browser-based scheduling puzzle game. Arrange the Smith family's 12 daily tasks across 10 people, then simulate to catch conflicts.

**Zero external dependencies** — pure Python stdlib + vanilla JS.

## Quick Start

```bash
python server.py
# → http://127.0.0.1:8094
```

Then open your browser. Press **New Game** to load the Smith family scenario.

## Gameplay

- **Tasks tab** — 12 family tasks with context (who it's for, travel time, notes)
- **People tab** — character profiles: age, occupation, driving status, bio, likes
- **Grid** — click a task, then click a time slot to assign it
- **Workload dots** — green/yellow/red per person based on how many tasks they have
- **Person overlay** — click a person's name in the grid for full profile + today's load
- **Import .ics** — import events from a Google Calendar `.ics` export and schedule them too
- **Simulate** — detect double bookings, travel conflicts, and shared-resource clashes

## The Smith Family

| Person | Age | Role |
|--------|-----|------|
| Alex (Dad) | 42 | Software Engineer, WFH |
| Jordan (Mom) | 40 | Part-time Nurse |
| Riley (Kid A) | 14 | 8th Grader — soccer + piano |
| Casey (Kid B) | 7 | 2nd Grader — tutoring + piano |
| Taylor (Kid C) | 4 | Preschooler — dentist today |
| Morgan (Grandma) | 68 | Retired teacher, local driver |
| Sam (Grandpa) | 70 | Retired, can't drive post-stroke |
| Jamie (Coach) | 35 | Soccer coach |
| Avery (Tutor) | 28 | Freelance math tutor |
| Drew (Neighbor) | 45 | WFH accountant, emergency backup |

## Running Tests

```bash
pytest -q
```

All 13 tests cover the API, session store, scenario generator, and simulation engine.

## Structure

```
server.py              # Entry point — HTTP + UI server on port 8094
game/
  scheduling_game/     # Core game logic (zero deps)
    person.py          # Person entity with profiles
    task.py            # Task entity with context
    scenario_generator.py  # Deterministic Smith family scenario
    simulation_engine.py   # Conflict detection
    scheduling_game_service.py
    scheduling_game_http_server.py
    game_ui.py         # Self-contained HTML/CSS/JS UI
    ...
tests/
  test_scheduling_game_*.py
```

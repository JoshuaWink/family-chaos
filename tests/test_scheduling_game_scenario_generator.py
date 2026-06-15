"""Tests for scheduling game scenario generation."""

from game.scheduling_game import ScenarioGenerator


class TestScenarioGenerator:
    """Scenario generator returns deterministic baseline game state."""

    def test_generate_normal_returns_people_and_tasks(self):
        generator = ScenarioGenerator()
        scenario = generator.generate("normal")

        people = scenario.get("people") or []
        tasks = scenario.get("tasks") or []

        assert len(people) >= 10
        assert len(tasks) >= 12

        assert all(person.person_id for person in people)
        assert all(person.name for person in people)

        assert all(task.task_id for task in tasks)
        assert all(task.description for task in tasks)
        assert all(task.duration_minutes > 0 for task in tasks)

    def test_generate_normal_is_deterministic(self):
        generator = ScenarioGenerator()
        scenario_a = generator.generate("normal")
        scenario_b = generator.generate("normal")

        people_ids_a = [person.person_id for person in scenario_a.get("people") or []]
        people_ids_b = [person.person_id for person in scenario_b.get("people") or []]
        assert people_ids_a == people_ids_b

        task_ids_a = [task.task_id for task in scenario_a.get("tasks") or []]
        task_ids_b = [task.task_id for task in scenario_b.get("tasks") or []]
        assert task_ids_a == task_ids_b

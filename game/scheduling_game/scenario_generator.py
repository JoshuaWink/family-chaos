"""Deterministic scenario generator for scheduling game MVP."""

from typing import Dict, List

from .person import Person
from .task import Task


class ScenarioGenerator:
    """Build deterministic scenario payloads for gameplay sessions."""

    def generate(self, difficulty: str = "normal") -> Dict[str, object]:
        """Return a scenario dictionary for the requested difficulty."""
        level = (difficulty or "normal").strip().lower()
        if level != "normal":
            raise ValueError("Only 'normal' difficulty is available in M0.")

        return {
            "scenario_id": "family_chaos_normal_001",
            "difficulty": level,
            "people": self._build_people(),
            "tasks": self._build_tasks(),
        }

    def _build_people(self) -> List[Person]:
        return [
            Person(
                person_id="p1", name="Alex (Dad)", home_location="home",
                age=42, can_drive=True,
                occupation="Software Engineer",
                work_schedule="WFH Mon–Fri, 9 am–5 pm",
                bio=(
                    "Alex is the primary breadwinner working remotely. He has flexibility "
                    "between meetings but his 9 am stand-up is non-negotiable. Great cook "
                    "and loves being involved in the kids' activities on weekends."
                ),
                likes="hiking, gaming, weekend BBQs, cooking new recipes",
            ),
            Person(
                person_id="p2", name="Jordan (Mom)", home_location="home",
                age=40, can_drive=True,
                occupation="Part-time Nurse",
                work_schedule="Tues, Thurs, Sat — 7 am to 3 pm",
                bio=(
                    "Jordan works three hospital shifts a week. On off-days she manages "
                    "the household, coordinates the kids' schedules, and tries to squeeze "
                    "in a yoga class. She knows everyone's routines better than anyone."
                ),
                likes="reading, yoga, gardening, true crime podcasts",
            ),
            Person(
                person_id="p3", name="Riley (Kid A)", home_location="home",
                age=14, can_drive=False,
                occupation="8th Grade Student",
                work_schedule="School Mon–Fri, 7:45 am–3:00 pm",
                bio=(
                    "Riley is an energetic 8th grader who loves soccer and recently started "
                    "piano. She needs rides to both activities and gets anxious if she misses "
                    "practice. Very independent but still needs adult transport."
                ),
                likes="soccer, piano, video games, graphic novels",
                primary_driver_id="p1",
            ),
            Person(
                person_id="p4", name="Casey (Kid B)", home_location="home",
                age=7, can_drive=False,
                occupation="2nd Grade Student",
                work_schedule="School Mon–Fri, 8:15 am–2:45 pm",
                bio=(
                    "Casey is a curious 7-year-old obsessed with dinosaurs and Legos. He's "
                    "been struggling with multiplication and has weekly tutoring with Avery. "
                    "Loves piano lessons too — Ms. Chen says he has great rhythm."
                ),
                likes="dinosaurs, Legos, drawing, piano, math puzzles",
                primary_driver_id="p2",
            ),
            Person(
                person_id="p5", name="Taylor (Kid C)", home_location="home",
                age=4, can_drive=False,
                occupation="Preschooler",
                work_schedule="Preschool Mon–Fri, 9:00 am–12:00 pm",
                bio=(
                    "Taylor is the youngest Smith and full of energy. She loves dancing and "
                    "toy trucks. Dentist visits are a battle — she needs a parent she trusts "
                    "to stay calm. Naps are sacred from 1–3 pm."
                ),
                likes="dancing, toy trucks, storytime, singing, bubbles",
                primary_driver_id="p2",
            ),
            Person(
                person_id="p6", name="Morgan (Grandma)", home_location="grandma_house",
                age=68, can_drive=True,
                occupation="Retired Teacher",
                work_schedule="Fully flexible — prefers mornings",
                bio=(
                    "Morgan is a retired elementary teacher who lives 15 minutes away. She's "
                    "a huge help but prefers not to drive on highways or after dark. She loves "
                    "the grandkids but needs notice before babysitting."
                ),
                likes="gardening, baking, crossword puzzles, game shows",
            ),
            Person(
                person_id="p7", name="Sam (Grandpa)", home_location="grandma_house",
                age=70, can_drive=False,
                occupation="Retired",
                work_schedule="Fully flexible",
                bio=(
                    "Sam retired 3 years ago after a minor stroke that left him unable to "
                    "drive safely. He manages well at home with Morgan, but needs someone to "
                    "pick up his monthly prescriptions from Walgreens."
                ),
                likes="chess, baseball, history books, morning crosswords",
                primary_driver_id="p6",
            ),
            Person(
                person_id="p8", name="Jamie (Coach)", home_location="gym",
                age=35, can_drive=True,
                occupation="Soccer Coach / Personal Trainer",
                work_schedule="Runs practice 4:00–5:30 pm, flexible otherwise",
                bio=(
                    "Jamie coaches Riley's soccer team and is extremely reliable. Not a family "
                    "member but often helps coordinate logistics around practice days."
                ),
                likes="fitness, outdoor sports, nutrition, coaching youth",
            ),
            Person(
                person_id="p9", name="Avery (Tutor)", home_location="library",
                age=28, can_drive=True,
                occupation="Freelance Math Tutor",
                work_schedule="Available most weekdays, sessions by appointment",
                bio=(
                    "Avery tutors Casey twice a week at the public library. Very patient "
                    "and uses game-based teaching. Sessions are 60 min and need advance "
                    "booking. Casey has been making great progress."
                ),
                likes="math puzzles, hiking, board games, teaching",
            ),
            Person(
                person_id="p10", name="Drew (Neighbor)", home_location="neighborhood",
                age=45, can_drive=True,
                occupation="Works from Home (Accountant)",
                work_schedule="WFH Mon–Fri, very flexible",
                bio=(
                    "Drew is the Smiths' helpful neighbor three houses down. Has offered to "
                    "help with emergency pickups. Reliable but shouldn't be over-relied on "
                    "— he has his own work deadlines."
                ),
                likes="DIY projects, neighborhood watch, cooking, gardening",
            ),
        ]

    def _build_tasks(self) -> List[Task]:
        return [
            Task(
                task_id="t1", description="Drop Riley at school",
                duration_minutes=20, location="school",
                for_person_id="p3", travel_minutes=20,
                notes=(
                    "Jefferson Middle starts at 7:45 am. Riley needs drop-off by 7:40 am. "
                    "Requires a licensed driver. Pick-up is a separate task (t9)."
                ),
            ),
            Task(
                task_id="t2", description="Drop Casey at preschool",
                duration_minutes=20, location="preschool",
                for_person_id="p4", travel_minutes=20,
                notes=(
                    "Sunshine Elementary starts at 8:15 am. Casey can be dropped off together "
                    "with Riley if the timing works — note they attend different schools."
                ),
            ),
            Task(
                task_id="t3", description="Dentist appointment — Taylor",
                duration_minutes=60, location="clinic",
                for_person_id="p5", travel_minutes=30,
                notes=(
                    "Taylor's 6-month checkup at Dr. Park's Pediatric Dental. Appointment "
                    "at 10 am — allow 30 min travel each way. Taylor needs a parent or "
                    "trusted adult she's comfortable with."
                ),
            ),
            Task(
                task_id="t4", description="Alex work stand-up",
                duration_minutes=30, location="home_office",
                for_person_id="p1", travel_minutes=0,
                notes=(
                    "Alex's non-negotiable 9:00–9:30 am engineering sync. Fully remote — "
                    "no travel needed. He cannot drive or supervise kids during this window."
                ),
            ),
            Task(
                task_id="t5", description="Riley soccer practice",
                duration_minutes=90, location="field",
                resource_id="family_car",
                for_person_id="p3", travel_minutes=25,
                notes=(
                    "Riley's team practices with Coach Jamie at Memorial Field. Practice "
                    "runs 4:00–5:30 pm. Requires the family car for the 25-min drive."
                ),
            ),
            Task(
                task_id="t6", description="Casey math tutoring",
                duration_minutes=60, location="library",
                for_person_id="p4", travel_minutes=15,
                notes=(
                    "Weekly session with Avery at the public library. Casey is working on "
                    "multiplication. Sessions are 60 min; allow 15 min drive each way."
                ),
            ),
            Task(
                task_id="t7", description="Weekly grocery run",
                duration_minutes=30, location="market",
                resource_id="family_car",
                travel_minutes=20,
                notes=(
                    "Weekly groceries from Costco. ~30 min in-store + 20 min drive each "
                    "way. Family car trunk needed for bulk items. Any licensed driver can do this."
                ),
            ),
            Task(
                task_id="t8", description="Pick up Sam's prescriptions",
                duration_minutes=20, location="pharmacy",
                resource_id="family_car",
                for_person_id="p7", travel_minutes=20,
                notes=(
                    "Sam's monthly blood pressure and cholesterol meds from Walgreens. He "
                    "can't drive himself. Morgan normally does this but anyone with the car can help."
                ),
            ),
            Task(
                task_id="t9", description="After-school pickup — Riley",
                duration_minutes=30, location="school",
                for_person_id="p3", travel_minutes=20,
                notes=(
                    "Riley is dismissed at 3:00 pm. Must be picked up by 3:15 pm. If no "
                    "one arrives, the school calls — Riley gets anxious waiting in the office."
                ),
            ),
            Task(
                task_id="t10", description="Casey piano lesson",
                duration_minutes=45, location="music_studio",
                for_person_id="p4", travel_minutes=25,
                notes=(
                    "Weekly piano lesson with Ms. Chen at the music studio. Casey is working "
                    "on Grade 2 pieces. 45-min lesson, 25-min drive each way."
                ),
            ),
            Task(
                task_id="t11", description="Cook family dinner",
                duration_minutes=45, location="home",
                travel_minutes=0,
                notes=(
                    "Family eats together at 6:30 pm. Someone needs to start cooking by "
                    "5:30 pm. Alex or Jordan usually handle this — it's a decompression "
                    "activity for both."
                ),
            ),
            Task(
                task_id="t12", description="Kids evening routine",
                duration_minutes=30, location="home",
                travel_minutes=0,
                notes=(
                    "Bath time, homework check, and bedtime for all 3 kids. Takes ~30 min "
                    "per child minimum. Needs at least one parent home. Often both help to "
                    "split the load."
                ),
            ),
        ]

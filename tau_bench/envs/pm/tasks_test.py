
from tau_bench.types import Task, Action

TASKS_TEST = [
    Task(
        annotator="team",
        user_id="alice_smith_1001",
        instruction="You are alice_smith_1001 from the Web App Redesign project. Assign all high-priority tickets in the project to yourself and move them to in_progress.",
        actions=[
            Action(name="assign_user", kwargs={"ticket_id": "tick_001", "user_id": "alice_smith_1001"}),
            Action(name="update_status", kwargs={"ticket_id": "tick_001", "new_status": "in_progress"}),
            Action(name="assign_user", kwargs={"ticket_id": "tick_003", "user_id": "alice_smith_1001"}),
            Action(name="update_status", kwargs={"ticket_id": "tick_003", "new_status": "in_progress"}),
        ],
        outputs=["assigned", "in_progress"],
    ),
    Task(
        annotator="team",
        user_id="bob_johnson_1002",
        instruction="You are bob_johnson_1002 from the Web App Redesign project. Create two new tickets: 'Login page slow on mobile' with high priority and 'Search results not displaying' with medium priority.",
        actions=[
            Action(
                name="create_ticket",
                kwargs={
                    "project_id": "proj_web_app_2024",
                    "title": "Login page slow on mobile",
                    "description": "Mobile login experiences 3+ second delay",
                    "priority": "high",
                },
            ),
            Action(
                name="create_ticket",
                kwargs={
                    "project_id": "proj_web_app_2024",
                    "title": "Search results not displaying",
                    "description": "Search page shows no results",
                    "priority": "medium",
                },
            ),
        ],
        outputs=["Login page slow on mobile", "Search results not displaying"],
    ),
    Task(
        annotator="team",
        user_id="carol_williams_1003",
        instruction="You are carol_williams_1003 working on the Web App Redesign project. Move the ticket 'Update homepage banner' (tick_003) to in_review status.",
        actions=[
            Action(name="update_status", kwargs={"ticket_id": "tick_003", "new_status": "in_review"}),
        ],
        outputs=["in_review"],
    ),
    Task(
        annotator="team",
        user_id="david_brown_1004",
        instruction="You are david_brown_1004 from the Backend API Upgrade project. Assign the 'Optimize database queries' ticket (tick_005) to yourself and update its priority to low.",
        actions=[
            Action(name="assign_user", kwargs={"ticket_id": "tick_005", "user_id": "david_brown_1004"}),
            Action(name="update_priority", kwargs={"ticket_id": "tick_005", "priority": "low"}),
        ],
        outputs=["assigned", "low"],
    ),
    Task(
        annotator="team",
        user_id="alice_smith_1001",
        instruction="You are alice_smith_1001 working on the Web App Redesign project. Add a comment 'Ready for testing' to ticket tick_003 and then move it to done status.",
        actions=[
            Action(name="add_comment", kwargs={"ticket_id": "tick_003", "comment": "Ready for testing"}),
            Action(name="update_status", kwargs={"ticket_id": "tick_003", "new_status": "done"}),
        ],
        outputs=["Ready for testing", "done"],
    ),
]

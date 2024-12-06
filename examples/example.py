import tes
import json

# Define task
task = tes.Task(
    executors=[
        tes.Executor(
            image="alpine",
            command=["echo", "hello"]
        )
    ]
)

# Create client
cli = tes.HTTPClient("http://localhost:8000", timeout=5)

# Create and run task
task_id = cli.create_task(task)
cli.wait(task_id, timeout=5)

# Fetch task info
task_info = cli.get_task(task_id, view="BASIC")
j = json.loads(task_info.as_json())

# Pretty print task info
print(json.dumps(j, indent=2))

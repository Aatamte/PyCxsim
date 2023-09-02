import time
from src.caes.background_jobs.decorators import background_task
from src.caes.background_jobs.job_manager import JobManager

# Mock long running tasks


@background_task
def task_sleeps():
    time.sleep(2)


@background_task
def task_instant():
    pass

# Tests


def test_task_runs_in_background():
    start_time = time.time()
    task_sleeps()
    end_time = time.time()
    # Ensure that the decorated function returns immediately, not after 2 seconds
    assert (end_time - start_time) < 2


def test_job_manager_tracks_jobs():
    initial_job_count = len(JobManager.jobs)
    task_instant()  # This should add the job to the JobManager
    assert len(JobManager.jobs) == initial_job_count + 1

# Add more tests as required...

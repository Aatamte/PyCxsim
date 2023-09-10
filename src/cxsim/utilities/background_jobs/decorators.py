from .job_manager import JobManager
import threading


def background_task(func):
    def wrapper(*args, **kwargs):
        def inner():
            result = func(*args, **kwargs)
            # Handle the result here if necessary

        thread = threading.Thread(target=inner)
        thread.start()
        JobManager.add_job(thread)

    return wrapper


from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=1)


class BackgroundTask:
    def __init__(self, func, visualizer, agent_name: str = None, *args, **kwargs):
        self.func = func
        self.visualizer = visualizer
        self.args = args
        self.kwargs = kwargs
        self.agent_name = agent_name

    def run(self):
        self.func(*self.args, **self.kwargs)

    def __enter__(self):
        if self.agent_name:
            self.visualizer.top_panel.current_task = f"Background Task for {self.agent_name}"
        else:
            self.visualizer.top_panel.current_task = "Background Task"
        self.future = _executor.submit(self.run)

        # Continuously call visualizer.step(False) while the background task is running
        while not self.future.done():
            self.visualizer.step(False)
        self.visualizer.top_panel.current_task = "None"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Since ThreadPoolExecutor handles the thread lifecycle, we don't have
        # to manually join the thread. However, if you want to retrieve the result
        # or handle exceptions, you can use `self.future.result()`.
        pass
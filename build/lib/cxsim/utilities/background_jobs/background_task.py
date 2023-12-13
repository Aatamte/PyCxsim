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

        #self.visualizer.environment.log.debug("Entering BackgroundTask context manager.")

        if self.agent_name:
            self.visualizer.top_panel.current_task = f"Background Task for {self.agent_name}"
        else:
            self.visualizer.top_panel.current_task = "Background Task"
        self.future = _executor.submit(self.run)

        try:
            while not self.future.done():
                self.visualizer.step(False)
            self.future.result()  # Retrieve the result to re-raise any exceptions that occurred.
        except Exception as e:
            raise Exception(e)
            # Handle exception
            self.visualizer.top_panel.current_task = "Error occurred"
            print(f"An error occurred for {self.agent_name}: {e}")

        self.visualizer.top_panel.current_task = "None"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Since ThreadPoolExecutor handles the thread lifecycle, we don't have
        # to manually join the thread. However, if you want to retrieve the result
        # or handle exceptions, you can use `self.future.result()`.
        pass
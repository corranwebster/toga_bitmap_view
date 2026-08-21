import asyncio
from typing import ClassVar
from unittest.mock import Mock

import toga


# class ExampleDoc(toga.Document):
#     description: str = "Example Document"
#     extensions: ClassVar[list[str]] = ["testbed", "tbed"]

#     def create(self):
#         # Create the main window for the document.
#         self.main_window = toga.DocumentWindow(
#             doc=self,
#             content=toga.Box(),
#         )
#         self._content = Mock()

#     def read(self):
#         if self.path.name == "broken.testbed":
#             raise RuntimeError("Unable to load broken document")
#         else:
#             self._content.read(self.path)

#     def write(self):
#         self._content.write(self.path)


# class ReadonlyDoc(toga.Document):
#     description: str = "Read-only Document"
#     extensions: ClassVar[list[str]] = ["other"]

#     def create(self):
#         # Create the main window for the document.
#         self.main_window = toga.DocumentWindow(
#             doc=self,
#             content=toga.Box(),
#         )
#         self._content = Mock()

#     def read(self):
#         self._content.read(self.path)


class Testbed(toga.App):
    # Objects can be added to this list to avoid them being garbage collected in the
    # middle of the tests running. This is problematic, at least, for WebView (#2648).
    _gc_protector: ClassVar[list] = []

    def startup(self):
        # Toga installs a custom task factory to ensure that a strong reference to
        # long-lived tasks is retained until the task completes. This task factory is
        # used to verify that the custom task factory has been installed.
        toga_task_factory = self.loop.get_task_factory()

        def task_factory(loop, coro, **kwargs):
            task = toga_task_factory(loop, coro, **kwargs)
            assert task in self._running_tasks, f"missing task reference for {task}"
            return task

        self.loop.set_task_factory(task_factory)

        # Set a default return code for the app, so that a value is
        # available if the app exits for a reason other than the test
        # suite exiting/crashing.
        self.returncode = -1

        self.cmd_action = Mock()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = toga.Box(
            children=[
                toga.Label("Did you forget to use --test?"),
            ]
        )
        self.main_window.show()

    async def on_running(self):
        # As soon as the app is running and the main window is visible, use the GUI
        # thread to set a flag that the test suite can use as permission to proceed.
        # The NoQA is warning about using sleep in a loop, which would be good advice
        # if there was an underlying Event that we could await - but there isn't.
        try:
            async with asyncio.timeout(10):
                while not self.main_window.visible:  # noqa: ASYNC110
                    await asyncio.sleep(0.05)
            self.is_visible = True
        except TimeoutError:
            # No extra handling required in the app. The test thread will fail after 5
            # seconds, killing the test suite.
            pass
        print("main window visible")


def main(appname):
    if toga.backend == "toga_winforms":
        import toga_winforms

        if toga_winforms._use_dotnet_core:
            print("Running testbed using .NET Core")
        else:
            print("Running testbed using .NET Framework 4.x")

    return Testbed(
        app_name=appname,
    )

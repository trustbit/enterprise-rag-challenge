from openai import OpenAI
import time
import logging
from langfuse.decorators import langfuse_context
from langfuse.decorators import observe

class AssistantManager:
    """
    A manager class to interact with the OpenAI API for managing assistant threads and messages.

    Attributes:
        client (OpenAI): An instance of the OpenAI client.
        thread_id (str): The ID of the current thread.
        assistant_id (str): The ID of the assistant.
        last_message_id (str): The ID of the last message sent in the thread.
    """
    def __init__(self, api_key, assistant_id):
        """
        Initialize the AssistantManager with API key, assistant ID, and optional thread ID.

        Args:
            api_key (str): The API key for OpenAI.
            assistant_id (str): The ID of the assistant.
            thread_id (str, optional): The ID of the thread. Defaults to None.
        """
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        # self.last_message_id = None
        self.thread_id = None


    def create_thread(self):
        """
        Create a new thread.

        Returns:
            str: The ID of the newly created thread.
        """
        response = self.client.beta.threads.create()
        return response.id

    def _add_message_to_thread(self, thread_id, message):
        """
        Add a message to a thread.

        Args:
            thread_id (str): The ID of the thread.
            message (str): The message content.

        Returns:
            dict: The message object returned by the API.
        """
        logging.info(f"Adding message to thread {thread_id}: {message}")
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message)
        logging.info(f"Message added to thread {thread_id} with ID: {message.id}")
        self.last_message_id = message.id

        return message

    def _wait_on_run(self, run, thread_id):
        """
        Wait for a run to complete.

        Args:
            run (dict): The run object.
            thread_id (str): The ID of the thread.

        Returns:
            dict: The updated run object after completion.
        """
        logging.info(f"Waiting for run {run.id} to complete...")
        while run.status == "queued" or run.status == "in_progress":
            logging.info(f"Run {run.id} status: {run.status}")
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            time.sleep(1)
        logging.info(f"Run {run.id} completed with status: {run.status}")
        return run

    def _run_thread(self):
        """
        Run the thread and retrieve messages.

        Returns:
            run: A run object
        """


        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
        )
        self._wait_on_run(run, self.thread_id)
        return run

    def _message_list(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread_id, order="asc")

    @observe()
    def assistant_response(self, message, thread_id=None):
        logging.info(f"!!! Assistant run with message: {message}")
        self.thread_id = thread_id

        if thread_id is None:
            self.thread_id = self.create_thread()

        self._add_message_to_thread(self.thread_id, message)
        run = self._run_thread()

        messages = self._message_list()
        assistant_response = messages.data[-1].content[0].text.value

        message_log = self.client.beta.threads.messages.list(thread_id=self.thread_id)

        input_messages = [{"role": message.role, "content": message.content[0].text.value} for message in message_log.data[::-1][:-1]]

        # log internal generation within the openai assistant as a separate child generation to langfuse
        # get langfuse client used by the decorator, uses the low-level Python SDK
        langfuse_client = langfuse_context._get_langfuse()
        # pass trace_id and current observation ids to the newly created child generation
        langfuse_client.generation(
            trace_id=langfuse_context.get_current_trace_id(),
            parent_observation_id=langfuse_context.get_current_observation_id(),
            model=run.model,
            usage=run.usage,
            input=input_messages,
            output=assistant_response
        )
        logging.info(f"!!! Assistant response message: {assistant_response}")
        return assistant_response

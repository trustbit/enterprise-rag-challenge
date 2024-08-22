from openai import OpenAI
import time
import logging

class AssistantManager:
    """
    A manager class to interact with the OpenAI API for managing assistant threads and messages.

    Attributes:
        client (OpenAI): An instance of the OpenAI client.
        thread_id (str): The ID of the current thread.
        assistant_id (str): The ID of the assistant.
        last_message_id (str): The ID of the last message sent in the thread.
    """

    SCHEMA_SYSTEM_PROMPT = """
You are convertor
Note the schema specified for each question:

number - only a metric number is expected as an answer. No decimal commas or separators. Correct: 122333, incorrect: 122k, 122 233
name - only name of the company is expected as an answer. It must be exactly as the name of the company in a dataset
boolean - only yes or no (or true, false). Case doesn't matter.
Important! Each schema also allows N/A or n/a which means "Not Applicable" or "There is not enough information even for a human to answer this question".
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

    def assistant_response(self, message, thread_id=None):
        """
        Process a message and get a response from the assistant.

        Args:
            message (str): The message content to send to the assistant.
            thread_id (str, optional): The ID of the thread. Defaults to None.

        Returns:
            str: The assistant's response message.
        """
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

        logging.info(f"!!! Assistant response message: {assistant_response}")
        return assistant_response

    def format_response(self, schema, question):
        completion = self.client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": self.SCHEMA_SYSTEM_PROMPT},
        {"role": "user", "content": "Convert [input] to [schema]"
            "[schema]: {schema}"
            "[input]: {question}"},
        ])

        return completion.choices[0].message

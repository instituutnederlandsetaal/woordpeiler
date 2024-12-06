# This locust test script example will simulate a user
# browsing the Locust documentation on https://docs.locust.io

import random
from locust import HttpUser, between, task
import json


class AwesomeUser(HttpUser):
    host = "http://localhost:8000/"
    wait_time = between(5, 10)
    word_list = []

    def on_start(self):
        with open("words.txt", encoding="utf8") as f:
            self.word_list = f.read().split("\n")

    @task
    def search(self):
        self.client.request_name = "/word_frequency?lemma=[lemma]"
        self.client.get("word_frequency?wordform=" + random.choice(self.word_list))

        # with self.client.get(
        #     "word_frequency?lemma=" + random.choice(self.word_list), catch_response=True
        # ) as response:
        #     # parse json
        #     data = json.loads(response.text)
        #     if len(data) == 42:
        #         response.success()
        #     else:
        #         response.failure("incorrect number of results")

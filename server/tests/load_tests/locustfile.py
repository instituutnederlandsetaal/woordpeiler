# This locust test script example will simulate a user
# browsing the Locust documentation on https://docs.locust.io

import random
from locust import HttpUser, between, task
import json


class RandomUser(HttpUser):
    host = "http://localhost:8000/"
    wait_time = between(0.1, 0.2)
    word_list = []

    def on_start(self):
        with open("words.txt", encoding="utf8") as f:
            self.word_list = f.read().split("\n")

    @task
    def search(self):
        word = random.choice(self.word_list)
        url = "frequency?w=" + word
        self.client.request_name = url

        with self.client.get(url, catch_response=True) as response:
            data = json.loads(response.text)
            num_of_years = 42  # valid for 2024. This is just a simple check.
            if len(data) >= num_of_years:  # more years is ok.
                response.success()
            else:
                response.failure(f"incorrect number of results: {len(data)}")

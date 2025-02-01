from locust import HttpUser, task, between
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

"""
     With this is can mock the client polls for the requested grammar checks.

     start the load generation from the root dir:

          - locust -f locustfile.py --host=http://localhost:8000 --web-port=8089

"""



class GrammarCheckUser(HttpUser):
    
     wait_time = between(1, 5)

     # here I start with wrong ids. that are not handed out be the api
     classification_ids = ["930ß839ß9", "7940589048"]
     eval_ids = ["94380304", "jsjbajidod"]

     @task(6)
     def post_grammar_check(self):
          """Simulate sending a grammar check request"""
          text_samples = [
          "Last weekend, I went to the beach with my friends. We was very excited because it was the first time in months we all get together. The sun were shining when we arrived, but soon it started to rain. The waves was too strong, so we decide to just sit and talk. One of my friend bring snacks, but he forget to bring drinks, so we had nothing to drink. We should of checked the weather forecast before we went. After waiting for the rain to stop, we finally was able to walk along the shore. It was a fun day, but we got home very tired because of all the walking and carrying our stuff back to the car.",
     
          "Yesterday, I seen a movie with my brother. The plot was confusing, and I did not knew what happened at the end. The main character was different then I expected, and the actors performance wasnot great. My brother said he liked it, but I was bored most of the time. After the movie, we go to a restaurant, but the menu didn’t had much options. I ordered pasta, which tasted okay, but my brothers food was too salty. The waiter was rude, he didnot even listen us properly and bring the wrong drinks. We should have went somewhere else, but we was too hungry to find another place. Next time, I will choose a better restaurant and check the reviews before going.",
     
          "She don not like coffee, so she ordered a tea instead. However, the café was out of tea, so they gived her a juice. It wasnot what she wanted, but she drunk it anyways. The juice wasnot fresh, and she wished she had just gotten water instead. After that, she meet her friend at the park. They was talking about their plans for next weekend, but none of them was sure what to do. Her friend suggested to go hiking, but she said she dont like hiking because it makes her tired. Then they talked about going shopping, but they didn’t knew if they had enough money for that. At the end, they decide to just stay home and watch a movie instead. It wasnt the most exciting plan, but they agreed it was better than doing nothing."
          ]

          payload = {"text": np.random.choice(text_samples)}
          res = self.client.post("/api/grammarcheck", json=payload)

          if res.status_code == 200:
               json_data = res.json()
               classification_id = json_data.get("classification_id")
               if classification_id:
                    logger.info(f"requested new grammar check with ID : {classification_id}")
                    self.classification_ids.append(classification_id) 

     @task(3)
     def get_result(self):
          """Fetch results using stored classification IDs."""
          if self.classification_ids:
               classification_id = np.random.choice(self.classification_ids)
               res = self.client.get(f"/api/result?classification_id={classification_id}")
               logger.info(f"result for the id : {classification_id} : {res.text}")
     
     @task(1)
     def request_eval(self):
        res = self.client.get("/api/eval")
        json_res = res.json()
        new_eval_id = json_res["eval_id"]
        self.eval_ids.append(new_eval_id)
        logger.info(f"requested eval with id : {new_eval_id}")
        
     @task(1)
     def get_eval_result(self):
          eval_id = np.random.choice(self.eval_ids)
          res = self.client.get(f"/api/eval/result?eval_id={eval_id}")
          logger.info(f"this is the eval for ID: {res.text} ")

        


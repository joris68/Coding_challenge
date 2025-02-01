from fastapi.testclient import TestClient
from main import app


"""
     To tun this test file you should have a mongo instance running on docker desktop.

          run : docker compose -f docker-compose-test.yml up

          then run : python main_test.py from the root directory (where venv is)

"""

client = TestClient(app)

def test_helth_check():
     res = client.get("/api/health")
     assert res.status_code == 200
     print(res.json())

def test_too_large_text():
     res = client.post(
          "/api/grammarcheck",
          json={
               "text": '''Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.  Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.   
               Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.  At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur'''
          }
     )

     print(res.status_code)

def text_too_small():
     res = client.post(
          "/api/grammarcheck",
          json={
               "text": '''Lorem sl ut  consequat.   
               . Lorem ipsum dolor sit amet, consetetur'''
          }
     )
     print(res.status_code)

def good_grammar_request():
     res = client.post(
          "/api/grammarcheck",
          json={
               "text": '''Last weekend, I went to the beach with my freinds to enjoy the sun. The weather was perfect, but we forgot to bring sunscreen, wich was a big mistake. As a result, we all got sunburns and had to go back home earlyer than expected. Even though it wasn’t the best day, we still had fun and made some nice memories. I thik next time we weill be more careful and plan ahead. But thats part of the adventure right? I am just glad we were able to laugh about it at the end.'''
          }
     )
     json_response = res.json()
     return json_response["classification_id"]


def good_grammar_request_result(classification_id):
     res = client.get(f"/api/result?classification_id={classification_id}")
     print(res.json())

def eval_request():
     res = client.get("/api/eval")
     return res.json()["eval_id"]


def eval_request_result(eval_id):
     res = client.get(f"/api/eval/result?eval_id={eval_id}")
     print(res.json())

test_helth_check()
test_too_large_text()
text_too_small()
class_id= good_grammar_request()
good_grammar_request_result(classification_id=class_id)
eval_id = eval_request()
eval_request_result(eval_id=eval_id)

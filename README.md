# Coding_challenge

# Grammar Check Backend

     This is a backend consisting of fastAPI and MongoDB. It implements a multiclass classification grammar check using structured outputs
     with openAI's 4o-mini api.

# Prerequisites

     - Python >= 3.10
     - docker desktop
     - pip


# Testing

     It provides to ways of testing:
     
          1. direct api tests using fastapis testclient
               run : docker compose -f docker-compose-test.yml up
               run: python main_test.py from root directory

          2. run load using locust:
               run : docker compose -f docker-compose.yml up
               run: locust -f locustfile.py --host=http://localhost:8000 --web-port=<desired port>

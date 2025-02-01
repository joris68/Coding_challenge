import logging
from pydantic import BaseModel
import tiktoken
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from internal.GrammarManager import GrammarManager
from typing import Union


app = FastAPI(title="Grammarcheck API", version="1.0.0")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GrammarRequest(BaseModel):
     text : str


class GrammarError(BaseModel):
     error_type : str
     original_sentence : str
     corrected_sentence : str

class GrammarCheck(BaseModel):
     classification_id : str


class Classification_Result(BaseModel):
     status : str
     classification_id : str
     classification_result : list[GrammarError]


class Classification_State(BaseModel):
     status : str

ClassificationResponse = Union[Classification_Result, Classification_State]



# singleton classes
DB_CLIENT = None
LLM_CLIENT = None

# Maximum number of token this backend handles
TOKEN_UPPER_LIMIT = 500
# minimum number of token this backend handles
TOKEN_LOWER_LIMIT = 60

#tokenizer for gpt-4o (which I am using)
TOKENIZER = tiktoken.get_encoding("o200k_base")
# length of ID generated for the classification
ID_LENGTH = 10

grammar_manager = GrammarManager(ID_LENGTH)

def process_classification(original_text : str, classifiation_id : str):
     grammar_manager.insert_pending(original_text=original_text, classification_id=classifiation_id)
     grammar_manager.handle_grammar_check_request(original_text=original_text, classification_id=classifiation_id)



@app.post("/api/grammarcheck", response_model=GrammarCheck)
def check_grammar(req : GrammarRequest, background_task : BackgroundTasks):
     req_id = grammar_manager.generate_request_id()
     logging.info(f"starting Grammarcheck id : {req_id}")
     num_tokens = TOKENIZER.encode(req.text)
     
     # user has send to many text
     if len(num_tokens) > TOKEN_UPPER_LIMIT:
          logging.error(f"got request with {len(num_tokens)} tokens")
          return JSONResponse(
               content={
                    "message": f"Text is too large. The upper limit is 400 tokens. Provided text lenght {len(num_tokens)}"
               },
               status_code=400
          )

     # user has send roughly any text
     if len(num_tokens) < TOKEN_LOWER_LIMIT:
          logging.error(f"got request with {len(num_tokens)} tokens")
          return JSONResponse(
               content={
                    "message": f"Text is too small. Please provide a longer input. Provided text lenght {len(num_tokens)}"
               },
               status_code=400
          )
     
     background_task.add_task(process_classification, req.text, req_id)
     # proceeding with the grammar check
     return JSONResponse(
          content= {
               "classification_id" : req_id
          },
          status_code=200
     )


@app.get("/api/result", response_model = ClassificationResponse)
def get_result(classification_id : str):
     try:
          res = grammar_manager.db_client.get_doc_classification_status(classification_id=classification_id)
          if isinstance(res, dict):
               # could successfully got the dodument
               res.pop("_id")
               return JSONResponse(
                    content = res,
                    status_code = 200
               )
          
          if isinstance(res, str):
               return JSONResponse(
                    content = {
                         "status" : res
                    },
                    status_code = 200
               )
               
     except Exception as e:
          logger.error(f"Error when retrieving classification status with id : {classification_id} : {str(e)} ")
          return JSONResponse(
               content={
                    "status": f"We are sorry for the inconvenience"
               },
               status_code=500
          )



@app.get("/api/health")
def healthy():
     logger.info("returned the health check")
     return {"healthy"}


"""
     Evaluates the Confusion matrix for the given sample size.
     Note: This might take a while, as a lot of request are being evaluated.
"""

def process_evaluation(eval_id):
     grammar_manager.insert_pending_eval(eval_id=eval_id)
     grammar_manager.handle_eval_request(eval_id=eval_id)



@app.get("/api/eval")
def get_evaluation(background_task : BackgroundTasks):
     eval_id = grammar_manager.generate_request_id()
     background_task.add_task(process_evaluation, eval_id)
     return JSONResponse(
          content= {
               "eval_id" : eval_id
          },
          status_code = 200
     )

@app.get("/api/eval/result")
def get_eval_result(eval_id : str):
     try:
          res = grammar_manager.db_client.get_doc_eval_status(eval_id=eval_id)
          if isinstance(res, dict):
               # could successfully got the dodument
               # this is not JSON serializable
               res.pop("_id")
               return JSONResponse(
                    content = res,
                    status_code = 200
               )
          
          if isinstance(res, str):
               return JSONResponse(
                    content = {
                         "status" : res
                    },
                    status_code = 200
               )
               
     except Exception as e:
          logger.error(f"Error when retrieving classification status with id : {eval_id} : {str(e)} ")
          return JSONResponse(
               content={
                    "status": f"We are sorry for the inconvenience"
               },
               status_code=500
          )

    





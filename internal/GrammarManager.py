

from internal.LLM_Client import LLM_Client, example_classification
import numpy as np
from internal.DB_Client import DBClient
import logging
from internal.LLM_Client import ErrorType
from sklearn.metrics import precision_score



"""

     This class exposes the internals to the main.py file. It has a reference on the LLM_Client and the DB_client.
     It is not implemented as a singleton class. However, there will be only one instance instantiated in the main.py file.

"""


logger = logging.getLogger(__name__)

# the two collections names for MONGODB
CLASSIFICATION_RESULTS = "classification_results"
EVALUATION_RESULTS = "evaluation_results"

# mapping the error integers for validation
ERROR_MAPPING= {
  "Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)": 1,
  "Errors that affect the readability or logical structure of a sentence (e.g., misplaced modifiers, passive voice, incomplete comparisons)": 2,
  "Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)": 3,
  "Errors in punctuation and formatting (e.g., commas, semicolons, apostrophes, punctuation in parentheses)": 4,
  "Errors in punctuation and formatting (e.g., commas, semicolons, apostrophes, punctuation in parentheses)": 5,
  "Typo in sentence": 6,
  "Other Mistake": 7,
  "Entirely correct sentence": 8
}


class GrammarManager:

     def __init__(self, id_lenght : int):
          self.id_length = id_lenght
          self.llm_client = LLM_Client()
          self.db_client = DBClient()

     def generate_request_id(self) -> str:
          random_id = np.random.randint(0, 10, self.id_length)
          random_id_str = ''.join(map(str, random_id))
          return random_id_str

     def insert_pending_eval(self, eval_id : str):
          eval_dict = {
               "eval_id" : eval_id,
               "status" : "pending"
          }

          success = self.db_client.insert_document_eval(eval_dict=eval_dict)
          if success:
               logger.info(f"Experiment with id : {eval_id} now PENDING")
          else:
               logger.error(f"experiement with id : {eval_id} change status")
     
     def delete_pending_eval(self, eval_id : str):
          success = self.db_client.delete_document_eval(eval_id=eval_id)
          if success:
               logger.info(f"PENDING state delted for ID : {eval_id} in evaluation")
          else:
               logger.error(f"Could not delete document PENDING state for id : {eval_id} in evaluation")
     
     def handle_eval_request(self, eval_id : str) -> None:
          # sample documents
          sample_docs = self.db_client.sample_eval_documents()
          # put thorugh the model
          evaluated_doc = self.llm_client.eval_sample(sampled_doc=sample_docs)
          self.delete_pending_eval(eval_id=eval_id)
          if evaluated_doc is None:
               failed_eval_dict = {
                    "eval_id" : eval_id,
                    "status" : "failed"
               }
               success = self.db_client.insert_document_eval(eval_dict=failed_eval_dict)
               if success:
                    logger.info(f"updated status pending to status failed for eval : {eval_id}")
               else:
                    logger.error(f"could not update status pending to status failed for eval : {eval_id}")
               return 

          micro_precison = self._get_classification_metrics(evaluated_doc)
          success_eval_dict = {
               "eval_id" : eval_id,
               "status" : "successful",
               "micro_precison" : micro_precison,
               "llm_evaluation" : evaluated_doc
          }
     
          success = self.db_client.insert_document_eval(eval_dict=success_eval_dict)
          if success:
               logger.info(f"successfully updated the status from pending to successful for eval: {eval_id}")
          else:
               logger.error(f"could not update the status from pending to successful for eval : {eval_id}")


     def _get_classification_metrics(self , doc : list[dict]) -> float:

          predicted = []
          validated = []
          try:
               eval_list = doc["eval_result"]
               for x in eval_list:
                    predicted.append(ERROR_MAPPING[x["error_type"]])
                    validated.append(ERROR_MAPPING[x["error_type_validation"]])
               
               logger.info(predicted)
               logger.info(validated)
               
               precision = precision_score(validated, predicted, average='micro', zero_division=0)
               return precision
          except Exception as e:
               logger.error(f"error when computing multiclass precision {str(e)}")
               return -1.0


     def insert_pending(self, original_text : str, classification_id: str):
          classification_dict = {
               "classification_id" : classification_id,
               "original_text" : original_text,
               "status" : "pending"
          }
          success = self.db_client.insert_document_classification(classification_result=classification_dict)
          if success:
               logger.info(f"Experiment with id : {classification_id} now PENDING")
          else:
               logger.error(f"experiement with id : {classification_id} change status")
     
     def delete_pending(self,classification_id: str ):
          success = self.db_client.delete_document_classification(classification_id=classification_id)
          if success:
               logger.info(f"PENDING state delted for ID : {classification_id}")
          else:
               logger.error(f"Could not delete document PENDING state for id : {classification_id}")


     def handle_grammar_check_request(self, original_text : str, classification_id : str) -> None:
          
          request_dict = {
               "classification_id" : classification_id,
               "original_text" : original_text
          }

          res = self.llm_client.check_request(req=request_dict)

          response_db_doc = {}

          if res is None:
               # handles the aborted case
               response_db_doc["status"] = "aborted"
               response_db_doc["original_text"] = original_text
               response_db_doc["classification_id"] = classification_id
          else :
               # LLM request was successful
               response_db_doc["status"] = "successful"
               response_db_doc["original_text"] = res["original_text"]
               response_db_doc["classification_id"] = res["classification_id"]
               response_db_doc["classification_result"] = res["classification_result"]

          # to keep the DB in consistent state for the experiments we have to delete the document with PENDING state, that will be inserted directly when the
          # classification rerquest in created
          self.delete_pending(classification_id=classification_id)
          success = self.db_client.insert_document_classification(response_db_doc)
          if success:
               logging.info(f"Classification for Id : {classification_id} now status : {response_db_doc['status']}")
          else:
               logging.error(f"Could not store the document in DB for id : {classification_id}")

     
     """
     Gets the classification result when the client polls for the ID:

          possible states:
           - PENDING (doc found but status == aborted)
           - Sucessful ( could find document in the DB and status == successful)
           - ABORTED (doc found but status == aborted)

     """
     def get_classification_result(self, classification_id : str):
          return self.db_client.get_doc_classification_status(classification_id=classification_id)
     
     def get_eval_result(self, eval_id : str):
          return self.db_client.get_doc_eval_status(eval_id=eval_id)


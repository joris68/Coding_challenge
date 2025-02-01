
import os
from pymongo import MongoClient
import logging
import numpy as np



"""
     This class acts as a interface to the mongoDB instance we are running.
     It should ONLY be called by the GrammarManager class.

"""

logger = logging.getLogger(__name__)

DATABASE_NAME = 'grammar-db'


CLASSIFICATION_RESULTS = "classification_results"
EVALUATION_RESULTS = "evaluation_results"


class DBClient:

     def __init__(self):
          self.mongourl = os.getenv("MONGO_URI", "mongodb://localhost:27017/grammar-db")
          self.client = MongoClient(self.mongourl)
     

     def _get_collection(self, collection_name : str):
          db = self.client[DATABASE_NAME]
          return db[collection_name]
     
     def insert_document_eval(self , eval_dict : dict) -> bool:

          try:
               collection = self._get_collection(EVALUATION_RESULTS)
               collection.insert_one(eval_dict)
               logger.info(f"inserted new Document in collection {EVALUATION_RESULTS}")
               return True
          except Exception as e:
               logger.error(f"Error incurred inserting the document in the eval col. : {str(e)}")
               return False
     
     def delete_document_eval(self, eval_id : str) -> bool:
          try:
               class_res = self._get_collection(EVALUATION_RESULTS)
               number_docs_with_id = class_res.count_documents({"eval_id" : eval_id})
               if number_docs_with_id != 1:
                    logger.error("DB is in incosistent state")
               
               # we are going to delete many here
               delte_result = class_res.delete_many({"eval_id" : eval_id})

               assert delte_result.deleted_count == number_docs_with_id

               logger.info(f"deleted {delte_result.deleted_count} docs for eval col.")
               return True
          
          except Exception as e:
               logger.error(f"An error occured when trying to delete doc with id : {eval_id}")
               return False

     def insert_document_classification(self, classification_result : dict) -> bool:
          try:
               collection = self._get_collection(CLASSIFICATION_RESULTS)
               collection.insert_one(classification_result)
               logger.info(f"inserted new Document in collection {CLASSIFICATION_RESULTS}")
               return True
          except Exception as e:
               logger.error(f"Error incurred inserting the document: {str(e)}")
               return False
     
     def delete_document_classification(self, classification_id : str) -> bool:
          try:
               class_res = self._get_collection(CLASSIFICATION_RESULTS)
               number_docs_with_id = class_res.count_documents({"classification_id" : classification_id})
               if number_docs_with_id != 1:
                    logger.error("DB is in incosistent state")
               
               # we are going to delete many here
               delte_result = class_res.delete_many({"classification_id" : classification_id})

               # 
               assert delte_result.deleted_count == number_docs_with_id
               logger.info(f"deleted {delte_result.deleted_count} docs")
               return True
          
          except Exception as e:
               logger.error(f"An error occured when trying to delete doc with id : {classification_id}")
               return False


     
     """
          Should return the status of the classification or the result
     """
     def get_doc_classification_status(self, classification_id : str) -> dict | str:
          try:
               logger.info(f"trying to access results document for ID : {classification_id}")
               class_res = self._get_collection(CLASSIFICATION_RESULTS)
               res = class_res.find_one({"classification_id" : classification_id})

               if res is None:
                    # this happens when no documents are found
                    return "NOT FOUND"
               
               status = res.get("status")
               return res if status == "successful" else status
          except Exception as e:
               logger.error(f"Error querying for the document with id {classification_id} : {str(e)}")
     
     """
          To have an ongoing endpoint for eval metrics
     """

     def sample_eval_documents(self) -> dict:

          logger.info(f"start sampling for evaluation ")
          try:
               class_res = self._get_collection(CLASSIFICATION_RESULTS)
               
               documents = list(class_res.find({}))
               if documents:
                    return np.random.choice(documents)

               return None     
               
          except Exception as e:
               logger.error(f"error when sampling documents")
     
     def get_doc_eval_status(self, eval_id: str)-> dict | str:
          try:
               logger.info(f"trying to access results document for ID : {eval_id}")
               class_res = self._get_collection(EVALUATION_RESULTS)
               res = class_res.find_one({"eval_id" : eval_id})

               if res is None:
                    # this happens when no documents are found
                    return "NOT FOUND"
               logger.info(res)
               status = res.get("status")
               logger.info(status)
               return res if status == "successful" else status
          except Exception as e:
               logger.error(f"Error querying for the document with id {eval_id} : {str(e)}")

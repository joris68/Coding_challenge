
from openai import OpenAI
from pydantic import BaseModel
from enum import Enum
import openai
import json
import logging




"""
     This class all interactions between the our backend and openAI Api.
     We will use structured outputs.
"""


logger = logging.getLogger(__name__)

"""
     Based on the grammatical errors by grammerly : https://www.grammarly.com/blog/grammar/grammatical-errors/
"""

class ErrorType(Enum):
    word_choice_confusable_words = 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)'
    sentence_structure_and_clarity = 'Errors that affect the readability or logical structure of a sentence (e.g., misplaced modifiers, passive voice, incomplete comparisons)'
    agreement_and_consistency = 'Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)'
    punctuation_and_mechanics = 'Errors in punctuation and formatting (e.g., commas, semicolons, apostrophes, punctuation in parentheses)'
    usage_and_style = 'Errors in punctuation and formatting (e.g., commas, semicolons, apostrophes, punctuation in parentheses)'
    Typo = 'Typo in sentence'
    Other_mistake = 'other Mistake'
    CORRECT = 'Entirely correct sentence'

class SentenceClassification(BaseModel):
     sentence : str
     error_type : ErrorType
     corrected_sentence : str


class GrammarCheck(BaseModel):
     text : str
     result : list[SentenceClassification]


class GrammarEvalauation(BaseModel):
     sentence : str
     error_type : ErrorType
     corrected_sentence : str
     error_type_validation : str

class GrammerEvaluationList(BaseModel):
     validation : list[GrammarEvalauation]



grammarcheck_prompt = '''
          You will be provided with english text. Classify EACH sentence in the text in the following categories:
               1. Word Choice and  Confusable Words
               2. Sentence Structure and Clarity
               3. Agreement and Consistency
               4. Punctuation and Mechanics
               5. Usage and Style
               6. The Sentence includes a typo
               7. The Sentence has another mistake which does into the other categories
               8. The Sentence is entirely correct
          
               Omit sentences which are not entirely finished in your classification.
          
               Correct the sentences at the end and give it back.
          '''


eval_prompt = '''
          You will be given a list of triplets:
          
         1.  the original sentence
         2. the type of error given the original sentence
         3. the corrected sentence

         Please Evaluate for each triplet if the type of error matches the type of error given.
         Put you validation (in terms of error type) in the forth field.

         4. your validation (error type)

         This should resemble like a second opinion on the error.
'''


example_classification = {
    "status": "successful",
    "original_text": "Last weekend, I went to the beach with my freinds to enjoy the sun. The weather was perfect, but we forgot to bring sunscreen, wich was a big mistake. As a result, we all got sunburns and had to go back home earlyer than expected. Even though it wasn’t the best day, we still had fun and made some nice memories. I thik next time we weill be more careful and plan ahead. But thats part of the adventure right? I am just glad we were able to laugh about it at the end.",
    "classification_id": "8344424212",
    "classification_result": [
        {
            "sentence": "Last weekend, I went to the beach with my freinds to enjoy the sun.",
            "error_type": "Typo in sentence",
            "corrected_sentence": "Last weekend, I went to the beach with my friends to enjoy the sun."
        },
        {
            "sentence": "The weather was perfect, but we forgot to bring sunscreen, wich was a big mistake.",
            "error_type": "Typo in sentence",
            "corrected_sentence": "The weather was perfect, but we forgot to bring sunscreen, which was a big mistake."
        },
        {
            "sentence": "As a result, we all got sunburns and had to go back home earlyer than expected.",
            "error_type": "Typo in sentence",
            "corrected_sentence": "As a result, we all got sunburns and had to go back home earlier than expected."
        },
        {
            "sentence": "I thik next time we weill be more careful and plan ahead.",
            "error_type": "Typo in sentence",
            "corrected_sentence": "I think next time we will be more careful and plan ahead."
        },
        {
            "sentence": "But thats part of the adventure right?",
            "error_type": "Typo in sentence",
            "corrected_sentence": "But that's part of the adventure, right?"
        }
    ]
}

example_evaluation = {
    'eval_id': '2723108297',
    'status': 'successful',
    'micro_precison': 0.3333333333333333,
    'llm_evaluation': {
      'classification_id': '6764185649',
      'eval_result': [
        {
          'sentence': 'Yesterday, I seen a movie with my brother.',
          'error_type': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)',
          'corrected_sentence': 'Yesterday, I saw a movie with my brother.',
          'error_type_validation': 'Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)'
        },
        {
          'sentence': 'The plot was confusing, and I did not knew what happened at the end.',
          'error_type': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)',
          'corrected_sentence': 'The plot was confusing, and I did not know what happened at the end.',
          'error_type_validation': 'Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)'
        },
        {
          'sentence': 'The main character was different then I expected, and the actors performance wasnot great.',
          'error_type': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)',
          'corrected_sentence': "The main character was different than I expected, and the actor's performance was not great.",
          'error_type_validation': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)'
        },
        {
          'sentence': 'After the movie, we go to a restaurant, but the menu didn’t had much options.',
          'error_type': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)',
          'corrected_sentence': 'After the movie, we went to a restaurant, but the menu didn’t have many options.',
          'error_type_validation': 'Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)'
        },
        {
          'sentence': 'The waiter was rude, he didnot even listen us properly and bring the wrong drinks.',
          'error_type': 'Errors that affect the readability or logical structure of a sentence (e.g., misplaced modifiers, passive voice, incomplete comparisons)',
          'corrected_sentence': 'The waiter was rude; he did not even listen to us properly and brought the wrong drinks.',
          'error_type_validation': 'Errors that affect the readability or logical structure of a sentence (e.g., misplaced modifiers, passive voice, incomplete comparisons)'
        },
        {
          'sentence': 'We should have went somewhere else, but we was too hungry to find another place.',
          'error_type': 'Mistakes involving similar-sounding or commonly confused words (e.g., your vs. you are, affect vs. effect, compliment vs. complement)',
          'corrected_sentence': 'We should have gone somewhere else, but we were too hungry to find another place.',
         'error_type_validation': 'Mistakes related to matching grammatical elements (e.g., subject-verb agreement, me vs. I, each and every)'
        }
      ]
    }
  }


class LLM_Client:

     def __init__(self):
          self.openai_client= OpenAI(
               api_key=""
               )
     
     def check_request(self, req : dict) -> dict:
          try:
               completion = self.openai_client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    store=True,
                    messages=[
                         {"role": "system", "content": grammarcheck_prompt},
                         {"role" : "user", "content" : req["original_text"]}
                    ],
                    response_format=GrammarCheck
               )

               message = completion.choices[0].message

               # check if the LLM has refused the structured output:
               # 93 % benchmark (at least they say...) https://openai.com/index/introducing-structured-outputs-in-the-api/
               if message.refusal :
                    logger.error(f"Prompt with ID {req['classification_id']} has refused")
                    return None

               if message.parsed.result:

                    json_result = self.parse_python_to_json(message.parsed.result)

                    if json_result is None:
                         return None

                    classification_result = {
                         "classification_id" : req['classification_id'],
                         "original_text" : req["original_text"],
                         "classification_result" : json_result
                    }

                    return classification_result
               else:
                    return None
               
          except Exception as e:
               logger.error(f"An error occured : {str(e)} when analyzing request with iD : {req["id"]}")
               return None
     
     # parses python objects to json string objects
     def parse_python_to_json(self, result : list[SentenceClassification]) -> list[dict]:
          try:
               return [{"sentence": sc.sentence, "error_type": sc.error_type.value, "corrected_sentence" : sc.corrected_sentence} for sc in result]
          
          except Exception as e:
               logger.error(f"Error parsing the request pydantic objects to json")
               return None
     
     def _extract_sentence_classification(self, doc : dict) -> dict:
          if doc["classification_result"]:
               return doc["classification_result"]
          else:
               logger.error("could not  find the results in the sample dict")
               return None
     
     def parse_python_to_json_eval(self, evaluation_result : GrammerEvaluationList) -> list[dict]:
          try:
               return [{"sentence": sc.sentence, "error_type": sc.error_type.value, "corrected_sentence" : sc.corrected_sentence, "error_type_validation":  sc.error_type_validation} for sc in evaluation_result]
          except Exception as e:
               logger.error(f"Error parsing the request pydantic objects to json")
               return None
     

     
     def eval_sample(self, sampled_doc : dict) -> dict:

               logger.info(f"reevaluating the  sample doc")
               try:

                    classification_result = self._extract_sentence_classification(sampled_doc)

                    if classification_result is None:
                         logger.error(f"could not process the  sampled doc")
                         return None

                    completion = self.openai_client.beta.chat.completions.parse(
                         model="gpt-4o-mini",
                         store=True,
                         messages=[
                              {"role": "system", "content": eval_prompt},
                              {"role" : "user", "content" : json.dumps(classification_result)}
                         ],
                         response_format=GrammerEvaluationList
                    )

                    message = completion.choices[0].message
                    if message.refusal :
                         logger.error(f"the sampled doc got refused by LLM api")
                         return None


                    if message.parsed.validation:

                         #print(message.parsed.validation)

                         json_result = self.parse_python_to_json_eval(message.parsed.validation)
                         #print(json_result)

                         if json_result is None:
                              return None

                         eval_result = {
                              "classification_id" : sampled_doc['classification_id'],
                              "eval_result" : json_result
                         }

                         return eval_result

               
               except Exception as e:
                    logger.error(f"An error occured : {str(e)} when evaluating the doc")
          



if __name__=="__main__":

     s = '''A dog wagging its tail is a clear sign of happiness and excitement. Pets bring joy, companionship,
     and unconditional love into our lives. They are always there to cheer us up, 
     whether we have had a good or bad day. Taking care of them requires love, patience, and responsibility, 
     as they depend on us for their well-being. A happy pet makes for a happy home, filled with warmth and affection. 
     In return, they offer loyalty and a bond that lasts a lifetime.'''

     my_dict = {
          "classification_id" : "kfokdhid",
          "original_text" : s
     }

     client = LLM_Client()
     #print(client.check_request(my_dict))
     res = client.eval_sample([example_classification])
     print(res)





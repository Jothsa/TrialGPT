import os
from openai import OpenAI
from TrialGPT.api.get_api_key import get_api_key

def generate_client():
  gpt_api_key = get_api_key()
  client = OpenAI(
    api_key=gpt_api_key,
  )
  return client
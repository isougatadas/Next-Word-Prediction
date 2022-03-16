import os
import streamlit as st
import torch
import string
from transformers import BertTokenizer, BertForMaskedLM
from transformers import logging
logging.set_verbosity_error()

st.set_page_config(page_title='Next Word Prediction Model', page_icon=None, layout='centered', initial_sidebar_state='auto')

@st.cache()
def load_model(model_name):
  try:
    if model_name.lower() == "bert":
      bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
      bert_model = BertForMaskedLM.from_pretrained('bert-base-uncased').eval()
      return bert_tokenizer,bert_model
  except Exception as e:
    pass

def decode(tokenizer, pred_idx, top_clean):
  ignore_tokens = string.punctuation + '[PAD]'
  tokens = []
  for w in pred_idx:
    token = ''.join(tokenizer.decode(w).split())
    if token not in ignore_tokens:
      tokens.append(token.replace('##', ''))
  return '\n'.join(tokens[:top_clean])

def encode(tokenizer, text_sentence, add_special_tokens=True):
  text_sentence = text_sentence.replace('<mask>', tokenizer.mask_token)
  if tokenizer.mask_token == text_sentence.split()[-1]:
    text_sentence += ' .'

    input_ids = torch.tensor([tokenizer.encode(text_sentence, add_special_tokens=add_special_tokens)])
    mask_idx = torch.where(input_ids == tokenizer.mask_token_id)[1].tolist()[0]
  return input_ids, mask_idx

def get_all_predictions(text_sentence, top_clean=5):
  input_ids, mask_idx = encode(bert_tokenizer, text_sentence)
  with torch.no_grad():
    predict = bert_model(input_ids)[0]
  bert = decode(bert_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
  return {'bert': bert}

def get_prediction_eos(input_text):
  try:
    input_text += ' <mask>'
    res = get_all_predictions(input_text, top_clean=int(top_k))
    return res
  except Exception as error:
    pass

try:

  st.markdown("<h1 style='text-align: center;'>Next Word Prediction</h1>", unsafe_allow_html=True)
  st.sidebar.text("Next Word Prediction")
  top_k = st.sidebar.slider("How many predictions do you need?", 1 , 25, 1) 
  print(top_k)
  model_name = st.sidebar.selectbox(label='Below is the model that will be applied',  options=['BERT'], index=0,  key = "model_name")

  bert_tokenizer, bert_model  = load_model(model_name) 
  input_text = st.text_area("Enter your text here", placeholder="press 'Ctrl+Enter' to get the prediction...")

  res = get_prediction_eos(input_text)

  answer = []
  print(res['bert'].split("\n"))
  for i in res['bert'].split("\n"):
  	answer.append(i)
  answer_as_string = "    ".join(answer)
  st.text_area("Predicted List is Here",answer_as_string,key="predicted_list") 

except Exception as e:
  print("SOME PROBLEM OCCURED")  

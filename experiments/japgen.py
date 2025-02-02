!pip install transformers datasets accelerate bitsandbytes sentencepiece --upgrade fsspec

import torch
from transformers import GPTNeoXJapaneseForCausalLM, GPTNeoXJapaneseTokenizer
from huggingface_hub import login

try:
    from google.colab import userdata
    HF_TOKEN = userdata.get('HF_TOKEN')
    login(token=HF_TOKEN)
    print("Login successful")
except ImportError:
    print("Not running on Google Colab. Skipping Hugging Face login.")
except KeyError:
    print("HF_TOKEN secret not found. Have you set it in Colab?")
except Exception as e:
    print(f"An error occurred during Hugging Face login: {e}")

from transformers import GPTNeoXJapaneseForCausalLM, GPTNeoXJapaneseTokenizer

model = GPTNeoXJapaneseForCausalLM.from_pretrained("abeja/gpt-neox-japanese-2.7b")
tokenizer = GPTNeoXJapaneseTokenizer.from_pretrained("abeja/gpt-neox-japanese-2.7b")

prompt = "人とAIが協調するためには、"

input_ids = tokenizer(prompt, return_tensors="pt").input_ids

gen_tokens = model.generate(
     input_ids,
     do_sample=True,
     temperature=0.9,
     max_length=100,
)
gen_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)[0]

print(gen_text)
import gdown
import os
import torch
from torchtext.data.utils import get_tokenizer
import pickle

if not os.path.exists("model.pt"):
  file_id = "1QbcnHy7tCotS00VYUHBO1lZL0jT1g-1K"
  url = f'https://drive.google.com/uc?id={file_id}'
  output = 'model.pt'  
  gdown.download(url, output, quiet=False)

if not os.path.exists("vocab.pkl"):
  file_id = "1QxM3U94Ak2uLAamUkA9q-zQxORyPVyK7"
  url = f'https://drive.google.com/uc?id={file_id}'
  output = 'vocab.pkl' 
  gdown.download(url, output, quiet=False)

  if not os.path.exists("formatted_data.csv"):
    file_id = "1xkIkUJWn_p-K_Lza9dqFWWe2QOb0mlqE"
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'formatted_data.csv' 
    gdown.download(url, output, quiet=False)


with open('vocab.pkl', 'rb') as f:

    vocab = pickle.load(f) # deserialize using load()

tokenizer = get_tokenizer("basic_english")
text_pipeline = lambda x: vocab(tokenizer(x))

attack_name_labels = {1: "SQLInjection", 2: "XSS", 3: "CommandInjection", 4: "Normal"}
def predict(text, text_pipeline, model):
    with torch.no_grad():
        text = torch.tensor(text_pipeline(text))
        output = model(text, torch.tensor([0]))
        return output.argmax(1).item() + 1
model222 = torch.jit.load('model.pt')
model222.eval()
#print(f"pred: {attack_name_labels[predict('hello my man what is up my dude', text_pipeline, model222)]}")


sql_str = "As the sun dipped below the horizon, casting a warm orange glow across the sky, \
    Sarah sat by the window, lost in thought. The day had been a whirlwind of activity, from hectic meetings \
    at work to catching up with friends over coffee. Now, in the quiet of her apartment, she finally had a\
    moment to herself. Outside, the city buzzed with life, but inside, all was calm. With a sigh, Sarah leaned back\
    in her chair and closed her eyes, letting the soothing melody of her favorite song fill the room. In that \
    moment, she felt grateful for the simple pleasures in life – the warmth of the sun on her skin, the laughter \
    of loved ones, and the promise of a new day ahead."


print(f"pred: {attack_name_labels[predict(sql_str, text_pipeline, model222)]}")
import torch
from torchtext.data.utils import get_tokenizer
import pickle
import os
import gdown

class Prediction:
    def __init__(self, prediction, passed): # Should probably be using getters and setters here but this is easier
        self.predicted_safe = passed 
        self.predicted_label = prediction

class CleaningML:

    def __init__(self):
        # IDK if this stuff is bad practice for python classes and should be within a 'load_model' class function.
        with open('vocab.pkl', 'rb') as f:
            vocab = pickle.load(f) # deserialize using load()

        tokenizer = get_tokenizer("basic_english")
        self.text_pipeline = lambda x: vocab(tokenizer(x))

        self.attack_name_labels = {1: "SQLInjection", 2: "XSS", 3: "CommandInjection", 4: "Normal"}
        
        self.model = torch.jit.load('model.pt')
        self.model.eval()

    def predict(self, text):
            with torch.no_grad():
                text = torch.tensor(self.text_pipeline(text))
                output = self.model(text, torch.tensor([0]))
                prediction = self.attack_name_labels[output.argmax(1).item() + 1]
                passed = False if prediction in ["SQLInjection", "XSS", "CommandInjection"] else True
                return Prediction(prediction, passed)


if __name__ == '__main__':

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


    injection_str = "As I strolled through the park, enjoying the crisp autumn air, I couldn't help but notice the vibrant colors \
        of the leaves as they danced in the gentle breeze. Suddenly, my phone buzzed with a notification from an unknown sender. Curious, \
        I opened the message, only to find a strange string of characters: {{ get_user_file('/etc/passwd') }}. Perplexed, I brushed it off \
        as a glitch and continued on my way, but little did I know, it was a cleverly disguised attempt at a code injection attack, aimed at \
        exploiting vulnerabilities in my device's operating system. Fortunately, my device's robust security measures were able to detect \
        and block the malicious code before any harm could be done."

    xss_str = "what is <script>alert('XSS attack!')</script> this has malicious intent."

    sql_str = "As I walked through the bustling streets of the city,\
        I couldn't help but marvel at the vibrant atmosphere. The aroma\
        of freshly baked bread wafted from the nearby bakery, mingling \
        with the sounds of laughter  SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' and chatter. I decided to stop for\
        a quick coffee at the quaint cafe on the corner. As I \
        sipped my espresso, I couldn't shake the feeling that something was amiss. \
        Little did I know, a hacker was attempting to breach the cafe's outdated \
        security system with a malicious SQL injection attack, trying to gain access to sensitive customer data.\
        Unbeknownst to them, the cafe had recently upgraded its defenses, thwarting their nefarious plans."

    normal_str = "As the sun dipped below the horizon, casting a warm orange glow across the sky, \
        Sarah sat by the window, lost in thought. The day had been a whirlwind of activity, from hectic meetings \
        at work to catching up with friends over coffee. Now, in the quiet of her apartment, she finally had a\
        moment to herself. Outside, the city buzzed with life, but inside, all was calm. With a sigh, Sarah leaned back\
        in her chair and closed her eyes, letting the soothing melody of her favorite song fill the room. In that \
        moment, she felt grateful for the simple pleasures in life – the warmth of the sun on her skin, the laughter \
        of loved ones, and the promise of a new day ahead."

    ml_model = CleaningML()

    print(f"actual: {'SQLInjection':<25}pred: {ml_model.predict(sql_str).predicted_label}")
    print(f"actual: {'Normal':<25}pred: {ml_model.predict(normal_str).predicted_label}")
    print(f"actual: {'XSS':<25}pred: {ml_model.predict(xss_str).predicted_label}")
    print(f"actual: {'CommandInjection':<25}pred: {ml_model.predict(injection_str).predicted_label}")

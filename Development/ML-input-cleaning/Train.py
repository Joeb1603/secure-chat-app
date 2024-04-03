import torch
import pandas as pd
import os
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from torch import nn
import time
from torch.utils.data.dataset import random_split
from torchtext.data.functional import to_map_style_dataset
import gdown
import pickle

# Making sure CUDA is happy and running on the intended device
print(torch.cuda.is_available())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: '{'GPU' if device == 'cuda' else 'CPU'}' in use")

x = torch.rand(3, 3).to(device)
print("Tensor is on:", x.device)

attack_name_labels = {1: "SQLInjection", 2: "XSS", 3: "CommandInjection", 4: "Normal"}

# downloads below dataset if it doesn't exist in folder
# https://www.kaggle.com/datasets/alextrinity/sqli-xss-dataset
if not os.path.exists("SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv"):
    file_id = "1xOAp6LHZWhDYSfkymgqJPBG0FgV3dw7d"
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv'
    gdown.download(url, output, quiet=False)

# formats the data if this has never been done
if not os.path.exists("formatted_data.csv"):
    df = pd.read_csv("SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv")
    new_rows = []

    # there is probably a faster and better way of doing this.
    # it turns 4 label columns into 1
    for index, row in df.iterrows():
        label = 0
        if row["SQLInjection"] == 1.0:
            label = 1
        if row["XSS"] == 1.0:
            label = 2
        elif row["CommandInjection"] == 1.0:
            label = 3
        elif row["Normal"] == 1.0:
            label = 4
        new_rows.append({"Sentence": row["Sentence"], "Label": label})

    df = pd.DataFrame(new_rows)

    df.to_csv("formatted_data.csv", index=False)

else:
    df = pd.read_csv("formatted_data.csv")

# splits into train test and val sets
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
valid_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

# resets indexes to be safe, not sure if this is neccasary
train_df.reset_index(drop=True, inplace=True)
valid_df.reset_index(drop=True, inplace=True)
test_df.reset_index(drop=True, inplace=True)

# I'll comment the rest later, most of it is from the pytorch docs for text processing
# (adding comments will never happen)

tokenizer = get_tokenizer("basic_english") # American spelling :(
train_iter = iter(zip( train_df["Label"], train_df["Sentence"]))
def yield_tokens(data_iter):
    for _, text in data_iter:
        yield tokenizer(text)

vocab = build_vocab_from_iterator(yield_tokens(train_iter), specials=["<unk>"])
vocab.set_default_index(vocab["<unk>"])

text_pipeline = lambda x: vocab(tokenizer(x))
label_pipeline = lambda x: int(x) - 1

def collate_batch(batch):
    label_list, text_list, offsets = [], [], [0]
    for _label, _text in batch:
        label_list.append(label_pipeline(_label))
        processed_text = torch.tensor(text_pipeline(_text), dtype=torch.int64)
        text_list.append(processed_text)
        offsets.append(processed_text.size(0))
    label_list = torch.tensor(label_list, dtype=torch.int64)
    offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
    text_list = torch.cat(text_list)
    return label_list.to(device), text_list.to(device), offsets.to(device)

train_iter = iter(zip( train_df["Label"], train_df["Sentence"]))
dataloader = DataLoader(
    train_iter, batch_size=8, shuffle=False, collate_fn=collate_batch
)

class TextClassificationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_class):
        super(TextClassificationModel, self).__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=False)
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)

iter(zip( train_df["Label"], train_df["Sentence"]))
num_class = len(set([label for (label, text) in train_iter]))
vocab_size = len(vocab)
emsize = 64
model = TextClassificationModel(vocab_size, emsize, num_class).to(device)

def train(dataloader):
    model.train()
    total_acc, total_count = 0, 0
    log_interval = 500
    start_time = time.time()

    for idx, (label, text, offsets) in enumerate(dataloader):
        optimizer.zero_grad()
        predicted_label = model(text, offsets)
        loss = criterion(predicted_label, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.1)
        optimizer.step()
        total_acc += (predicted_label.argmax(1) == label).sum().item()
        total_count += label.size(0)
        if idx % log_interval == 0 and idx > 0:
            elapsed = time.time() - start_time
            print(
                "| epoch {:3d} | {:5d}/{:5d} batches "
                "| accuracy {:8.3f}".format(
                    epoch, idx, len(dataloader), total_acc / total_count
                )
            )
            total_acc, total_count = 0, 0
            start_time = time.time()

def evaluate(dataloader):
    model.eval()
    total_acc, total_count = 0, 0

    with torch.no_grad():
        for idx, (label, text, offsets) in enumerate(dataloader):
            predicted_label = model(text, offsets)
            loss = criterion(predicted_label, label)
            total_acc += (predicted_label.argmax(1) == label).sum().item()
            total_count += label.size(0)
    return total_acc / total_count

# Hyperparameters
EPOCHS = 10  # epoch
LR = 5  # learning rate
BATCH_SIZE = 64
# batch size for training

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.1)
total_accu = None
train_iter = iter(zip( train_df["Label"], train_df["Sentence"]))
test_iter = iter(zip( test_df["Label"], test_df["Sentence"]))
valid_iter = iter(zip( valid_df["Label"], valid_df["Sentence"]))
train_dataset = to_map_style_dataset(train_iter)
test_dataset = to_map_style_dataset(test_iter)
valid_dataset = to_map_style_dataset(valid_iter)

train_dataloader = DataLoader(
    train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch
)
valid_dataloader = DataLoader(
   valid_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch
)
test_dataloader = DataLoader(
    test_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch
)

for epoch in range(1, EPOCHS + 1):
    epoch_start_time = time.time()
    train(train_dataloader)
    accu_val = evaluate(valid_dataloader)
    if total_accu is not None and total_accu > accu_val:
        scheduler.step()
    else:
        total_accu = accu_val
    print("-" * 59)
    print(
        "| end of epoch {:3d} | time: {:5.2f}s | "
        "valid accuracy {:8.3f} ".format(
            epoch, time.time() - epoch_start_time, accu_val
        )
    )
    print("-" * 59)

print("Checking the results of test dataset.")
accu_test = evaluate(test_dataloader)
print("test accuracy {:8.3f}".format(accu_test))

# Inference on some examples
def predict(text, text_pipeline, model=model):
    with torch.no_grad():
        text = torch.tensor(text_pipeline(text))
        output = model(text, torch.tensor([0]))
        return output.argmax(1).item() + 1


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

model = model.to("cpu")

print(f"actual: {'SQLInjection':<25}pred: {attack_name_labels[predict(sql_str, text_pipeline)]}")
print(f"actual: {'Normal':<25}pred: {attack_name_labels[predict(normal_str, text_pipeline)]}")
print(f"actual: {'XSS':<25}pred: {attack_name_labels[predict(xss_str, text_pipeline)]}")
print(f"actual: {'CommandInjection':<25}pred: {attack_name_labels[predict(injection_str, text_pipeline)]}")

model_to_save = torch.jit.script(model)
model_to_save.save('model.pt')  # Save
with open('vocab.pkl', 'wb') as f:  # open a text file
    pickle.dump(vocab, f)
import random
import datetime
from cryptography.fernet import Fernet
import importlib
import Database
importlib.reload(Database)

#TODO: remove duplicates anf make sure they are all good
adjectives = list(set(['happy', 'silly', 'clever', 'funny', 'smart', 'kind', 'brave', 'friendly', 'calm', 'shy',
              'curious', 'gentle', 'eager', 'honest', 'loyal', 'polite', 'generous', 'energetic', 'playful',
              'sincere', 'creative', 'cheerful', 'helpful', 'graceful', 'witty', 'determined', 'thoughtful',
              'optimistic', 'charming', 'modest', 'confident', 'mysterious', 'fierce', 'resourceful', 'patient',
              'adventurous', 'carefree', 'independent', 'radiant', 'sensitive', 'grateful', 'prudent', 'innocent',
              'persistent', 'genuine', 'sympathetic', 'dynamic', 'insightful', 'cooperative', 'harmonious',
              'adaptable', 'resilient', 'tolerant', 'enthusiastic', 'peaceful', 'loyal', 'glamorous', 'sophisticated',
              'tenacious', 'gregarious', 'tenacious', 'vibrant', 'versatile', 'exuberant', 'capable', 'frank',
              'sociable', 'diplomatic', 'spontaneous', 'astute', 'intrepid', 'intuitive', 'pragmatic', 'quirky',
              'enterprising', 'zestful', 'versatile', 'candid', 'dynamic', 'cosmopolitan', 'mellow', 'exuberant',
              'affable', 'discerning', 'nurturing', 'gregarious', 'elegant', 'adventurous', 'gregarious', 'radiant',
              'introspective', 'vivacious', 'gracious', 'boisterous', 'gregarious', 'brilliant', 'gregarious', 'vivacious',
              'silly', 'clever', 'funny', 'smart', 'kind', 'brave', 'friendly', 'calm', 'shy', 'curious',
              'gentle', 'eager', 'honest', 'loyal', 'polite', 'generous', 'energetic', 'playful', 'sincere',
              'creative', 'cheerful', 'helpful', 'graceful', 'witty', 'determined', 'thoughtful', 'optimistic',
              'charming', 'modest', 'confident', 'mysterious', 'fierce', 'resourceful', 'patient', 'adventurous',
              'carefree', 'independent', 'radiant', 'sensitive', 'grateful', 'prudent', 'innocent', 'persistent',
              'genuine', 'sympathetic', 'dynamic', 'insightful', 'cooperative', 'harmonious', 'adaptable',
              'resilient', 'tolerant', 'enthusiastic', 'peaceful', 'loyal', 'glamorous', 'sophisticated', 'tenacious',
              'gregarious', 'vibrant', 'versatile', 'exuberant', 'capable', 'frank', 'sociable', 'diplomatic',
              'spontaneous', 'astute', 'intrepid', 'intuitive', 'pragmatic', 'quirky', 'enterprising', 'zestful',
              'versatile', 'candid', 'dynamic', 'cosmopolitan', 'mellow', 'exuberant', 'affable', 'discerning',
              'nurturing', 'gregarious', 'elegant', 'adventurous', 'gregarious', 'radiant', 'introspective',
              'vivacious', 'gracious', 'boisterous', 'gregarious', 'brilliant', 'gregarious', 'vivacious',
              'impulsive', 'imaginative', 'humble', 'ambitious', 'bold', 'delightful', 'majestic', 'mysterious',
              'melodious']))

nouns = list(set(['cat', 'dog', 'bird', 'rabbit', 'turtle', 'elephant', 'lion', 'monkey', 'fish', 'penguin',
         'bear', 'tiger', 'deer', 'dolphin', 'zebra', 'giraffe', 'kangaroo', 'koala', 'hippo', 'rhino',
         'cheetah', 'fox', 'wolf', 'owl', 'eagle', 'hawk', 'sparrow', 'swan', 'peacock', 'parrot',
         'hamster', 'guinea pig', 'rat', 'mouse', 'squirrel', 'chipmunk', 'gerbil', 'hamster', 'ferret',
         'rabbit', 'frog', 'toad', 'newt', 'lizard', 'gecko', 'snake', 'turtle', 'tortoise', 'crocodile',
         'alligator', 'iguana', 'chameleon', 'salamander', 'axolotl', 'dinosaur', 'shark', 'whale', 'dolphin',
         'jellyfish', 'octopus', 'squid', 'lobster', 'crab', 'shrimp', 'clam', 'oyster', 'snail',
         'slug', 'butterfly', 'moth', 'bee', 'wasp', 'ant', 'dragonfly', 'grasshopper', 'cricket',
         'beetle', 'ladybug', 'caterpillar', 'centipede', 'millipede', 'spider', 'scorpion', 'tick',
         'flea', 'mosquito', 'fly', 'bee', 'wasp', 'ant', 'dragonfly', 'grasshopper', 'cricket',
         'beetle', 'ladybug', 'caterpillar', 'centipede', 'millipede', 'spider', 'scorpion', 'tick',
         'flea', 'mosquito', 'fly','apple', 'banana', 'orange', 'pear', 'strawberry', 'blueberry', 'raspberry', 'grape', 'pineapple', 'watermelon',
         'kiwi', 'mango', 'peach', 'plum', 'apricot', 'cherry', 'lemon', 'lime', 'coconut', 'avocado',
         'pomegranate', 'fig', 'date', 'papaya', 'melon', 'dragonfruit', 'guava', 'passionfruit', 'lychee', 'cantaloupe',
         'blackberry', 'cranberry', 'elderberry', 'boysenberry', 'tangerine', 'apricot', 'persimmon', 'honeydew', 'nectarine', 'gooseberry',
         'grapefruit', 'kumquat', 'quince', 'rutabaga', 'turnip', 'potato', 'carrot', 'beet', 'radish', 'celery',
         'cabbage', 'lettuce', 'spinach', 'kale', 'arugula', 'broccoli', 'cauliflower', 'asparagus',
         'cucumber', 'zucchini', 'eggplant', 'jalapeno', 'habanero', 'pumpkin', 'squash',
          'yam', 'corn', 'peas', 
         'chickpeas', 'lentils', 'soybeans', 
         'barley', 'oats', 'rice', 'quinoa', 'bulgur', 'millet', 'amaranth', 'buckwheat', 'wheat', 'rye']))


def generate_username(): 
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return adjective.capitalize() + noun.capitalize()

def add_user():
    new_username = generate_username()
    if not Database.get_user(new_username) and not Database.invite_exists(new_username): #TODO: error handling 
        
        invite_id_key = "jQZ-Ijedw017l5T_UR_KmOToGYVwEKhln3udhsm39Zw=" # This could be more secure #Fernet.generate_key()
        cipher_suite = Fernet(invite_id_key)

        current_time = datetime.datetime.now()
        invite_id = f"{new_username}[split]{current_time.strftime('%Y%m%d%H%M%S')}"
        encrypted_invite_id = cipher_suite.encrypt(invite_id.encode()).decode('utf-8')
        
        Database.write_invite(new_username, encrypted_invite_id) 
                                                       
        #print(f"https://team20.joe-bainbridge.com/register/{encrypted_invite_id}")
        print(f"http://127.0.0.1:5000/register/{encrypted_invite_id}")

    else:
        print("error handling")
        add_user() #TODO: this is bad, could lead to an infinite loop

add_user()




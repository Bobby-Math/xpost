import requests  
import tweepy   
import apikeys   
import json
import re
import time
import argparse

def parse_arguments():
    
    parser = argparse.ArgumentParser(description="Script Parser")
    parser.add_argument("x", type = str, nargs='?', default='default_value', help = " A String")
    return parser.parse_args()

def send_to_telegram(message):
    
    global tg
    tg=0    
    apiURL = f'https://api.telegram.org/bot{apikeys.apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': apikeys.chatID, 'text': message})
        data = response.json()
        if(data['ok'] == True ):
            print("\nPosted to Telegram successfully")
            tg = 1
        else:
            print("\nNot posted in Telegram: FAILED")
    except Exception as e:
       print(e)

def create_tweet(message:str, reply_id = None, image_path = None):
    if image_path:
        response = client.create_tweet(message, media_id = image_path, in_reply_to_tweet_id = reply_id)
    else:
      response = client.create_tweet(text = message, in_reply_to_tweet_id = reply_id)

    print("Tweeting........") 
    return response

def divide_paragraph(paragraph):

    # Replacing ." with ". 
    # Dot should be placed outside of quotes.
    paragraph = re.sub(r'\."\s*', '". ', paragraph)

    # Step 1: Replace one or two digits followed by a dot and space
    paragraph = re.sub(r'\b(\d{1,2}\. )', lambda m: m.group().replace('. ', '__DOT__'), paragraph)

    # Step 2: Replace one, two, or three English alphabets followed by a dot
    paragraph = re.sub(r'\b([A-Za-z]{1,3}\. )', lambda m: m.group().replace('. ', '__DOT__'), paragraph)

    # Step 3: Split the paragraph on dot followed by space
    sentences = re.split(r'(?<=\.)\s', paragraph)

    # Step 4: Restore the dot and space in the relevant cases
    sentences = [sentence.replace('__DOT__', '. ') for sentence in sentences]

    # IN the paragraph, sentences are split when you encounter a dot followed by a space.
    # but abbreviations like a one,two,three digit words followed by a dot
    # one or two digits followed by a dot.

    #Combining sentences into paragraphs in tweet length.
    divided_paragraphs = []
    current_paragraph = []
    current_size = 0
    flag1=0

    # for checking if an English sentence is out of bound.
    for i in sentences:
        if (len(i)>277):
            print("\n\n Warning: Pay attention: ENGLISH Sentence is out of bound\n\n")
            print(i + "\n\nThe above sentence has length " + str(len(i)))
            print("\n\n")
            flag1+=1
    if(flag1!= 0):  
        print(str(flag1) + " Sentence(s) are out of bound. Exiting. Cut this english sentence short. ") 
        exit()

    for sentence in sentences:
        sentence = sentence.strip()  # Remove leading/trailing whitespace
        if sentence:
            sentence_size = len(sentence)
            if current_size + sentence_size + len(current_paragraph) <= 273:
                current_paragraph.append(sentence)
                current_size += sentence_size
            else:
                divided_paragraphs.append(current_paragraph)
                current_paragraph = [sentence]
                current_size = sentence_size

    if current_paragraph:
        divided_paragraphs.append(current_paragraph)

    formatted_paragraphs = []
    for i, paragraph in enumerate(divided_paragraphs):
        formatted_sentences = '\n\n\n'.join(paragraph)  # Use this for spacing between sentences.
        # formatted_sentences = ' '.join(paragraph) #Use this if you don't want spacing between sentences in the thread.
        formatted_paragraphs.append(formatted_sentences)

# Just in case you need to check the length of the final sentence in the final twitter paragraph.
#Final Checking if a tweet is within bounds

    cleaned_paragraphs = [] 
    for paragraph in formatted_paragraphs:
        cleaned_paragraph = re.sub(r'\n\n\n',' ', paragraph)
        # New line character will be counted only once in twitter.
        cleaned_paragraphs.append(cleaned_paragraph)

    flag = 0
    for i in cleaned_paragraphs:
        if (len(i)>280):
            print("\n\n Warning: Pay attention: Final **TWEET** is out of bound\n\n")
            print(i + "\n\nThe FINAL TWEET is out of " + str(len(i)))
            print("\n\n")
            flag+=1
    if(flag!= 0):  
        print(str(flag) + " Tweet(s) are out of bound. Exiting. Cut this TWEET short. ") 
        exit()
        
    return formatted_paragraphs

def create_thread(data, image_path = None, reply_id = None):
    
    global x
    x = 0
    tweets = divide_paragraph(data)
    print("\nNumber of tweets in this thread:" + str(len(tweets)))
    print("\nTweeting for " + apikeys.twitter_account_id + "\n")
    
    response = create_tweet(tweets[0], image_path)
    
    first_tweet_id = response.data['id']

    if(reply_id != None):
        print("in reply to:" + "https://twitter.com/" + apikeys.twitter_account_id + "/status/" + str(reply_id))
              
    thread_link = "https://twitter.com/" + apikeys.twitter_account_id + "/status/" + str(first_tweet_id)

    print("\nSending tweet[" + str(1) + "]")
    time.sleep(1)
    tweet_count = 1

    if(len(tweets)<=15):
        time_delay = 1
    else:
        time_delay = 2

    for t in tweets[1:]:
        tweet_id = response.data['id']
        tweet_count+=1
        print("Sending tweet[" + str(tweet_count) + "]")
        response = client.create_tweet(text = t, in_reply_to_tweet_id = tweet_id)
        time.sleep(time_delay)

    if tweet_count == len(tweets):
        print("\nAll tweets have been successfully posted.")
        x = 1
        print("\n" + thread_link + "\n")

def Authenticate_Client():

    client = tweepy.Client(consumer_key = apikeys.API_KEY, consumer_secret = apikeys.API_SECRET_KEY, access_token = apikeys.ACCESS_KEY, access_token_secret = apikeys.ACCESS_SECRET_KEY)

    return client

if __name__ == '__main__':
    
    args = parse_arguments()
    
    client = Authenticate_Client()

    fileobject = open("textfile.txt","r")
    data = fileobject.read()

    if(args.x != "x"):
        send_to_telegram(data)
    
    image_path = None
    reply_id = None
    
    create_thread(data, image_path, reply_id)

    if(x == 1) or (tg == 1):
        with open("textfile.txt", "w") as file:
            pass 
    
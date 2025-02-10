# Auto Twitter Replier

## Description
This Python script automatically replies to tweets from a specified list of Twitter users within a defined time window (between 1 and 24 hours old). It uses OpenAI's GPT model to generate context-aware, natural-sounding responses and interacts with the Twitter API to fetch tweets, generate replies, and post them back. This tool is ideal for automating engagement and growing interactions on Twitter while ensuring responses blend seamlessly with existing conversations.

## Features
- **Automated Twitter Replies**: Generates and posts AI-driven responses.
- **Time-Based Filtering**: Only replies to tweets that are at least 1 hour old but not older than 24 hours.
- **User-Specific Monitoring**: Replies only to tweets from pre-defined Twitter accounts.
- **Natural AI Responses**: Uses OpenAI's GPT model for realistic engagement.
- **Rate Limit Handling**: Includes delays to comply with Twitter API rate limits.

## Requirements
### 1. Twitter API Credentials
To use this script, you'll need to obtain Twitter API credentials.
#### Steps:
1. **Go to** [Twitter Developer Portal](https://developer.twitter.com/)
2. **Sign up** or log in, then apply for a Developer Account.
3. **Create a project** and an app.
4. Navigate to **Keys and Tokens** and generate the following:
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret
5. Replace the placeholders in `config.py`:
   ```python
   TWITTER_API_KEY = "your_api_key"
   TWITTER_API_SECRET = "your_api_secret"
   TWITTER_ACCESS_TOKEN = "your_access_token"
   TWITTER_ACCESS_SECRET = "your_access_secret"
   ```

### 2. OpenAI API Key
To generate replies, you need an OpenAI API key.
#### Steps:
1. **Go to** [OpenAI API](https://platform.openai.com/signup/) and sign up.
2. Navigate to **API Keys** and generate a new key.
3. Replace the placeholder in `config.py`:
   ```python
   OPENAI_API_KEY = "your_openai_key"
   ```

### 3. Configure Target Users
Specify the Twitter usernames to which the bot should reply:
```python
TARGET_USERS = ["user1", "user2", "user3"]  # Replace with actual usernames
```

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/auto-twitter-replier.git
   cd auto-twitter-replier
   ```
2. Install dependencies:
   ```sh
   pip install tweepy openai
   ```
3. Run the script:
   ```sh
   python bot.py
   ```

## Script Overview
### `bot.py`
```python
import tweepy
import openai
import time
from datetime import datetime, timedelta
from config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, OPENAI_API_KEY, TARGET_USERS

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)

openai.api_key = OPENAI_API_KEY

def fetch_tweets():
    one_hour_ago = datetime.utcnow() - timedelta(hours=24)
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=1)
    eligible_tweets = []
    
    for user in TARGET_USERS:
        tweets = api.user_timeline(screen_name=user, count=50, tweet_mode='extended')
        for tweet in tweets:
            tweet_time = tweet.created_at.replace(tzinfo=None)
            if twenty_four_hours_ago <= tweet_time <= one_hour_ago:
                eligible_tweets.append(tweet)
    
    return eligible_tweets

def fetch_replies(tweet_id, user):
    replies = []
    for tweet_reply in tweepy.Cursor(api.search_tweets, q=f'to:{user}', since_id=tweet_id, tweet_mode='extended').items(50):
        if tweet_reply.in_reply_to_status_id == tweet_id:
            replies.append(tweet_reply.full_text)
    return replies

def generate_reply(original_tweet, replies):
    prompt = f"""
    Original Tweet: {original_tweet}
    Existing Replies: {replies[:5]}
    Generate a reply that blends in naturally:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Twitter user replying in a natural and organic way."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def post_reply(tweet_id, reply_text):
    api.update_status(status=reply_text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
    print(f"Replied: {reply_text}")

if __name__ == "__main__":
    tweets = fetch_tweets()
    for tweet in tweets:
        replies = fetch_replies(tweet.id, tweet.user.screen_name)
        reply_text = generate_reply(tweet.full_text, replies)
        post_reply(tweet.id, reply_text)
        time.sleep(10)  # Avoid API rate limits
```

## Contribution
Feel free to fork, modify, and create pull requests!

## License
MIT License

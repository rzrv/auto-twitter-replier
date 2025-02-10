import tweepy
import openai
import time
from datetime import datetime, timedelta

# Twitter API credentials (replace with your keys)
TWITTER_API_KEY = "your_api_key"
TWITTER_API_SECRET = "your_api_secret"
TWITTER_ACCESS_TOKEN = "your_access_token"
TWITTER_ACCESS_SECRET = "your_access_secret"

# OpenAI API key (replace with your key)
OPENAI_API_KEY = "your_openai_key"

# List of Twitter users to monitor
TARGET_USERS = ["user1", "user2", "user3"]  # Replace with actual usernames

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)

# OpenAI API setup
openai.api_key = OPENAI_API_KEY

def fetch_tweets_from_users():
    """Fetch tweets from target users within the time range."""
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
    """Fetch replies to a specific tweet."""
    replies = []
    
    for tweet_reply in tweepy.Cursor(api.search_tweets, q=f'to:{user}', since_id=tweet_id, tweet_mode='extended').items(50):
        if tweet_reply.in_reply_to_status_id == tweet_id:
            replies.append(tweet_reply.full_text)
    
    return replies

def generate_reply(original_tweet, replies):
    """Generate a natural reply based on existing comments."""
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
    """Post the generated reply to Twitter."""
    api.update_status(status=reply_text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
    print(f"Replied: {reply_text}")

if __name__ == "__main__":
    tweets = fetch_tweets_from_users()
    for tweet in tweets:
        replies = fetch_replies(tweet.id, tweet.user.screen_name)
        reply_text = generate_reply(tweet.full_text, replies)
        post_reply(tweet.id, reply_text)
        time.sleep(10)  # Avoid API rate limits

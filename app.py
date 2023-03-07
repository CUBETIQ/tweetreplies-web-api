from flask import Flask, jsonify, make_response, request, Response
from config import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
import tweepy

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def str2bool(v):
    if not v:
        return False

    if isinstance(v, bool):
        return v

    return v.lower() in ("yes", "true", "t", "1")


def create_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        tweet_id = request.args.get('tweet_id') or request.form.get('tweet_id')
        dl = request.args.get('dl') or request.form.get('dl')
        dl = str2bool(dl)

        if tweet_id:
            # Get the replies to the tweet
            replies = tweepy.Cursor(
                api.search_tweets, q=f"to:{api.get_status(tweet_id).user.screen_name}", since_id=tweet_id, tweet_mode="extended").items()
            usernames = []
            author = api.get_status(tweet_id).user.screen_name

            for reply in replies:
                if reply.user.screen_name != author:
                    usernames.append(reply.user.screen_name)

            return make_response(jsonify({
                'tweet_id': tweet_id,
                'total_replies': len(usernames),
                'unique_replies': len(set(usernames)),
                'author': author,
                'replies': usernames,
            }), 200)

        return make_response(jsonify({
            'error': 'No tweet_id is provided',
            'params': {
                'tweet_id': '1632730569065787392',
                'lang': 'eng+khm',
            },
            "examples": [
                {
                    "uri": "/?tweet_id=1632730569065787392",
                }
            ]
        }), 400)

    return app

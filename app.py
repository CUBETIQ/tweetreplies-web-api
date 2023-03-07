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


def to_csv(usernames):
    csv = 'no, username'
    for i, username in enumerate(usernames):
        csv += f'{i}, {username}'

    return csv


def create_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        tweet_id = request.args.get('tweet_id') or request.form.get('tweet_id')
        export = request.args.get('export') or request.form.get('export')
        dl = request.args.get('dl') or request.form.get('dl')
        dl = str2bool(dl)
        mine_type = 'text/csv' if export == 'csv' else 'application/json'
        download_filename = f'export_{tweet_id}.csv' if export == 'csv' else f'export_{tweet_id}.json'
        content_disposition_type = 'attachment' if dl else 'inline'
        content_disposition = f"{content_disposition_type}; filename={download_filename}"

        if tweet_id:
            # Get the replies to the tweet
            replies = tweepy.Cursor(
                api.search_tweets, q=f"to:{api.get_status(tweet_id).user.screen_name}", since_id=tweet_id, tweet_mode="extended").items()
            usernames = []
            author = api.get_status(tweet_id).user.screen_name

            for reply in replies:
                if reply.user.screen_name != author:
                    usernames.append(reply.user.screen_name)

            uniqe_usernames = set(usernames)

            if export == 'csv':
                csv = to_csv(uniqe_usernames)
                return Response(
                    csv,
                    mimetype=mine_type,
                    headers={"Content-disposition": content_disposition}
                )

            if dl:
                return Response(
                    uniqe_usernames,
                    mimetype=mine_type,
                    headers={"Content-disposition": content_disposition}
                )

            return make_response(jsonify({
                'tweet_id': tweet_id,
                'total_replies': len(usernames),
                'unique_replies': len(uniqe_usernames),
                'author': author,
                'replies': usernames,
            }), 200)

        return make_response(jsonify({
            'error': 'No tweet_id is provided',
            'params': {
                'tweet_id': 'TWITTER_TWEET_ID',
                'dl': '0/1',
                'export': 'csv/json',
            },
            # 'body': {
            #     'TWEET_CONSUMER_KEY': 'stirng',
            # },
            "examples": [
                {
                    "uri": "/?tweet_id=1632730569065787392",
                },
                {
                    'uri': '/?tweet_id=1632730569065787392&export=csv',
                },
                {
                    'uri': '/?tweet_id=1632730569065787392&export=json',
                },
                {
                    'uri': '/?tweet_id=1632730569065787392&export=csv&dl=1',
                },
            ]
        }), 400)

    return app

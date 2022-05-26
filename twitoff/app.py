from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_or_update_user, vectorize_tweet
import os
from .predict import predict_user

def create_app():
    app = Flask(__name__)
    app_title= 'Luke\'s awesome (well kinda shitty but soon to be\
         awesome) twitoff app!'

    # database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)


    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route("/test")
    def test():
        return f"<p>This is a page for {app_title}</p>"

    @app.route("/reset")
    def reset():
        DB.drop_all()
        DB.create_all()
        return """The database has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate>Go to populate</a>
        """
    
    @app.route("/populate")
    def populate():
        user1 = User(id=1, username='luke')
        DB.session.add(user1)
        user2 = User(id=2, username='jake')
        DB.session.add(user2)
        tweet_text = 'hi'
        tweet_vector = vectorize_tweet(tweet_text)
        tweet = Tweet(id=1, text=tweet_text, vector=tweet_vector, user=user1)
        DB.session.add(tweet)
        tweet2_text = 'hey baby'
        tweet2_vector = vectorize_tweet(tweet2_text)
        tweet2 = Tweet(id=2, text=tweet2_text, vector=tweet2_vector, user=user2)
        # tweet3 = Tweet(id=3, text='Hola amigo', user=user1)
        # tweet4 = Tweet(id=4, text='Namaste', user=user2)
        # tweet5 = Tweet(id=5, text='E = MC Squared', user=user1)
        # tweet6 = Tweet(id=6, text='What\'s Crackin\'n homeskillet', user=user2)
        DB.session.add(tweet2)
        # DB.session.add(tweet3)
        # DB.session.add(tweet4)
        # DB.session.add(tweet5)
        # DB.session.add(tweet6)
        DB.session.commit()
        return '''The database has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate>Go to populate</a>
        '''

    @app.route('/update')
    def update():
        usernames = []
        for user in User.query.all():
            add_or_update_user(user.username)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        username = username or request.values['username']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User {username} successfully added.'

            tweets = User.query.filter(
                User.username == username
            ).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}'
            tweets = []

        return render_template(
            "user.html",
            title=username,
            message=message,
            tweets=tweets,
        )

    @app.route('/compare', methods=['POST'])
    def compare():
        username0 = request.values['user0']
        username1 = request.values['user1']

        if username0 == username1:
            message = 'Cannot compare users to themselves'
        else:
            hypo_tweet_text = request.values['tweet_text']
            prediction = predict_user(username0, username1, hypo_tweet_text)
            if prediction:
                selected_user = username1
            else:
                selected_user = username0
            message = f"'{hypo_tweet_text}' is more likely written by {selected_user}"

        return render_template('prediction.html', title='Prediction', message=message)

    return app

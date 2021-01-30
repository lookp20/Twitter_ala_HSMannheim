from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/follower")
def follower():
    return render_template("follower.html")
@app.route("/tweets")
def tweets():
    return render_template("tweets.html")
@app.route("/tweetsSend")
def tweetsSend():
    return render_template("tweetsSend.html")
if __name__ == "__main__":
    app.run(debug=True)
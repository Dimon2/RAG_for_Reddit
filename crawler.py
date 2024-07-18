
import praw
from dotenv import load_dotenv
from praw.models import MoreComments
import os


def traverse_replies(replies, ret = None):

    if ret is None:
        ret = []

    for reply in replies:
        ret.append(reply.body)
        if len(reply.replies) > 0: 
            traverse_replies(reply.replies, ret)
        
    return ret

class Crawler():
    def __init__(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"), 
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"), 
            user_agent="crawler")
        
    def load(self, with_replies = False):
        combined_subreddits = self.reddit.subreddit("stocks+investing+stockmarket+wallstreetbets")
        for submission in combined_subreddits.top(time_filter="week"):
            metadata = { 
                "subreddit": submission.subreddit.display_name,
                "title": submission.title,
                "score": submission.score
            }
            entry = {
                "metadata": metadata,
                "text": submission.selftext,
                "comments": []
            }
            
            submission.comments.replace_more(limit=24, threshold=1)

            for top_level_comment in submission.comments:

                if isinstance(top_level_comment, MoreComments): continue

                comment = {"text": top_level_comment.body }
                if with_replies:
                    replies = traverse_replies(top_level_comment.replies)        
                    comment["replies"] = replies                
                entry["comments"].append(comment)

            yield entry


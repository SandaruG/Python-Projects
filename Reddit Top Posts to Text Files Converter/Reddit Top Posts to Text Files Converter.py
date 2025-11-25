import praw
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reddit API credentials
reddit = praw.Reddit(
    client_id='id',
    client_secret='secret',
    user_agent='agent'
)

# Directory to save text files
output_dir = r"Folder"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    logger.info(f"Created directory: {output_dir}")

# Function to sanitize file names
def sanitize_filename(title):
    # Remove invalid characters for Windows file names
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', title)
    # Replace spaces with underscores and limit length
    sanitized = sanitized.replace(' ', '_')[:200]
    # Ensure the filename is not empty
    return sanitized if sanitized else "unnamed_post"

# Function to save a post to a text file
def save_post_to_file(post):
    try:
        title = post.title
        selftext = post.selftext if post.selftext else "No selftext available."
        filename = sanitize_filename(title) + ".txt"
        filepath = os.path.join(output_dir, filename)
        
        # Combine title and selftext
        content = f"Title: {title}\n\n{selftext}"
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved post: {filename}")
    except Exception as e:
        logger.error(f"Error saving post '{title}': {str(e)}")

# Fetch top posts from r/AmItheAsshole
subreddit = reddit.subreddit('AmItheAsshole')
try:
    # Get top posts of all time (limit=None to get as many as possible)
    top_posts = subreddit.top(time_filter='all', limit=None)
    
    # Process each post
    for post in top_posts:
        save_post_to_file(post)
        
    logger.info("Finished fetching and saving posts.")
except Exception as e:
    logger.error(f"Error fetching posts: {str(e)}")
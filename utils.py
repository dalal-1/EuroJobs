import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from models import Notification, db

def save_picture(form_picture, folder):
    """Save a picture to the filesystem and return the filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', folder, picture_fn)
    
    # Save the file
    form_picture.save(picture_path)
    
    return os.path.join(folder, picture_fn)

def save_cv(form_cv):
    """Save a CV file to the filesystem and return the filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_cv.filename)
    cv_fn = random_hex + f_ext
    cv_path = os.path.join(current_app.root_path, 'static', 'uploads', 'cvs', cv_fn)
    
    # Save the file
    form_cv.save(cv_path)
    
    return f'cvs/{cv_fn}'

def create_notification(user, message, link=None):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user.id,
        message=message,
        link=link,
        timestamp=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_unread_notifications_count(user):
    """Get the count of unread notifications for a user"""
    from models import Notification
    return Notification.query.filter_by(user_id=user.id, read=False).count()

def get_unread_messages_count(user):
    """Get the count of unread messages for a user"""
    from models import Message
    return Message.query.filter_by(recipient_id=user.id, read=False).count()

def format_datetime(dt):
    """Format a datetime object to a readable string"""
    now = datetime.utcnow()
    delta = now - dt
    
    if delta.days == 0:
        if delta.seconds < 60:
            return "Just now"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            hours = delta.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif delta.days == 1:
        return "Yesterday"
    elif delta.days < 7:
        return f"{delta.days} {'day' if delta.days == 1 else 'days'} ago"
    else:
        return dt.strftime("%b %d, %Y")

def get_user_by_username_or_email(username_or_email):
    """Get a user by username or email"""
    from models import User
    user = User.query.filter_by(username=username_or_email).first()
    if not user:
        user = User.query.filter_by(email=username_or_email).first()
    return user

def get_or_create_conversation(user1_id, user2_id):
    """Get an existing conversation or create a new one between two users"""
    from models import Conversation
    
    # Check if conversation exists (in either direction)
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
        ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
    ).first()
    
    if not conversation:
        # Create new conversation
        conversation = Conversation(user1_id=user1_id, user2_id=user2_id)
        db.session.add(conversation)
        db.session.commit()
    
    return conversation

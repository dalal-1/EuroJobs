from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Message, User, Student, Company, Conversation
from forms import MessageForm
from datetime import datetime
from utils import get_or_create_conversation, create_notification

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def inbox():
    # Get all conversations involving the current user
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | 
        (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()
    
    # Get latest message for each conversation
    conversation_data = []
    for conv in conversations:
        other_user_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
        other_user = User.query.get(other_user_id)
        
        # Get the student or company info to display name
        display_name = other_user.username
        if Student.query.filter_by(user_id=other_user_id).first():
            student = Student.query.filter_by(user_id=other_user_id).first()
            if student.first_name and student.last_name:
                display_name = f"{student.first_name} {student.last_name}"
            profile_pic = student.profile_picture
        else:
            company = Company.query.filter_by(user_id=other_user_id).first()
            if company and company.name:
                display_name = company.name
            profile_pic = company.logo if company else None
        
        # Get latest message
        latest_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()
        
        # Count unread messages
        unread_count = Message.query.filter_by(
            sender_id=other_user_id, 
            recipient_id=current_user.id, 
            read=False
        ).count()
        
        conversation_data.append({
            'conversation_id': conv.id,
            'other_user_id': other_user_id,
            'display_name': display_name,
            'profile_pic': profile_pic,
            'latest_message': latest_message,
            'unread_count': unread_count
        })
    
    return render_template('messages/inbox.html', conversations=conversation_data)

@messages_bp.route('/conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    
    # Get or create conversation
    conversation = get_or_create_conversation(current_user.id, user_id)
    
    # Get display name and profile pic
    if Student.query.filter_by(user_id=user_id).first():
        student = Student.query.filter_by(user_id=user_id).first()
        if student.first_name and student.last_name:
            display_name = f"{student.first_name} {student.last_name}"
        else:
            display_name = other_user.username
        profile_pic = student.profile_picture
    else:
        company = Company.query.filter_by(user_id=user_id).first()
        display_name = company.name if company and company.name else other_user.username
        profile_pic = company.logo if company else None
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user_id, 
        recipient_id=current_user.id, 
        read=False
    ).all()
    
    for message in unread_messages:
        message.read = True
    
    if unread_messages:
        db.session.commit()
    
    # Get messages between the two users
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()
    
    # Form for sending a new message
    form = MessageForm()
    form.recipient_id.data = user_id
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            body=form.body.data,
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create notification for recipient
        notify_message = f"New message from "
        if current_user.id == conversation.user1_id:
            if Student.query.filter_by(user_id=current_user.id).first():
                student = Student.query.filter_by(user_id=current_user.id).first()
                notify_message += f"{student.first_name} {student.last_name}"
            else:
                company = Company.query.filter_by(user_id=current_user.id).first()
                notify_message += company.name
        else:
            if Student.query.filter_by(user_id=current_user.id).first():
                student = Student.query.filter_by(user_id=current_user.id).first()
                notify_message += f"{student.first_name} {student.last_name}"
            else:
                company = Company.query.filter_by(user_id=current_user.id).first()
                notify_message += company.name
                
        create_notification(
            other_user, 
            notify_message,
            url_for('messages.conversation', user_id=current_user.id)
        )
        
        return redirect(url_for('messages.conversation', user_id=user_id))
    
    return render_template('messages/conversation.html', 
                          other_user=other_user,
                          display_name=display_name,
                          profile_pic=profile_pic,
                          messages=messages,
                          form=form)

@messages_bp.route('/new/<int:user_id>')
@login_required
def new_conversation(user_id):
    # Check if user exists
    user = User.query.get_or_404(user_id)
    
    # Redirect to conversation
    return redirect(url_for('messages.conversation', user_id=user_id))

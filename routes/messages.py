from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Message, User, Student, Company, Conversation
from forms import MessageForm
from datetime import datetime, timedelta
from utils import get_or_create_conversation, create_notification

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def inbox():
    from app import db

    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | 
        (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()

    conversation_data = []
    for conv in conversations:
        other_user_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
        other_user = User.query.get(other_user_id)

        display_name = other_user.username
        profile_pic = None

        student = Student.query.filter_by(user_id=other_user_id).first()
        company = Company.query.filter_by(user_id=other_user_id).first()

        if student and student.first_name and student.last_name:
            display_name = f"{student.first_name} {student.last_name}"
            profile_pic = student.profile_picture
        elif company:
            display_name = company.name
            profile_pic = company.logo

        latest_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()

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

    return render_template(
        'messages/inbox.html',
        conversations=conversation_data,
        now=datetime.utcnow()
    )


@messages_bp.route('/conversation/<int:user_id>/details', methods=['GET'])
@login_required
def conversation_details(user_id):
    from app import db

    other_user = User.query.get_or_404(user_id)
    conversation = get_or_create_conversation(current_user.id, user_id)

    student = Student.query.filter_by(user_id=user_id).first()
    company = Company.query.filter_by(user_id=user_id).first()

    if student and student.first_name and student.last_name:
        display_name = f"{student.first_name} {student.last_name}"
        profile_pic = student.profile_picture
    elif company and company.name:
        display_name = company.name
        profile_pic = company.logo
    else:
        display_name = other_user.username
        profile_pic = None

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()

    return render_template(
        'messages/detail.html',
        other_user=other_user,
        display_name=display_name,
        profile_pic=profile_pic,
        messages=messages,
        now=datetime.utcnow()
    )


@messages_bp.route('/conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    from app import db

    other_user = User.query.get_or_404(user_id)
    conversation = get_or_create_conversation(current_user.id, user_id)

    student = Student.query.filter_by(user_id=user_id).first()
    company = Company.query.filter_by(user_id=user_id).first()

    if student and student.first_name and student.last_name:
        display_name = f"{student.first_name} {student.last_name}"
        profile_pic = student.profile_picture
    elif company and company.name:
        display_name = company.name
        profile_pic = company.logo
    else:
        display_name = other_user.username
        profile_pic = None

    unread_messages = Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        read=False
    ).all()
    for message in unread_messages:
        message.read = True

    if unread_messages:
        db.session.commit()

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()

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
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        # Créer une notification propre avec fallback
        sender_name = current_user.username
        student_sender = Student.query.filter_by(user_id=current_user.id).first()
        company_sender = Company.query.filter_by(user_id=current_user.id).first()
        if student_sender:
            sender_name = f"{student_sender.first_name} {student_sender.last_name}"
        elif company_sender:
            sender_name = company_sender.name

        create_notification(
            other_user,
            f"New message from {sender_name}",
            url_for('messages.conversation_details', user_id=current_user.id)
        )

        return redirect(url_for('messages.conversation', user_id=user_id))

    return render_template(
        'messages/conversation.html',
        other_user=other_user,
        display_name=display_name,
        profile_pic=profile_pic,
        messages=messages,
        form=form,
        now=datetime.utcnow(),
        timedelta=timedelta
    )

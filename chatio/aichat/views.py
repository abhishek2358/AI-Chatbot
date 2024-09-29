from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import chatSessions, chatMessages, patient
from .chatbot.botfunctions import handle_user_input
from .chatbot.conversation import conversation_history
import json
conversation_memory = []

def index(request):

    patient_record = patient.objects.create(patient_id=1, patient_name='Abhishek Goyal',
                                            patient_email="abhi2358@seas.upenn.edu", patient_phone='123456', patient_dob='1999-05-19', patient_summary='No summary yet', patient_last_appointment='2024-02-19', patient_next_appointment='2024-03-19', patient_treatment_plan='Aspirin', patient_doctor='Dr. Adam Smith')
                
    
    return HttpResponse("Hello, world. You're at the aichat index.")


def home(request):
    
    chatSessions_list = chatSessions.objects.all()

    # check if patient with record patient_id 1 exists, if not create one
    if not patient.objects.filter(patient_id=1).exists():
        patient_record = patient.objects.create(patient_id=1, patient_name='Abhishek Goyal',
                                            patient_email="abhi2348@seas.upenn.edu", patient_phone='123456', patient_dob='1999-05-19', patient_summary='No summary yet', patient_last_appointment='2024-02-19', patient_next_appointment='2024-03-19', patient_treatment_plan='Aspirin', patient_doctor='Dr. Adam Smith')
        
    # if patient record exists, fetch the record
    else:
        patient_record = patient.objects.get(patient_id=1)
    # Check if there are any sessions
    if chatSessions_list.exists():
        # Get the last session
        selected_session = chatSessions_list.last()
        # Fetch messages for the last session
        messages = chatMessages.objects.filter(session_id=selected_session).order_by('message_time')
    else:
        # If no session exists, create a new one
        selected_session = chatSessions.objects.create(session_name="New Chat Session")
        messages = None  # No messages for the new session yet

        # Redirect to the home view to avoid duplicate form submission and show the newly created session
        return redirect('home')

    # Pass the session and messages to the template
    return render(request, 'aichat/home.html', {
        'chatSessions_list': chatSessions_list,  # All sessions for the sidebar
        'selected_session': selected_session,  # Last session or new session
        'messages': messages,  # Messages for the selected session
        'summary': patient_record.patient_summary
    })

def chat_session(request, session_id):
    global conversation_memory
    # Get the chat session by session_id
    session = get_object_or_404(chatSessions, session_id=session_id)
    patient_summary = patient.objects.get(patient_id=1).patient_summary

    # Fetch messages for this session
    messages = chatMessages.objects.filter(session_id=session).order_by('message_time')

    if request.method == 'POST':
        # Get the message content from the POST request
        message_content = request.POST.get('message', '')

        # Create a new chat message
        new_message = chatMessages.objects.create(
            session_id=session,
            message=message_content,
            sender='user'  # Assuming the message is from the user
        )
        patient_record = patient.objects.get(patient_id=1)
        response = handle_user_input(message_content, patient_record.patient_summary,conversation_memory)
        response = json.loads(response)
        patient_response = response.get("patient_response", "I'm sorry, I couldn't process your request.")
        review_message = response.get("review_message", None)


        # If the session name is still the default or empty, update it with the first 15 characters of the first message
        if session.session_name == "New Chat Session" or session.session_name == "":
            # Truncate the message to the first 15 characters
            truncated_message = message_content[:15]
            if len(message_content) > 15:
                truncated_message += "..."
            session.session_name = truncated_message
            session.save()  # Save the updated session name

        # Append the user input and bot response to the conversation memory
        conversation_memory = conversation_history(conversation_memory, message_content, patient_response,patient_record.patient_summary)

        bot_message = chatMessages.objects.create(
            session_id=session,
            message=patient_response,
            sender='bot'
        )

         #create json response with bot_message2 if review_message is not None
        if review_message!="":
            bot_message2 = chatMessages.objects.create(
                session_id=session,
                message=review_message,
                sender='bot'
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': {
                        'message': new_message.message,
                        'sender': new_message.sender,
                        'message_time': new_message.message_time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'bot_message': {
                        'message': bot_message.message,
                        'sender': bot_message.sender,
                        'message_time': bot_message.message_time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'bot_message2': {
                        'message': bot_message2.message,
                        'sender': bot_message2.sender,
                        'message_time': bot_message2.message_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
        
        else:
            # If the request is AJAX, return the user and bot messages in JSON format with timestamps
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': {
                        'message': new_message.message,
                        'sender': new_message.sender,
                        'message_time': new_message.message_time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'bot_message': {
                        'message': bot_message.message,
                        'sender': bot_message.sender,
                        'message_time': bot_message.message_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })


        # Redirect back to the same chat session after sending the message (for non-AJAX requests)
        return redirect('chat_session', session_id=session_id)

    return render(request, 'aichat/home.html', {
        'chatSessions_list': chatSessions.objects.all(),
        'messages': messages,
        'selected_session': session,
        'summary': patient_summary
    })


def create_chat_session(request):
    # Create a new chat session
    new_session = chatSessions.objects.create(session_name="New Chat Session")
    
    # Redirect to the chat session page of the newly created session
    return redirect('chat_session', session_id=new_session.session_id)

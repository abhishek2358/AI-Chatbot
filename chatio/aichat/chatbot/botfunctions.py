import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from aichat.chatbot.llm import get_llm
from aichat.models import patient

# Load the environment variables
# load_dotenv()
# api_key = os.getenv('GOOGLE_API_KEY')

# genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-pro")

model = get_llm()

if patient.objects.filter(patient_id=1).exists():
    patient_record = patient.objects.get(patient_id=1)

    doctor_name = patient_record.patient_doctor
    patient_name = patient_record.patient_name
    current_time = patient_record.patient_next_appointment

    #format current_time to only show date
    current_time = current_time.strftime("%Y-%m-%d")

    #Combine all patient information into a single string
    patient_info = f"Patient name is {patient_name}. The next appointment is scheduled for {current_time} with Dr. {doctor_name}. The patient's treatment plan includes {patient_record.patient_treatment_plan}. Patient contact details: Email: {patient_record.patient_email}, Phone: {patient_record.patient_phone}. Patient date of birth: {patient_record.patient_dob}."



def is_health_related(user_input):
    # Define the prompt for the LLM
    llm_prompt = f"""
    You are an AI assistant. Your task is to classify the following user input based on whether it falls under following topics or not. The specific topics include:
    1. General health and lifestyle inquiries.
    2. Questions about the user's medical condition, medication regimen, diet, etc.
    3. Requests from the patient to their doctor, such as medication changes.
    4. General greetings and pleasantries.
    5. Any non-medical inquiries related to the user's health.
    6. Any non-sensitive or non-controversial message.
    7. User appointment realted queries.
    8. User treatment related queries.

    If the input is sensitive, or controversial, it should be classified as Not health-related.
    
    Input: "{user_input}"
    
    Please respond with one of the following categories only:
    - Health-related
    - Not health-related
    - Appointment-related
    - Treatment-related
    """
    
    response = model.generate_content(llm_prompt)  
    # Extract the classification from the response
    classification = response.text.strip().lower()
    
    return classification



def handle_treatment_request(user_input):
    # Define the prompt for the LLM
    llm_prompt = f"""
    You are an AI assistant. Your task is to determine if the following user input is related to treatment requests, such as:
    
    1. **Medication Changes**: If the input requests to change, stop, or adjust medication (e.g., "Can we switch my medication to something else?"), respond with:
       "I will discuss your medication change request with Dr. {doctor_name}."
       Also, generate a message for internal review in the format:
       "Patient {patient_name} is requesting to change their medication."

    2. **Treatment Adjustments**: If the input requests to adjust or change the treatment plan (e.g., "Can we update my treatment plan?"), respond with:
       "I will review your treatment plan with Dr. {doctor_name}."
       Also, generate a message for internal review in the format:
       "Patient {patient_name} is requesting to adjust their treatment plan."

    3. **General Treatment Inquiries**: If the input asks about ongoing treatments (e.g., "How is my treatment progressing?"), respond with:
       "I will provide you with an update on your treatment status with Dr. {doctor_name}."
       No review message is needed for general inquiries.

    Use the following patient information for context:
    Patient Information: {patient_info}
    
    Input: "{user_input}"
    
    Provide your response in the following JSON format:
    {{
        "patient_response": "<response to patient>",
        "review_message": "<review message or null>"
    }}
    """

    response = model.generate_content(llm_prompt)

    # Parse the JSON response from the LLM
    response_data = response.text.strip()
    
    try:
        response_dict = json.loads(response_data)
        patient_response = response_dict.get("patient_response", "I'm sorry, I couldn't process your request.")
        review_message = response_dict.get("review_message", None)
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        patient_response = "I'm sorry, I couldn't process your request."
        review_message = None

    response_json = json.dumps({
        "patient_response": patient_response,
        "review_message": review_message
    })

    return response_json

def handle_appointment_request(user_input):
    # Define the prompt for the LLM to determine if the input is related to an appointment request
    llm_prompt = f"""
    You are an AI assistant. Your task is to determine if the following user input is a request to modify, cancel, or confirm an appointment. Based on the input, generate the following:
    
    1. **Response to Patient**: A response to the patient indicating the action that will be taken (e.g., "I will convey your request to {doctor_name}.").
    
    2. **Review Message**: A message for internal review if the input involves rescheduling or canceling an appointment. The review message should be in the following format:
       - For rescheduling: "Patient {patient_name} is requesting an appointment change from {current_time} to [requested time]." Undestand from the user input the requested time the appointment should be changed to.
       - For cancellation: "Patient {patient_name} is requesting to cancel their appointment scheduled for {current_time}."

    If the input does not involve rescheduling, canceling, or confirming an appointment, just provide a response to the patient and do not generate a review message.
    
    Input: "{user_input}"
    
    Provide your response in the following JSON format:
    {{
        "patient_response": "<response to patient>",
        "review_message": "<review message or null>"
    }}
    """

    response = model.generate_content(llm_prompt)

    response_data = response.text.strip()
    try:
        response_dict = json.loads(response_data)
        patient_response = response_dict.get("patient_response", "I'm sorry, I couldn't process your request.")
        review_message = response_dict.get("review_message", "")
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        patient_response = "I'm sorry, I couldn't process your request."
        review_message = None

    response_json = json.dumps({
        "patient_response": patient_response,
        "review_message": review_message
    })

    return response_json

def health_chatbot(user_input,summarized_memory,conversation_memory):

    # Define the prompt for the LLM

    context = summarized_memory + "\n" + "\n".join(conversation_memory)
    llm_prompt = f"""
    You are an AI assistant specialized in health-related conversations. Your task is to provide appropriate and helpful responses to user inquiries related to health, including but not limited to:
    
    1. **General health inquiries**: Questions about symptoms, general health advice, etc.
    2. **Lifestyle inquiries**: Advice on diet, exercise, sleep, stress management, etc.
    3. **Medical condition inquiries**: Information or advice on specific medical conditions, including symptoms, treatment options, etc.
    4. **Medication regimen**: Questions or requests related to taking, changing, or stopping medications.

    Following is the information about the patient:
    Patient Information: {patient_info}

    Ensure that your responses are clear, empathetic, and helpful. If the inquiry is sensitive or requires human intervention, gently suggest that the patient should consult with their healthcare provider.
    Take into account the context of the conversation to provide relevant responses.

    Context:"{context}"

    Continue the dialogue based on the above context.

    Input: "{user_input}"
    
    Provide your response directly as a text output.
    """

    response = model.generate_content(llm_prompt)

    response_data = response.text.strip()

    response_json = json.dumps({
        "patient_response": response_data,
        "review_message": ""
    })

    return response_json


# Function to handle user input
def handle_user_input(user_input,summarized_memory,conversation_memory):
    # Check if the input is health-related
    classification = is_health_related(user_input)
    
    if classification == "health-related":
        return health_chatbot(user_input,summarized_memory,conversation_memory)
    elif classification == "appointment-related":
        # Handle the appointment request
        return handle_appointment_request(user_input)
    elif classification == "treatment-related":
        # Handle the treatment request
        return handle_treatment_request(user_input)
    else:
        # Respond with an appropriate message if it's not health-related
        response_json = json.dumps({
        "patient_response": "I'm here to help you with health-related inquiries. Could you please ask a question related to your health or medical needs?",
        "review_message": ""
             })
        return response_json


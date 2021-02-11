from __future__ import print_function
import boto3
from botocore.exceptions import ClientError
import logging

s3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def my_logging_handler(event, context):
    logger.info('got event{}'.format(event))
    logger.error('something went wrong')
    return 'Hello World!'


def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # if (event['session']['application']['applicationId'] !=
    #        ""):
    #    raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return get_welcome_response()


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'] + " Intent=" + intent_request['intent']['name'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "Describe":
        return get_buckets_by_tag_value(intent, session)

    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Accediendo al servicio S3 de Amazon. Que tarea deseas que realice? " \
                    "Puedo describir tus buckets ."

    reprompt_text = "Por favor, dime si quieres que describa, inicie o detenga tus instancias."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_describe_attributes(instance_id):
    return {"InstanceId": instance_id}


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_buckets_by_tag_value(intent, session):
    card_title = intent['name']

    session_attributes = {}
    should_end_session = True

    reprompt_text = "Disculpa, no te he entendido." \
                    "Puedo decirte las instancias que tienes si me dices. " \
                    "Alexa, describe mis instancias."

    buckets = s3.list_buckets()

    count = 0
    bucket_names = []

    for bucket in buckets['Buckets']:
        bucket_names.append(bucket['Name'])
        count += 1

    if count == 1:
        speech_output = "Tienes un bucket. El nombre es " + str(bucket_names)
    elif count > 1:
        speech_output = "Tienes " + str(count) + " buckets. Los nombres son " + str(
            bucket_names)
    else:
        speech_output = "No tienes ningun bucket."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


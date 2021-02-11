from __future__ import print_function
import boto3
from botocore.exceptions import ClientError
import logging

ec2_details = boto3.resource('ec2')
ec2_control = boto3.client('ec2')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
def my_logging_handler(event, context):
	logger.info('got event{}'.format(event))
	logger.error('something went wrong')
	return 'Hello World!'


def lambda_handler(event, context):

	#print("event.session.application.applicationId=" +
	#      event['session']['application']['applicationId'])

	#if (event['session']['application']['applicationId'] !=
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

	#print("on_launch requestId=" + launch_request['requestId'] +
	#      ", sessionId=" + session['sessionId'])
	# Dispatch to your skill's launch
	return get_welcome_response()


def on_intent(intent_request, session):

	#print("on_intent requestId=" + intent_request['requestId'] +
	#      ", sessionId=" + session['sessionId'] + " Intent=" + intent_request['intent']['name'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	# Dispatch to your skill's intent handlers
	if intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "Describe":
		return get_instances_by_tag_value(intent, session)
	elif intent_name == "Start":
		return change_instances_state_by_tag_value(intent, session, "start")
	elif intent_name == "Stop":
		return change_instances_state_by_tag_value(intent, session, "stop")
	elif intent_name == "Reboot":
		return change_instances_state_by_tag_value(intent, session, "reboot")

	else:
		raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):

   print("on_session_ended requestId=" + session_ended_request['requestId'] +
         ", sessionId=" + session['sessionId'])


def get_welcome_response():

	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Accediendo al servicio EC2 de Amazon. Que tarea deseas que realice? " \
					"Puedo describir, iniciar o detener tus instancias ."

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


def get_instances_by_tag_value(intent, session):

	card_title = intent['name']

	session_attributes = {}
	should_end_session = False

	reprompt_text = "Disculpa, no te he entendido." \
				"Puedo decirte las instancias que tienes si me dices. " \
				"Alexa, describe mis instancias."

	instances = ec2_details.instances.all()

	count = 0
	instance_ids = []
	names = []
	instance_states = []

	for instance in instances:
		instance_ids.append(instance.id)
		if instance.state["Name"] == 'running':
			state_name = 'En ejecucion'
		elif instance.state["Name"] == 'stopped':
			state_name = 'Detenida'
		elif instance.state["Name"] == 'stopping':
			state_name = 'Deteniendose'
		elif instance.state["Name"] == 'rebooting':
			state_name = 'Reiniciando'
		elif instance.state["Name"] == 'pending':
			state_name = 'Pendiente'
		elif instance.state["Name"] == 'shutting-down':
			state_name = 'Apagandose'
		else:
			state_name = 'Terminada'

		instance_states.append(state_name)
		session_attrubutes = create_describe_attributes(instance.id)
		count += 1
		for tag in instance.tags:
			if tag['Value'] is "":
				name = instance.id
			else:
				name = tag['Value']

			names.append(name)

	if count is 1:
		speech_output = "Tienes una instancia. El nombre es " + str(name) + " e ID " + str(instance_ids) + ". La instancia esta " + str(instance_states) + " Deseas hacer algo mas? Puedo parar o iniciar todas las instancias."
	elif count > 1:
		speech_output = "Tienes " + str(count) + " instancias. Los nombres o IDs son " + str(names) + ". Las instancias estan " + str(instance_states) + " Deseas hacer algo mas? Puedo parar o iniciar todas las instancias."
	else:
		speech_output = "No tienes ninguna instancia."

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


def change_instances_state_by_tag_value(intent, session, state):

	card_title = intent['name']
	#tag = intent['Text']['value']

	session_attributes = {}
	should_end_session = True

	reprompt_text = "Disculpa, no te he entendido." \
				"Puedo iniciar o detener tus instancias. "

	instances = ec2_details.instances.all()
	
	names = []
	
	for instance in instances:
		for tag in instance.tags:
			if tag['Value'] is "":
				name = instance.id
			else:
				name = tag['Value']

			names.append(name)

			if state == "stop":
				ec2_control.stop_instances(InstanceIds=[instance.id], DryRun=False)
				speech_output = "La instancia o instancias con nombre o IDs " + str(names) + " se estan deteniendo."
			elif state == "reboot":
				ec2_control.reboot_instances(InstanceIds=[instance.id], DryRun=False)
				speech_output = "La instancia o instancias con nombre o IDs " + str(names) + " se estan reiniciando."
			else:
				ec2_control.start_instances(InstanceIds=[instance.id], DryRun=False)
				speech_output = "La instancia o instancias con nombre o IDs " + str(names) + "se estan iniciando."


	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

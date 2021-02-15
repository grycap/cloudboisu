# cloudboisu

These skills are prepared to test them in Alexa Developer Console once you invoke them through Amazon Web Services lambda functions. A registered AWS and Alexa Developer Console accounts are required.

1. In AWS Lambda section, create a new lambda function for each skill (alexa_ec2 and alexa_s3). In the basic information of the creation menu, add a function name (alexaEC2 and alexaS3 respectively is recommended). In runtime, choose Python 3.8 and in permissions you can create a new IAM policy for the lambda function that needs to give access to EC2 and S3 full control, which is necessary for the skills.
2. In Alexa Developer Console, create a new skill. Skill name can be the same as the lambda function in order to prevent errors. In language, please choose spanish as is the language supported in the first version. In the skill model, choose Custom and method Alexa-hosted (Python).
3. Once the skill is created, copy the skill ID and in AWS Lambda, in design you must add an Alexa Skills Kit trigger to the function and add the copied skill ID.
4. To upload the lambda function you can copy the Python code of lambda_function.py in Function's Code or create a zip file of the directory of the skill (alexa_ec2 or alexa_s3 dir) and upload it as zip. (Actions-> Load a zip file)
5. Copy the lambda's function ARM (upper-right corner) inside the function and paste it in Amazon Developer Console in Default Region field (Endpoint menu)
6. Update the JSON file from Interaction Model folder in the "Intents" menu (you can add intents as you consider) and add an invocation name in "Invocation" menu. Save and build the model. All of these options are in "Build" tab.
7. In "Test" tab inside Amazon Developer Console invoke the skill saying the invoication name. You can interact with the skill with the options included in the Intent.

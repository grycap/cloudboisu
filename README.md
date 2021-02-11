# cloudboisu

1. Create lambda functions in AWS for each skill to be installed.
2. Create a zip file of alexa_skill and upload the zip file in the function's code
3. Configure IAM policies of lambda functions (allow EC2 and S3 full access depending on the skill)
4. Create the skill in Alexa Developer Console to test it
5. Update JSON file from Interaction Model folder in the Intents, Samples, and Slots menu (you can add intents as you consider) 
6. Add lambda's function ARM as Alexa Developer console skill endpoint
7. Copy Skill ID from Alexa Developer Console and add it as a lambda's function trigger.

Runtime compatibility: Python 3.8

import os
import sys
import datetime
import zipfile

welcome_intent = """
{
  "name": "Default Welcome Intent",
  "auto": true,
  "contexts": [],
  "responses": [
    {
      "resetContexts": false,
      "action": "input.welcome",
      "affectedContexts": [],
      "parameters": [],
      "messages": [
        {
          "type": 0,
          "lang": "en",
          "speech": "Welcome to board game rules helper.  Ask about any rule, or say CANCEL to exit"
        }
      ],
      "defaultResponsePlatforms": {},
      "speech": []
    }
  ],
  "priority": 500000,
  "webhookUsed": false,
  "webhookForSlotFilling": false,
  "fallbackIntent": false,
  "events": [
    {
      "name": "WELCOME"
    }
  ]
}
"""

fallback_intent = """
{
  "name": "Default Fallback Intent",
  "auto": true,
  "contexts": [],
  "responses": [
    {
      "resetContexts": false,
      "action": "input.unknown",
      "affectedContexts": [],
      "parameters": [],
      "messages": [
        {
          "type": 0,
          "lang": "en",
          "speech": "Ask about any rule"
        }
      ],
      "defaultResponsePlatforms": {},
      "speech": []
    }
  ],
  "priority": 500000,
  "webhookUsed": false,
  "webhookForSlotFilling": false,
  "fallbackIntent": true,
  "events": [
    {
      "name": "actions_intent_NO_INPUT"
    }
  ]
}
"""

agent_json = """
{
  "description": "%PACKAGE_NAME%",
  "language": "en",
  "disableInteractionLogs": true,
  "disableStackdriverLogs": true,
  "googleAssistant": {
    "googleAssistantCompatible": true,
    "project": "%PROJECT_NAME%",
    "welcomeIntentSignInRequired": false,
    "startIntents": [],
    "systemIntents": [],
    "endIntentIds": [],
    "oAuthLinking": {
      "required": false,
      "grantType": "AUTH_CODE_GRANT"
    },
    "voiceType": "FEMALE_1",
    "capabilities": [],
    "protocolVersion": "V2",
    "isDeviceAgent": false
  },
  "defaultTimezone": "America/Chicago",
  "webhook": {
    "available": false,
    "useForDomains": false,
    "cloudFunctionsEnabled": false,
    "cloudFunctionsInitialized": false
  },
  "isPrivate": true,
  "customClassifierMode": "use.after",
  "mlMinConfidence": 0.3,
  "supportedLanguages": [],
  "onePlatformApiVersion": "v2",
  "analyzeQueryTextSentiment": false,
  "enabledKnowledgeBaseNames": [],
  "knowledgeServiceConfidenceAdjustment": -0.4,
  "dialogBuilderMode": false
}
"""

speechFile = """
{
  "name": "%SKILLNAME%",
  "auto": true,
  "contexts": [],
  "responses": [
    {
      "resetContexts": false,
      "affectedContexts": [],
      "parameters": [],
      "messages": [
        {
          "type": 0,
          "lang": "en",
          "speech": "%RESPONSE%"
        }
      ],
      "defaultResponsePlatforms": {},
      "speech": []
    }
  ],
  "priority": 500000,
  "webhookUsed": false,
  "webhookForSlotFilling": false,
  "fallbackIntent": false,
  "events": []
}
"""

sampleTemplate = """
  {
    "data": [
      {
        "text": "%USERSAYS%",
        "userDefined": false
      }
    ],
    "isTemplate": false,
    "count": 0,
    "updated": 1544369557
  }
"""

#Globals
rule_name = ""
all_samples = ""
speech_json = ""
usersays_json = ""
output_path = "output_" + datetime.datetime.now().strftime("%m%d%Y%H%M%S")
line = ' '

projectName = input("Please type a name for this project")

try:
    os.mkdir(output_path)
    os.mkdir(output_path  + "/intents")
except OSError:
    print ("Creation of the directory %s failed" % output_path)
else:
    print ("Successfully created output directories")

with open('rules.txt', 'r') as fp:
   while line:
       line = fp.readline()
       str = line.rstrip().lstrip()
       # print(str)
       if (len(str) > 0):
           if (str[0] == '!'):
               # start of the rule
               rule_name = str.lstrip('!').strip(' ')

           elif (str[0] == '='):
               # strip = from what Google says
               google_says = str.lstrip('=')

               # Remove final comma from sample phrases
               all_samples = all_samples.rstrip('\n').rstrip(',')

               # Prepare final output strings for both files
               userFileFinal = '[' + all_samples + '\r\n]'
               speechFileFinal = speechFile \
                   .replace('%SKILLNAME%',rule_name) \
                   .replace('%RESPONSE%',google_says)

               # Write the speech file
               speech_file = open(output_path + '/intents/' + rule_name + '.json', "w")
               speech_file.write(speechFileFinal)
               speech_file.close()

               # And write the _usersays file
               userSays_file = open(output_path + '/intents/' + rule_name + '_usersays_en.json', "w")
               userSays_file.write(userFileFinal)
               userSays_file.close()

               # Package.json
               userSays_file = open(output_path + '/package.json', "w")
               userSays_file.write("""{ "version": "1.0.0" }""")
               userSays_file.close()

               # And finally the agent file
               agentJsonText = agent_json \
                   .replace('%PACKAGE_NAME%',projectName) \
                   .replace('%PROJECT_NAME%',projectName.strip(''))
               agentJsonFile = open(output_path + '/agent.json', "w")
               agentJsonFile.write(agentJsonText)
               agentJsonFile.close()

               # Welcome intent file
               welcomeFile = open(output_path + '/intents/Default Welcome Intent.json', "w")
               welcomeFile.write(welcome_intent)
               welcomeFile.close()

               # Fallback intent file
               fallbackFile = open(output_path + '/intents/Default Fallback Intent.json', "w")
               fallbackFile.write(fallback_intent)
               fallbackFile.close()

               # Reset our string variables for next rule
               all_samples = ""

           else:
               # Rule text
               sample = sampleTemplate.replace('%USERSAYS%',str.strip('<').strip('>').strip('\\').strip('&'))
               all_samples += sample + ','

zf = zipfile.ZipFile("upload_to_google.zip", "w")
for dirname, subdirs, files in os.walk(output_path):
    zf.write(dirname)
    for filename in files:
        zf.write(os.path.join(dirname, filename))
zf.close()

print ("Complete.  You can find your zip file in this subdirectory: " + output_path)


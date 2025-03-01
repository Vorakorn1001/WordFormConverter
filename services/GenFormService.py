import os
import json
from httplib2 import Http
from apiclient import discovery
from oauth2client import client, file, tools
from typing import List
from services.types.Question import Question
from services.types.UserInfo import UserInfo

class GenFormService:
    def __init__(self, collectEmail: bool = False):
        self.indexOffset: int = 0
        self.formService = None
        self.update = {
            "requests": [
                {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True,
                            },
                            "emailCollectionType": "VERIFIED" if collectEmail else "DO_NOT_COLLECT"
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }
            ]
        }
        
    def readTempFile(self, jsonPath):
        """Reads the content of the temporary file."""
        with open(jsonPath, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def createGoogleForm(self):
        """Initializes and creates a Google Form."""
        print("Creating Google Form...")
        scopes = "https://www.googleapis.com/auth/forms.body"
        discoveryDoc = "https://forms.googleapis.com/$discovery/rest?version=v1"

        store = file.Storage("token.json")
        creds = None
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets("client_secrets.json", scopes)
            creds = tools.run_flow(flow, store)

        self.formService = discovery.build(
            "forms",
            "v1",
            http=creds.authorize(Http()),
            discoveryServiceUrl=discoveryDoc,
            static_discovery=False,
        )
        
        formBody = {
            "info": {
                "title": self.name,
            }
        }
                
        self.formResult = self.formService.forms().create(body=formBody).execute()
        self.questionSetting = self.formService.forms().batchUpdate(
            formId=self.formResult["formId"],
            body=self.update
        ).execute()
        
        print(f"Google Form created: {self.formResult['formId']}")

    def addUserInfoSection(self):
        """Add answer info section to the Google Form using userInfo list."""
        def createTextQuestion(title, index, isParagraph):
            return {
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {"paragraph": isParagraph}
                            }
                        }
                    },
                    "location": {"index": index}
                }
            }

        def createChoiceQuestion(title, choices, index):
            return {
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": choice} for choice in choices]
                                }
                            }
                        }
                    },
                    "location": {"index": index}
                }
            }

        def createPageBreak(index):
            return {
                "createItem": {
                    "item": {
                        "title": "Exam Questions",
                        "pageBreakItem": {}
                    },
                    "location": {"index": index}
                }
            }

        requestsList = []
        indexOffset = 0
        for info in self.userInfo:
            question = info.get("question")
            choices = info.get("choices", None)
            if choices:
                requestsList.append(createChoiceQuestion(question, choices, indexOffset))
            else:
                requestsList.append(createTextQuestion(question, indexOffset, True))
            indexOffset += 1

        requestsList.append(createPageBreak(indexOffset))
        self.indexOffset = indexOffset + 1
        body = {"requests": requestsList}
        self.formService.forms().batchUpdate(
            formId=self.formResult["formId"],
            body=body
        ).execute()
        print("Answer info section added successfully.")

    def addQuestionsToForm(self):
        """Adds questions to the created Google Form."""
        print("Adding questions to Google Form...")
        questions = self.jsonOutput
        requestsList = []
        for i, question in enumerate(questions):
            requestsList.append({
                "createItem": {
                    "item": {
                        "title": question["question"],
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": choice} for choice in question["choices"]],
                                },
                                "grading": {
                                    "pointValue": 1,
                                    "correctAnswers": {"answers": [{"value": question["answer"]}]},
                                },
                            }
                        },
                    },
                    "location": {"index": self.indexOffset + i}
                }
            })

        batchUpdateRequest = {"requests": requestsList}
        self.formService.forms().batchUpdate(
            formId=self.formResult["formId"],
            body=batchUpdateRequest
        ).execute()
        print("Questions added successfully.")
    
    def removeOutputJson(self):
        jsonPath = "tmp/output.json"
        try:
            os.remove(jsonPath)
            print(f"Removed {jsonPath}")
        except FileNotFoundError:
            print(f"{jsonPath} not found.")

    def createFormFromJson(self, name: str, userInfo: List[UserInfo], jsonPath: str = "tmp/output.json"):
        """Creates a Google Form from questions loaded from output.json."""
        self.name: str = name
        self.userInfo: List[UserInfo] = userInfo
        self.jsonOutput: List[Question] = self.readTempFile(jsonPath)

        self.createGoogleForm()
        self.addUserInfoSection()
        self.addQuestionsToForm()
        self.removeOutputJson()
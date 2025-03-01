from services.GenJsonService import GenJsonService
from services.GenFormService import GenFormService

genJsonService = GenJsonService()
genformService = GenFormService()

name='<Google-Form-Title>'
userInfo=[
    {
        'question': "Name", # didn't provide a choice make it small paragraph question
    },
    {
        'question': 'Section',
        'choices': [
            '1', '2', '3' # with choices it now become multiple choices 
        ]
    }
]

genJsonService.run()

input("Please check the tmp/output.json file before proceeding to the next step.")

genformService.createFormFromJson(
    name=name,
    userInfo=userInfo
)

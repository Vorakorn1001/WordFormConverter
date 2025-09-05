from services.GenJsonService import GenJsonService
from services.GenFormService import GenFormService

genJsonService = GenJsonService()
genformService = GenFormService()

name = """ข้อสอบกลางภาควิชาสังคมกับสิ่งแวดล้อม 01-110-004 รศ.กรธัช คำสั่งจงเลือกคำตอบที่ถูกต้องเพียงข้อเดียว 75 ข้อ 30คะแนน"""
userInfo = [
    {
        'question': "Name", # didn't provide a choice make it small paragraph question
    },
    {
        'question': "Student ID", # didn't provide a choice make it small paragraph question
    },
    {
        'question': "Student Order", 
    },
    {
        'question': 'Section',
        'choices': [
            'เช้าจันทร์', 'บ่ายจันทร์', 'บ่ายอังคาร', 'เช้าพฤหัส' # with choices it now become multiple choices 
        ]
    }
]

genJsonService.run()

input("Please check the tmp/output.json file before proceeding to the next step.")

genformService.createFormFromJson(
    name=name,
    userInfo=userInfo
)

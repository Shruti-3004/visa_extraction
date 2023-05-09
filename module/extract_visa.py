from prettyprinter import pprint
import re
import json
import os
import shutil
from pdf2image import convert_from_path
from PIL import Image
import cv2

class ExtractVisaData:

    def __init__(self, pdf_file=None):
        self.pdf_file = pdf_file
        self.path = 'C:/air_ticket/visa_extraction/'
        filename = os.path.split(self.pdf_file)[-1]
        # self.preproc_pdf =  + "\\static\\uploads\\" + filename
        # shutil.copy(self.pdf_file, self.preproc_pdf)
        self.preproc_pdf = self.pdf_file
    # method to create a copy of original pdf to apply particular configurations and run tesseract command

    def convert_to_image(self, pdf):

        pages = convert_from_path(pdf, 500)
        # print(output_filename)
        image_file = "C:/air_ticket/visa_extraction/module/documents/visa/image.jpg"
        for page in pages:
            page.save(image_file, 'JPEG')
            break
        return image_file 

    def dpi_300(self, preproc_img):
        im = Image.open(preproc_img)
        im.save(preproc_img, dpi=(300, 300))
        return preproc_img

    def bgrtogray(self, preproc_img):
        image = cv2.imread(preproc_img)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(preproc_img, image)
        return preproc_img

    def image(self, filters):

        filename = self.pdf_file.split('/')[-1]
        # self.preproc_img = "C:\\Users\\Lenovo\\Desktop\\Image_Processing\\preprocessed\\receipts\\"+filters+"_"+filename
        # self.preproc_pdf = "C:\\Users\\Lenovo\\Desktop\\Image_Processing\\static\\uploads\\"+filename
        self.preproc_pdf = os.getcwd()+"/static/uploads/" + filename
        
        shutil.copy(self.pdf_file, self.preproc_pdf)
        return self.preproc_pdf

    # method to call the required filter methods and apply it to the 

    def preproc(self, image_file, conf, i):

        if conf[i].lower() == 'dpi-600':
            self.preproc_img = self.dpi_600(image_file)
        if conf[i].lower() == 'bgrtorgb':
            self.preproc_img = self.bgrtorgb(image_file)
        if conf[i].lower() == "bgrtogray":
            self.preproc_img = self.bgrtogray(image_file)
        if conf[i].lower() == "bgrtohsv":
            self.preproc_img = self.bgrtohsv(image_file)
        if conf[i].lower() == "threshold-binary":
            self.preproc_img = self.threshold_binary(image_file)
        if conf[i].lower() == "threshold-binary-otsu":
            self.preproc_img = self.threshold_binary_otsu(image_file)
        if conf[i].lower() == "threshold-binary-gaussian":
            self.preproc_img = self.threshold_binary_gaussian(image_file)
        if conf[i].lower() == "threshold-binary-inv":
            self.preproc_img = self.threshold_binary_inv(image_file)
        if conf[i].lower() == "threshold-zero":
            self.preproc_img = self.threshold_zero(image_file)
        if conf[i].lower() == "threshold-zero-inv":
            self.preproc_img = self.threshold_zero_inv(image_file)

    def get_authority(self):
        authority = ''
        for line in self.text_by_line:
            if 'authority' in line.lower():
                authority = line
                authority = authority.encode('ascii', 'ignore')
                authority = authority.decode()
                return authority

    def get_date_of_issue(self):
        date = ''
        for line in self.text_by_line:
            if re.search('.*date.*of.*issue.*', line.lower()):
                words = line.split()
                ind = words.index(':')
                date = words[ind+1]
                return date

    def get_place_of_issue(self):
        place = ''
        for line in self.text_by_line:
            if re.search('.*place.*of.*issue.*', line.lower()):
                words = line.split()
                ind = words.index(':')
                place = words[ind+2]
                return place

    def get_validity(self):
        date = ''
        for line in self.text_by_line:
            if re.search('.*valid.*until.*', line.lower()):
                words = line.split()
                ind = words.index(':')
                date = words[ind+1]
                return date

    def is_arabic(self, word):
        regex = r"[\u0600-\u06FF]+"
        if re.findall(regex, word):
            return True
        return False

    def get_full_name(self):
        name = ''
        for line in self.text_by_line:
            if re.search('.*full.*name.*', line.lower()):
                words = line.split()
                lwords = line.lower().split()
                ind = lwords.index('name:')
                for word in words[ind+1:]:
                    if self.is_arabic(word):
                        break
                    name += word + ' '
                return name.strip()

    def get_nationality(self):
        nationality = ''
        for line in self.text_by_line:
            if 'nationality' in line.lower():
                words = line.split()
                ind = words.index(':')
                nationality = words[ind+1]
                return nationality

    def get_place_of_birth(self):
        place = ''
        flag = 0
        for line in self.text_by_line:
            if 'place of birth' in line.lower():
                words = line.split()
                for i in range(len(words)):
                    if ':' in words[i]:
                        for j in range(i+1, len(words)):
                            if self.is_arabic(words[j]):
                                flag = 1
                                break
                            place += words[j] + ' '
                    if flag:
                        return place

    def get_date_of_birth(self):
        dob = ''
        for line in self.text_by_line:
            if 'date of birth' in line.lower():
                words = line.split()
                for i in range(len(words)):
                    if ':' in words[i]:
                        dob = words[i+1]
                        return dob

    def get_passport_no(self):
        pass_no = ''
        for line in self.text_by_line:
            if 'passport no.' in line.lower():
                line = line.replace('|', '')
                words = line.split()
                for i in range(len(words)):
                    if ':' in words[i]:
                        pass_no = ' '.join(words[i+1:i+4])
                        return pass_no

    def get_profession(self):
        profession = ''
        for line in self.text_by_line:
            if 'profession' in line.lower():
                words = line.split()
                for i in range(len(words)):
                    if ':' in words[i]:
                        profession = words[i+1]
                        return profession

    ##---------------------------------------------##

    def get_arabic_authority(self):
        auth = ''
        ind = 0
        for line in self.text_by_line:
            line = line.replace('\u200f', '')
            line = line.replace('\u200e', '')
            for i in range(len(line.split())):
                if self.is_arabic(line.split()[i]):
                    ind = i
                    break
            auth = ' '.join(line.split()[ind:])
            return auth
            
        
    def get_arabic_date_of_issue(self):
        doi = ''
        for line in self.text_by_line:
            # print(line)
            if re.search('.*date.*of.*issue.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                # print(line)
                words = line.split()
                # print('words---> ', words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i+4]

    def get_arabic_place_of_issue(self):
        for line in self.text_by_line:
            if re.search('.*place.*of.*issue.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i+5]

    def get_arabic_validity_date(self):
        for line in self.text_by_line:
            if re.search('.*valid.*until.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i-2]

    def get_arabic_full_name(self):
        for line in self.text_by_line:
            if re.search('.*full.*name.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return ' '.join(words[i+2:]).strip('. ')

    def get_arabic_nationality(self):
        for line in self.text_by_line:
            if re.search('.*nationality.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i+2]

    def get_arabic_place_of_birth(self):
        for line in self.text_by_line:
            if re.search('.*place.*of.*birth.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return ' '.join(words[i+3:])

    def get_arabic_date_of_birth(self):
        for line in self.text_by_line:
            if re.search('.*date.*of.*birth.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i-2]

    def get_arabic_passport_no(self):
        for line in self.text_by_line:
            if re.search('.*passport.*no.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i-2]

    def get_arabic_profession(self):
        for line in self.text_by_line:
            if re.search('.*profession.*', line.lower()):
                line = line.replace('\u200f', '')
                line = line.replace('\u200e', '')
                words = line.split()
                # print(words)
                for i in range(len(words)):
                    if self.is_arabic(words[i]):
                        return words[i+2]

    # def extract_text_ocr_tesseract_cli(self, image_file, {'oem': [1]}):
    #     with open('C:\\air_ticket\\arabic_page0.jpg_4_ara_eng_set_dpi-convert_to_grayscale.txt', 'r', encoding='utf-8') as fp:
    #         text = fp.read()
    #         text = text.splitlines()
    #         text = [line for line in text if not line.isspace() and len(line) > 0]

    def extract_text_ocr_tesseract_cli(self, file=None, filters=None):
        """ 
        Run tesseract from CLI
        """
        os.environ['TESSERACT'] = "C:/air_ticket/visa_extraction"
        os.environ['TESSDATA_PREFIX'] = "C:/air_ticket/visa_extraction/tessdata" 

        oem_list = filters['oem']
        psm_list = filters['psm']
        
        for each_oem in oem_list:
            oem_str = "--oem " + str(each_oem)
            
            for each_psm in psm_list:
                psm_str = "--psm " + str(each_psm)
                
                lang_str = "-l eng+ara"

                command_parts = []
                command_parts.append("tesseract")
                command_parts.append(file)
                command_parts.append("output")
                command_parts.append(oem_str)
                command_parts.append(lang_str)
                command_parts.append(psm_str)
                print(command_parts)
                # Creating the cli command
                command = " ".join(command_parts)
                print("COMMAND : ", command)
                # print(command)
                # res = os.popen(command).read()
                os.system(command)
                # print(res)

                with open('output.txt', 'r', encoding='utf-8') as fp:
                    res = fp.read()
                    res = res.splitlines()
                    res = [line for line in res if not line.isspace() and len(line) > 0]

                self.text = res
                # if res == 0:
                    # filename = output_file.replace("\\", "//") + '.txt'
                 #   with open('output.txt', encoding="utf8") as fp:
                 #       self.text = fp.read()
                    # os.remove("output.txt")
        
        return self.text

    def get_all(self):

        filters = 'dpi-300_bgrtogray_psm_4'

        if filters:
            
            conf = filters.split('_')
            self.preproc_pdf = self.image(filters)
            print("PDF : ", self.preproc_pdf)
            image_file = self.convert_to_image(self.preproc_pdf)
            for i in range(len(conf)-1):
                if conf[i].lower() == 'psm':
                    psm_value = conf[i+1]
                else:
                    self.preproc(image_file, conf, i)

        # print(self.preproc_img)
        image_file = self.convert_to_image(self.preproc_pdf)
        self.text = self.extract_text_ocr_tesseract_cli(image_file, {'oem':[1], 'psm':[4]})
        self.text_by_line = self.text
        # self.text_by_line = self.text.split("\n")
        print('SELF.TEXT_BY_LINE----------> ', self.text_by_line)
        pprint(self.text_by_line)

        self.all = {}

        f = open('C:/air_ticket/visa_extraction/keys.json', encoding='utf-8')
        data = json.load(f)

        self.all['English'] = {
            'Authority': self.get_authority(),
            'Date of Issue': self.get_date_of_issue(),
            'Place of Issue': self.get_place_of_issue(),
            'Validity': self.get_validity(),
            'Full Name': self.get_full_name(),
            'Nationality': self.get_nationality(),
            'Place of Birth': self.get_place_of_birth(),
            'Date of Birth': self.get_date_of_birth(),
            'Passport Number': self.get_passport_no(),
            'Profession': self.get_profession()
        }

        f = open('keys.json', encoding='utf-8')
        data = json.load(f)

        self.all['Arabic'] = {
        data['Authority'][0]: self.get_arabic_authority(),
        data['Date of Issue'][0]: self.get_arabic_date_of_issue(),
        data['Place of Issue'][0]: self.get_arabic_place_of_issue(),
        data['Validity'][0]: self.get_arabic_validity_date(),
        data['Full Name'][0]: self.get_arabic_full_name(),
        data['Nationality'][0]: self.get_arabic_nationality(),
        data['Place of Birth'][0]: self.get_arabic_place_of_birth(),
        data['Date of Birth'][0]: self.get_arabic_date_of_birth(),
        data['Passport Number'][0]: self.get_arabic_passport_no(),
        data['Profession'][0]: self.get_arabic_profession()
    }

    # result['Arabic'] = {
    #     data['Authority'][0]: self.get_arabic_authority(text),
    #     data['Date of Issue'][0]: self.get_arabic_date_of_issue(text),
    #     data['Place of Issue'][0]: self.get_arabic_place_of_issue(text),
    #     data['Validity'][0]: self.get_arabic_validity_date(text),
    #     data['Full Name'][0]: self.get_arabic_full_name(text),
    #     data['Nationality'][0]: self.get_arabic_nationality(text),
    #     data['Place of Birth'][0]: self.get_arabic_place_of_birth(text),
    #     data['Date of Birth'][0]: self.get_arabic_date_of_birth(text),
    #     data['Passport Number'][0]: self.get_arabic_passport_no(text),
    #     data['Profession'][0]: self.get_arabic_profession(text)
    # }

    # pprint(result)
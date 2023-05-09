from module.extract_visa import ExtractVisaData

class VisaExtract:
    def __init__(self, image_file, document_type, field_type, file_type):
        if file_type.lower() == "document":
            self.obj = ExtractVisaData(image_file)
            self.field_type = field_type.lower() 

    def get_output(self):
        self.obj.get_all()
        print("hello")
        if hasattr(self.obj, self.field_type):
            return getattr(self.obj, self.field_type)
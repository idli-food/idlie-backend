import re





class HotelCreation:

    @classmethod
    def generate_request_id(cls,phonenumber):
        return "re342r432"


    @classmethod
    def is_request_id_valid(cls,request_id):
        original_request_id = "re342r432"

        if request_id == original_request_id:
            return True
        return False
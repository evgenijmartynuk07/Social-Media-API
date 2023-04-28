from rest_framework.exceptions import APIException


class ObjectAlreadyExists(APIException):
    status_code = 400
    default_detail = "This Profile already exists."


class AlreadySubscribeExists(APIException):
    status_code = 400
    default_detail = "You already subscribe."

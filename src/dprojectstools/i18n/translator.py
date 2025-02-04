import boto3
from ..secrets import SecretsManager

# translate
class Translator:

    # ctor
    def __init__(self, aws_access_key_id:str = None, aws_secret_access_key: str = None):

        # get credentials        
        secrets = SecretsManager("translator")
        if aws_access_key_id == None:
            aws_access_key_id = secrets.get("TRANSLATOR_AWS_ACCESS_KEY_ID")

        if aws_secret_access_key == None:
            aws_secret_access_key = secrets.get("TRANSLATOR_AWS_SECRET_ACCESS_KEY")
        # create client        
        self._translate_client = boto3.client(
            service_name="translate", 
            aws_access_key_id = aws_access_key_id, 
            aws_secret_access_key = aws_secret_access_key,
            region_name="us-east-1")

    # methods
    def translate(self, text: str, src: str, dest:str) -> str:
        response = self._translate_client.translate_text(
            Text=text,
            SourceLanguageCode=src,
            TargetLanguageCode=dest
        )
        return response["TranslatedText"]
    

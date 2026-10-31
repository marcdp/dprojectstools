import boto3
import os
from ..secrets import SecretsManager

# translate
class Translator:

    # ctor
    def __init__(self, aws_access_key_id:str = None, aws_secret_access_key: str = None):

        # Get credentials from arguments or environment variables
        aws_access_key_id = aws_access_key_id or os.getenv("TRANSLATOR_AWS_ACCESS_KEY_ID")
        aws_secret_access_key = aws_secret_access_key or os.getenv("TRANSLATOR_AWS_SECRET_ACCESS_KEY")

        # Fallback to SecretsManager
        if not aws_access_key_id or not aws_secret_access_key:
            secrets = SecretsManager("translator")
            aws_access_key_id = aws_access_key_id or secrets.get("TRANSLATOR_AWS_ACCESS_KEY_ID")
            aws_secret_access_key = aws_secret_access_key or secrets.get("TRANSLATOR_AWS_SECRET_ACCESS_KEY")

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
    

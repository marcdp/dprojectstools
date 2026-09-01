from ..commands import command, Argument, Flag, CommandsManager
from typing import Annotated, List
from lxml import etree
import sys
import urllib
import pyotp

# class
class Otp:

    # methods
    @command()
    def generate(self, 
        # input
        auth_otp_url: Annotated[str,  Argument("URL")]
    ):
        # otpurl parsing
        parsed_url = urllib.parse.urlparse(auth_otp_url)
        secret = urllib.parse.parse_qs(parsed_url.query).get('secret', [None])[0].replace(' ', '').upper()
        algorithm = urllib.parse.parse_qs(parsed_url.query).get('algorithm', ['SHA1'])[0]
        digits = int(urllib.parse.parse_qs(parsed_url.query).get('digits', [6])[0])
        period = int(urllib.parse.parse_qs(parsed_url.query).get('period', [30])[0])
        
        # get totp instance
        totp = pyotp.TOTP(secret, digits=digits, digest=algorithm.lower(), interval=period)

        print(totp.now())
        return 0
        

        
# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(instance = Otp())
    commandsManager.execute(sys.argv) 
if __name__ == "__main__":
    main()


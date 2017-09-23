
class Message:

    @staticmethod
    def getStartMessage():
        return 'Hi! I need some information about you\n\n'

    @staticmethod
    def getGenderStartMessage():
        return '1. What it your gender?'

    @staticmethod
    def getGenderEndMessage(genderPrefix, lastName):
        return 'Ok, ' + genderPrefix + ' ' + lastName

    @staticmethod
    def getPhotoStartMessage():
        return '2. Send your personal photo (you can /skip this point)'

    @staticmethod
    def getDescriptionStartMessage():
        return '3. Tell me something about yourself'

    @staticmethod
    def getEndMessage(userModel):
        # show saved data to user
        strUserData = ''
        for (label, value) in userModel.getPublicAttributes().items():
            strUserData += '%s : %s \n' % (label, value)
        return  'Your information has been stored on our server: ' \
                + '\n\n'\
                + strUserData \
                + '\n\n ' \
                'Thank you! Goodbye!'

    @staticmethod
    def getGoBackMessage():
        return 'Go to the previous step /goback'
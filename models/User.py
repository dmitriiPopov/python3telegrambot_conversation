
from collections import OrderedDict
from config.config import Config

# Class for User entity
class User:

    GENDER_VALUE_MALE   = 'Male'
    GENDER_VALUE_FEMALE = 'Female'

    def __init__(self):
        self.username        = None
        self.gender          = None
        # https://python-telegram-bot.readthedocs.io/en/stable/telegram.file.html#telegram.File
        self.photoFileObject = None
        self.photoCaption    = None
        self.description     = None

    def setUsername(self, value):
        self.username = value

    def setGender(self, value, onlyInsert = False):
        if (onlyInsert and self.gender != None) :
            value = self.gender
        self.gender = value

    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.file.html#telegram.File
    def setPhotoFileObject(self, value, onlyInsert = False):
        if (onlyInsert and self.photoFileObject != None):
            value = self.photoFileObject
        self.photoFileObject = value

    def setPhotoCaption(self, value, onlyInsert = False):
        if (onlyInsert and self.photoCaption != None):
            value = self.photoCaption
        self.photoCaption = value

    def setDescription(self, value, onlyInsert = False):
        if (onlyInsert and self.description != None):
            value = self.description
        self.description = value

    # Get prefix for selected gender value
    def getGenderPrefix(self):
        prefixes = {
            self.GENDER_VALUE_MALE: 'Mr.',
            self.GENDER_VALUE_FEMALE: 'Mrs.'
        }
        return prefixes[self.gender]

    # get dictionary with current attributes
    def getPublicAttributes(self):
        return OrderedDict({
            'Gender' : self.gender,
            'Photo': ('' if self.photoFileObject == None else self.photoFileObject.file_path),
            'Photo caption': ('' if self.photoFileObject == None else self.photoCaption),
            'Description': self.description,
        })


    def save(self):
        # open storage
        text_file = open(self.getUserTextfile(), "w")

        #save gender
        text_file.write('Gender: %s\n' % (self.gender))
        # save photo
        if self.photoFileObject != None:
            imagefile = self.getUserImagefile()
            # download file on server
            text_file.write('File with image: %s\n' % (imagefile))
            self.photoFileObject.download(imagefile)
            # save caption to photo
            text_file.write('Caption to image: %s\n' % (self.photoCaption))
        # save description
        text_file.write('Description: %s\n' % (self.description))

        #close storage
        text_file.close()

    # get filename for text information
    def getUserTextfile(self):
        return Config.APP_WEB_UPLOADS_DIR + '/' + self.username + '_text.txt'

    # get filename for image
    def getUserImagefile(self):
        return Config.APP_WEB_UPLOADS_DIR + '/' + self.username + '_photo.jpg'


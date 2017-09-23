# application bot

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

from config.config import Config
from models.User import User
from helpers.Message import Message

import logging


# defined constants as points in conversation
STEP_GENDER      = 0
STEP_PHOTO       = 1
STEP_DESCRIPTION = 2

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# set global user object (one instance)
userModel    = User()

####### first start action for `/start`
def start(bot, update):
    # keyboard for first question
    # https://core.telegram.org/bots/api#keyboardbutton
    keyboard = [
        [
            KeyboardButton(User.GENDER_VALUE_MALE),
            KeyboardButton(User.GENDER_VALUE_FEMALE)
        ]
    ]

    # https://core.telegram.org/bots/api#replykeyboardmarkup
    # https://core.telegram.org/bots#keyboards
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # set user username
    userModel.setUsername(update.message.from_user.username)

    # show message to client
    update.message.reply_text(
        Message.getStartMessage() +
        Message.getGenderStartMessage(),
        reply_markup=reply_markup
    )
    # go to next step
    return STEP_GENDER

###### action after getting gender from user
def handleGenderAction(bot, update):
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.message.html
    user = update.message.from_user
    # set gender to User model
    userModel.setGender(update.message.text, True)

    # console log
    logger.info("Gender of %s: %s" % (user.username, update.message.text))

    # show message to client
    update.message.reply_text(
        Message.getGenderEndMessage(userModel.getGenderPrefix(), user.last_name)
        + '\n\n' +
        Message.getPhotoStartMessage()
        + '\n' +
        Message.getGoBackMessage(),
        reply_markup=ReplyKeyboardRemove()
    )
    # go to next step
    return STEP_PHOTO


###### action after sending photo by user
# https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html#telegram.Bot
def handlePhotoAction(bot, update):
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.message.html
    user = update.message.from_user
    # set image object to User Model
    userModel.setPhotoFileObject(bot.get_file(update.message.photo[-1].file_id), True)
    # set caption under image to User Model
    userModel.setPhotoCaption(update.message.caption, True)
    # console log
    logger.info("Photo of %s: %s" % (user.username, userModel.getUserImagefile()))

    # show message to client
    update.message.reply_text(
        Message.getDescriptionStartMessage()
        + '\n' +
        Message.getGoBackMessage()
    )
    # got to next step
    return STEP_DESCRIPTION

##### action after skipping photo
def handleSkipPhotoAction(bot, update):
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html
    user = update.message.from_user
    # console log
    logger.info("User %s did not send a photo." % user.first_name)

    # show message to client
    update.message.reply_text(
        Message.getDescriptionStartMessage()
        + '\n' +
        Message.getGoBackMessage()
    )
    # go to next step
    return STEP_DESCRIPTION

##### handle description request (last action)
def handleDescriptionAction(bot, update):
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html
    user = update.message.from_user
    # set description to user model
    userModel.setDescription(update.message.text)
    # console log
    logger.info("Description of %s: %s" % (user.first_name, update.message.text))

    #save user data
    userModel.save()

    #last message for user
    update.message.reply_text(Message.getEndMessage(userModel))
    # signal that should end conversation
    return ConversationHandler.END


###### `/cancel`
def handleCancelAction(bot, update):
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.user.html
    user = update.message.from_user
    # console log
    logger.info("User %s canceled the conversation." % user.username)

    # last message for user
    update.message.reply_text(
        'Goodbye, ' + user.first_name + ' ' + user.last_name,
        reply_markup=ReplyKeyboardRemove()
    )
    # sygnal that should end conversation
    return ConversationHandler.END

########### `/help`
def handleHelpAction(bot, update):
    update.message.reply_text("INFO: Use /start to start filling information; /cancel for quit")

########### error handler
def handleErrorAction(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


###### BEGIN ######
def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(Config.BOT_TOKEN)

    # Add conversation handler with the states GENDER, PHOTO, and DESCRIPTION
    conversation_handler = ConversationHandler(
        # first state
        entry_points=[
            CommandHandler('start', start)
        ],
        # list of steps and appropriated handlers
        states = {
            STEP_GENDER: [
                RegexHandler('^(%s|%s)$' % (User.GENDER_VALUE_MALE, User.GENDER_VALUE_FEMALE), handleGenderAction),

            ],

            STEP_PHOTO: [
                MessageHandler(Filters.photo, handlePhotoAction),
                CommandHandler('skip', handleSkipPhotoAction),
                CommandHandler('goback', start)
            ],

            STEP_DESCRIPTION: [
                MessageHandler(Filters.text, handleDescriptionAction),
                CommandHandler('goback', handleGenderAction)
            ]
        },
        # conversation fallback handler
        fallbacks = [
            CommandHandler('cancel', handleCancelAction)
        ]
    )

    # add conversation handler to dispatcher
    updater.dispatcher.add_handler(conversation_handler)

    # when user clicks `/help` do...
    updater.dispatcher.add_handler(CommandHandler('help', handleHelpAction))

    # log all errors
    updater.dispatcher.add_error_handler(handleErrorAction)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
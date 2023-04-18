from command.basecommand import BaseCommand


class DefaultFallbackCommand(BaseCommand):

    def __init__(self):
        super(DefaultFallbackCommand, self).__int__(command_name="cancel")

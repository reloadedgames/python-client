from commands.config import ConfigCommand
from docopt import docopt

if __name__ == '__main__':
    command = ConfigCommand()
    args = docopt(command.help())
    command.run(args)
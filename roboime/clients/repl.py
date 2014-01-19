from .cli import CLI


class Repl(CLI):

    def read(self):
        return raw_input('> ')

    def write(self, text):
        print text

from .cli import CLI


class Repl(CLI):

    def read(self):
        cmdlist = raw_input('> ').split()
        return {
            'cmd': cmdlist[0],
            'args': cmdlist[1:],
        }

    def write(self, text, ok=True):
        print text

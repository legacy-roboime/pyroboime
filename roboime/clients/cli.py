from threading import Thread


class CLI(Thread):

    def __init__(self, world):
        super(CLI, self).__init__()
        self.world = world
        self.quit = False

    def read(self):
        raise NotImplementedError('this method is meant to be overridden')

    def write(self, text):
        raise NotImplementedError('this method is meant to be overridden')

    def run(self):
        while True:
            try:
                cmd = self.read()

                if cmd == 'q' or cmd == 'quit' or cmd == 'exit':
                    self.quit = True
                    self.write('Bye...')
                    break
                else:
                    self.write('Command {} is invalid.'.format(cmd))

            except Exception as e:
                self.write('An exception occured: {}'.format(e))
                self.write('Quiting...')
                self.quit = True
                break

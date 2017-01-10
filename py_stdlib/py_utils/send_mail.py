
class SenMail(object):
    def __init__(self, mail='/bin/mail'):
        self.bin = mail

    def _create_message(message):
        # Securely create a temporary file
        pass

    def send_mail(sender, to, subject, message):
        os.system('echo \'%s\' > message.txt' % (message))
        command = '/bin/mail -s \'%s\' %s < \'%s\'' % (subject, to, 'message.txt')
        os.system(command)

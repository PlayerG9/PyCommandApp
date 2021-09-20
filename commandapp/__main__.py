import sys
import shlex
if len(sys.argv) <= 1:
    sys.argv.extend(shlex.split(input("=> ")))
import commandapp as cmdapp


app = cmdapp.CommandApp()

app.version = cmdapp.__version__


@app.register
def test():
    print("Test success")


def subcmd():
    raise RuntimeError()


@app.register(name='raise')
def cmd_raise():
    subcmd()


app.run()

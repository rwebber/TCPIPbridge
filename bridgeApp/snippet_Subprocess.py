import subprocess
import ast
import time

#  C:\Users\DusX\CODE\python\TCPIP_bridge\bridgeApp\
p = subprocess.Popen(["python", "-u", r"C:\Users\DusX\CODE\python\TCPIP_bridge\bridgeApp\mediawiki_socketstream.py"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)

print ("launched: " + p.stdout.readline()), # read the first line
hold = True
while hold: # repeat several times to show that it works
    # print >>p.stdin, i # write input
    # p.stdin.flush() # not necessary in this case
    currentT = time.clock()

    data = p.stdout.readline() # read output
    print ("Line" + ": " + data)

    try:
        data = ast.literal_eval(data)
        print("data=: " + str(type(data)))
        if type(data) is 'list':
            print("MATCH")
        hold = False
    except:
        # add timeout code, incase
        data = False
        pass

print("DONE: " + str(data))

# print p.communicate("n\n")[0], # signal the child to exit,
print p.communicate()[0] # signal the child to exit, # read the rest of the output, # wait for the child to exit
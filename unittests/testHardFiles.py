import commands

f = open('HARD_FILES', 'r')
l = f.readlines()
f.close()

for a in l:
    status, out = commands.getstatusoutput('ls -dl mnt' + a.strip())
    if status != 0:
        print a.strip()
        print out

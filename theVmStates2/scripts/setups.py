import re
import sys

f = sys.argv[1]
param = sys.argv[2]
val = sys.argv[3]
dest = sys.argv[4]

with open(f, 'r') as reader:
    content = reader.read()
    new_content = re.sub(r"%s:\s+\d+.?\d*" % param, "%s: %s" % (param, val), content)

with open(dest, 'w') as writer:
    writer.write(new_content)
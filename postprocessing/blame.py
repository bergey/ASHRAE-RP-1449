import sys
import os
import re

blamere = re.compile(r'([0-9a-f]+)( \(.*\))( .*$)\n')
#msgre = re.compile(r'Date:.*\n\n\s+([^\n]*)\n')

commit_msgs = dict()

def get_msg(cid, width=80):
    os.system('git show {0} | head > tmp-git-show'.format(cid))
    commit_desc = open('tmp-git-show').readlines()
    msg = commit_desc[4].strip()

    if width==None: #don't pad or truncate
        return msg
    elif len(msg)>width:
        return msg[:width+1]
    else:
        pad = ' '*(width-len(msg))
        return msg+pad
        
for line in sys.stdin:
    match = blamere.search(line)
    cid = match.group(1) # commit id
    if not cid in commit_msgs:
        commit_msgs[cid] = get_msg(cid)
    print('{0}{1}{2}'.format(commit_msgs[cid], match.group(2), match.group(3)))

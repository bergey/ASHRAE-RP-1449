# Read a csv file of TRNSYS sims to be performed, one per row
# push JSON specs of these sims to Amazon SQS
# to be read and performed by a suitable EC2 instance running Cygwin

import json
from csv import DictReader
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
import sys
from time import sleep

configuration = json.loads(open('trnbatch.conf').read())
user_data =  configuration['user_data']

sqs = SQSConnection(user_data['AWS_ACCESS_KEY'], user_data['AWS_SECRET_ACCESS_KEY'])
q = sqs.create_queue(user_data['TRN_ResDH_INPUT_QUEUE'], 25*60)
logq = sqs.create_queue(user_data['TRN_ResDH_INPUT_QUEUE']+'-log')

def push(o):
    m = Message()
    m.set_body(json.dumps(o))
    status = q.write(m)
    if not status:
        print "SQS didn't write a message; waiting and retrying"
        sleep(5)
        push(o)

if len(sys.argv) > 1:
  for csvname in sys.argv[1:]:
      for row in DictReader(open(csvname)):
          push(row)
      print("finished {0}".format(csvname))

# report log
while True:
    msg = logq.read()
    if msg == None:
        sleep(10)
        continue
    print(msg.get_body())
    logq.delete_message(msg)

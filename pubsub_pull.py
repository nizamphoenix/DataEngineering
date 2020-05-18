'''
Messages are pulled from Pub/Sub by a subscriber and acknowledged
Step1: install pubsub sudo pip install --upgrade google-cloud-pubsub
Step2: create topic with gcloud pubsub topics create topic_name
Step3: subscribe to topic created in Step2 with gcloud pubsub subscriptions create subscriber_name --topic=topic_name
'''

from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()

def callback(message):
  print('Message recieved is: {}'.format(message))
  message.ack()# acknowleding the msg, executed by the subscriber


subscription_path = 'projects/my_project_name/subscriptions/cpsubs'
subscriber.subscribe(subscription_path, callback=callback)

#register a callback and forget. No need to keep looping and pulling and sleeping

import pika
import numpy as np
import json
import time
from datetime import datetime
from sklearn.datasets import load_diabetes

while True:
    try:
        X, y = load_diabetes(return_X_y=True)
        random_row = np.random.randint(0, X.shape[0]-1)
        message_id = datetime.timestamp(datetime.now())

        message_y_true = {
            'id': message_id,
            'body': float(y[random_row])
        }
        message_features = {
            'id': message_id,
            'body': X[random_row].tolist()
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='y_true')
        channel.queue_declare(queue='features')

        channel.basic_publish(exchange='',
                            routing_key='y_true',
                            body=json.dumps(message_y_true))
        print('Сообщение с правильным ответом отправлено в очередь')

        channel.basic_publish(exchange='',
                            routing_key='features',
                            body=json.dumps(message_features))
        print('Сообщение с вектором признаков отправлено в очередь')

        time.sleep(10)

        connection.close()
    except:
        print('Не удалось подключиться к очереди')


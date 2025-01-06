import pika
import pickle
import numpy as np
import json

try:
    with open('myfile.pkl', 'rb') as pkl_file:
        regressor = pickle.load(pkl_file)
    print('Модель успешно загружена')
except Exception as e:
    print(f'Ошибка при загрузке модели: {e}')
    exit(1)

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='features')
    channel.queue_declare(queue='y_pred')

    def callback(ch, method, properties, body):
        try:
            print(f'Получен вектор признаков: {body}')
            message = json.loads(body)
            features = message.get('body')
            message_id = message.get('id')

            if features is None or message_id is None:
                raise ValueError('Сообщение не содержит необходимых данных (id или body)')

            features_array = np.array(features).reshape(1, -1)
            pred = regressor.predict(features_array)

            prediction_message = {
                'id': message_id,
                'y_pred': float(pred[0])
            }

            channel.basic_publish(
                exchange='',
                routing_key='y_pred',
                body=json.dumps(prediction_message)
            )
            print(f'Предсказание {prediction_message} отправлено в очередь y_pred')

        except Exception as e:
            print(f'Ошибка в callback: {e}')

    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

except Exception as e:
    print(f'Ошибка подключения к RabbitMQ: {e}')

finally:
    if 'connection' in locals() and connection.is_open:
        connection.close()
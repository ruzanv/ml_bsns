import pika
import json
import csv
import os

log_file = './logs/metric_log.csv'
os.makedirs('./logs', exist_ok=True)

if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'y_true', 'y_pred', 'absolute_error'])

messages = {}

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='y_pred')

    def log_to_csv(message_id, y_true, y_pred):
        try:
            absolute_error = abs(y_true - y_pred)
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([message_id, y_true, y_pred, absolute_error])
            print(f'Записано в лог: id={message_id}, y_true={y_true}, y_pred={y_pred}, error={absolute_error}')
        except Exception as e:
            print(f'Ошибка записи в CSV: {e}')

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            message_id = data.get('id')
            
            if method.routing_key == 'y_true':
                value = data.get('body')
                if message_id not in messages:
                    messages[message_id] = {}
                messages[message_id]['y_true'] = value
            elif method.routing_key == 'y_pred':
                value = data.get('y_pred')
                if message_id not in messages:
                    messages[message_id] = {}
                messages[message_id]['y_pred'] = value

            if 'y_true' in messages[message_id] and 'y_pred' in messages[message_id]:
                log_to_csv(
                    message_id,
                    messages[message_id]['y_true'],
                    messages[message_id]['y_pred']
                )
                del messages[message_id]

        except Exception as e:
            print(f'Ошибка обработки сообщения: {e}')

    channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

except Exception as e:
    print(f'Ошибка подключения или обработки: {e}')

finally:
    if 'connection' in locals() and connection.is_open:
        connection.close()
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

log_file = './logs/metric_log.csv'
output_image = './logs/error_distribution.png'
os.makedirs('./logs', exist_ok=True)

print('Plot запущен')

while True:
    try:
        if os.path.exists(log_file):
            data = pd.read_csv(log_file)

            if 'absolute_error' in data.columns and not data.empty:
                absolute_errors = data['absolute_error']

                plt.figure(figsize=(10, 6))
                plt.hist(absolute_errors, bins=20, color='blue', alpha=0.7, edgecolor='black')
                plt.title('Distribution of Absolute Errors', fontsize=16)
                plt.xlabel('Absolute Error', fontsize=14)
                plt.ylabel('Frequency', fontsize=14)
                plt.grid(axis='y', linestyle='--', alpha=0.7)

                plt.savefig(output_image)
                plt.close()
                print(f'Гистограмма обновлена: {output_image}')
            else:
                print('Файл пуст или данные об абсолютных ошибках отсутствуют.')
        else:
            print('Файл metric_log.csv не создан.')

    except Exception as e:
        print(f'Ошибка при обработке: {e}')

    time.sleep(10)
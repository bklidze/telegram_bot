import unittest # импортируем библиотеку для написания тестов на Python
from unittest.mock import patch, MagicMock # импортирует инструменты для подмены объектов во время исполнения тестов, patch временно заменяет функцию на мок, MagicMock создает заглушку, где можно настраивать значения
import requests # импортируем библиотеку request, необходимую для отправки HTTP-запросов
import telebot # импортируем библиотеку telebot, необходимую для работы с ботом Телеграмма
import get_weather # импортируем файл, который мы тестируем

class TestWeatherBot(unittest.TestCase): # объявляем класс TestWeatherBot, который наследуется от unitest.TestCase, все методы класса запускаются как отдельный тест
    @patch('get_weather.requests.get') # @patch временно заменяет получаемое значение GET на мок-объект
    def test_get_weather_success(self, mock_get): # объявляем функцию test_get_weather_success, где мы будем вызывать GET-запрос с необходимыми нам значениями, в mock_get мы указываем необходимый ответ
        mock_response = MagicMock() # присваеваем переменной mock_response мок-значения:
        mock_response.status_code = 200 # ответ GET должен быть равен 200
        mock_response.json.return_value = { # прописанный json-словарь, который функция получит в ответ
            'name': 'Moscow',
            'main': {'temp': 22.5, 'feels_like': 20.1, 'humidity': 60},
            'weather': [{'description': 'clear sky'}],
            'wind': {'speed': 4.5}
        }
        mock_get.return_value = mock_response # объявляем, что при вызове функции get_weather.requests.get, она получит ответ с необходимыми нам данными, содержащимися в переменной mock_response

        result = get_weather.get_weather('fake_api_key') # присваеваем переменной result ответы функции get_weather, которая получает наш мок-ответ
        self.assertIsNotNone(result) # проверяем, что функция не вернула None
        self.assertIn('Moscow', result) # проверяем, что в ответе есть указанное значение
        self.assertIn('22.5°C', result) # проверяем, что в ответе есть указанное значение
        self.assertIn('Clear sky', result) # проверяем, что в ответе есть указанное значение
    
    @patch('get_weather.requests.get') # @patch временно заменяет получаемое значение GET на мок-объект
    def test_get_weather_network_exception(self, mock_get): # объявляем функцию test_get_weather_network_exception, где мы будем вызывать GET-запрос с необходимыми нам значениями, в mock_get мы указываем необходимый ответ
        mock_get.side_effect = requests.exceptions.ConnectionError('No internet') # вызываем из библиотеки request, с помощью свойства .side_effect, ошибку requests.exceptions.ConnectionError, те. ошибку подключения интернета и присваем это значение переменной mock_get

        result = get_weather.get_weather('fake_api_key') # присваеваем переменной result ответы функции get_weather, которая получает наш мок-ответ
        self.assertIsNone(result) # проверяем, что функция не вернула None

    def test_bot_keyboard(self):  # объявляем функцию test_bot_keyboard, которая проверяет создание кнопки
        markup = get_weather.bot_keyboard() # присваеваем переменной markup ответ функции get_weather.bot_keyboard
        self.assertIsInstance(markup, telebot.types.ReplyKeyboardMarkup) # проверяем, что переменная markup является экземпляром класса ReplyKeyboardMarkup библиотеки telebot
        self.assertTrue(markup.resize_keyboard) # проверяем, что атрибут resize_keyboard равен True
        
        button = markup.keyboard[0][0] # получаем саму кнопку
        
        # проверяем тип кнопки: в некоторых версиях telebot это словарь, в других - объект KeyboardButton
        if isinstance(button, dict):
            self.assertEqual(button['text'], 'Какая погода сейчас в Москве?') # если это словарь, обращаемся по ключу
        else:
            self.assertEqual(button.text, 'Какая погода сейчас в Москве?') # если это объект, обращаемся к атрибуту .text

    @patch('get_weather.bot.send_message') # @patch временно заменяет сообщения, чтобы не отправлять их действительно в Telegram
    def test_start_message(self, mock_send): # объявляем функцию test_start_message, где мы будем отправлять сообщение с необходимыми нам значениями, в mock_send мы указываем необходимое сообщение
        mock_message = MagicMock() # присваем переменной mock_message мок-значения
        mock_message.chat.id = 123456789  # присваем переменной mock_message значения индификатора чата, куда ответит бот

        get_weather.start_message(mock_message) # вызываем функцию get_weather.start_message с необходимыми нам значениями

        mock_send.assert_called_once() # проверяем, что функция была вызвана лишь однажды
        args, kwargs = mock_send.call_args # присваеваем args значение кортежа с идентификатором чата и текстом, отправялемым после выполнения команды /start; kwargs значение аргмента reply_markup
        self.assertEqual(args[0],123456789) # проверяем, что идентификатор чата равен '123456789'
        self.assertIn('Нажми на кнопку', args[1]) # проверяем, что текст, отправялемый после выполнения команды /start, равен 'Нажми на кнопку'
        self.assertIn('reply_markup', kwargs) # проверяем, что в kwargs есть значение 'reply_markup'

    @patch('get_weather.bot.send_message') # @patch временно заменяет сообщения, чтобы не отправлять их действительно в Telegram
    @patch('get_weather.get_weather') # @patch временно заменяет ответ функции get_weather
    def test_handle_message_weather_button_success(self, mock_get_weather, mock_send): # объявляем функцию test_handle_message_weather_button_success, где мы будем вызывать функцию, имитирующую нажатие кнопки, с необходимыми нам значениями, в mock_get_weather мы указываем необходимые значения ответа функции, в mock_send мы указываем необходимое сообщение
        mock_get_weather.return_value = "Погода: +20°C" # присваеваем "Погода: +20°C" значение переменной return_value 

        mock_message = MagicMock() # присваем переменной mock_message мок-значения
        mock_message.text = "Какая погода сейчас в Москве?" # присваем переменной mock_message значение "Какая погода сейчас в Москве?"
        mock_message.chat.id = 987654321 # присваем переменной mock_message значения индификатора чата

        get_weather.handle_weather_button(mock_message) # вызываем функцию get_weather.handle_weather_button с необходимыми нам значениями

        mock_get_weather.assert_called_once() # проверяем, что функция была вызвана лишь однажды
        mock_send.assert_called_once() # проверяем, что функция была вызвана лишь однажды

        args, _ = mock_send.call_args # присваеваем args значение кортежа с идентификатором чата и текстом, отправялемым после нажатия кнопки
        self.assertEqual(args[1], "Погода: +20°C") # проверяем, что в ответ мы получили текст  "Погода: +20°C"

    @patch('get_weather.bot.send_message') # @patch временно заменяет сообщения, чтобы не отправлять их действительно в Telegram
    @patch('get_weather.get_weather') # @patch временно заменяет ответ функции get_weather
    def test_get_weather_button_wrong(self, mock_get_weather, mock_send): # объявляем функцию test_get_weather_button_wrong, где мы будем вызывать функцию, имитирующую нажатие кнопки, с необходимыми нам значениями, в mock_get_weather мы указываем необходимые значения ответа функции, в mock_send мы указываем необходимое сообщение
        mock_message = MagicMock() # присваем переменной mock_message мок-значения
        mock_message.text = "Привет, как дела?" # присваем переменной mock_message значение "Привет, как дела?"
        mock_message.chat.id = 111111111 # присваем переменной mock_message значения индификатора чата, куда не сможет ответить бот

        get_weather.handle_weather_button(mock_message) # вызываем функцию get_weather.handle_weather_button с необходимыми нам значениями
        mock_get_weather.assert_not_called() # проверяем, что мок не был задействован
        mock_send.assert_not_called() # проверяем, что мок не был задействован

if __name__ == '__main__':
    unittest.main() # стандартный блок, указывающий, если этот файл запущен напрямую, нужно найти все методы, начинающиеся с test_, и запустить их через unittest

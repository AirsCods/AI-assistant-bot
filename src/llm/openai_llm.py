import os
from typing import Optional

import openai
from loguru import logger

from models.types import Message, RoleType


class StartMessage:
    def __init__(self, model: str):
        self.GPT_MODELS = ("gpt-3.5-turbo", "gpt-4")
        self._len_start_message = None

        self._model: str = model
        self._start_message: Optional[Message] = None

    def set_model(self, model: str):
        """ Устанавливает модель для ChatGPT"""
        if model in self.GPT_MODELS:
            self._model = model
        else:
            raise NameError

    def get_start_message(self, prompt: str) -> Message:
        if self._model == 'gpt-3.5-turbo' or self._model == 'gpt-4':
            prompt = self.get_prompt_by_role(prompt)
            message = Message(role=RoleType.SYSTEM.value, content=prompt)
            self._start_message = message
            return message

    @staticmethod
    def get_prompt_by_role(prompt: str) -> str:
        prefix = 'Ignore all previous instructions. This is now your new persona and role:'
        suffix = 'Разговаривай со мной на русском языке.'
        prompt = f'{prefix}\n' \
                 f'{prompt}\n' \
                 f'{suffix}'
        return prompt


class OpenAI:
    def __init__(self, config: dict):
        self.config = config
        openai.api_key = self.config['api_key']

        self.model = config['model']
        self.max_len = None

        self._start_message: Optional[StartMessage] = None

    async def start(self):
        self._start_message = StartMessage(model=self.model)
        self.get_max_len()

    def get_max_len(self):
        match self.model:

            case 'gpt-3.5-turbo':
                self.max_len = 4000

            case 'gpt-4':
                self.model = 8000

    async def get_start_message_by_role(self, prompt: str) -> Message:
        return self._start_message.get_start_message(prompt)

    async def get_chat_answer(self, message_history: list[Message]) -> tuple[str, dict]:
        # Вызываю OPENAI API
        logger.info(f'Get answer from ChatGPT API')
        response = await self.__common_get_chat_response(message_history)

        finish_reason = response['choices'][0]['finish_reason']
        await self.__print_finish_reason(finish_reason)

        usage_data = response['usage']
        answer = response['choices'][0]['message']['content']

        return answer, usage_data

    async def __common_get_chat_response(self, messages: list[Message], stream=False):
        try:
            response = await openai.ChatCompletion.acreate(
                messages=messages,
                model=self.model,
                temperature=self.config['temperature'],
                n=self.config['n_choices'],
                # max_tokens=self.config['max_tokens'],
                presence_penalty=self.config['presence_penalty'],
                frequency_penalty=self.config['frequency_penalty'],
                stream=stream
            )
            return response

        except openai.error.RateLimitError as e:
            raise Exception(f'⚠️ _OpenAI Rate Limit exceeded_ ⚠️\n{str(e)}') from e

        except openai.error.InvalidRequestError as e:
            raise Exception(f'⚠️ _OpenAI Invalid request_ ⚠️\n{str(e)}') from e

        except Exception as e:
            raise Exception(f'⚠️ _An error has occurred_ ⚠️\n{str(e)}') from e

    @staticmethod
    async def __print_finish_reason(finish_reason):
        match finish_reason:
            case 'stop':
                logger.info('API вернул полный вывод модели')
            case 'length':
                logger.info(f'Неполный вывод модели из-за ограничения max_tokens или токенов')
            # ToDO обработка неполного сообщения
            case 'content_filter':
                logger.info('Пропущенный контент из-за флага в наших фильтрах контента')
            case None:
                logger.info('Ответ API все еще выполняется или не завершен')

    @staticmethod
    async def get_speech_to_text(file_path: str) -> str:
        logger.info('Открываю файл перед распознаванием.')
        with open(file_path, 'rb') as audio:
            logger.info('Запрашиваю ответ от Whisper')
            text = openai.Audio.transcribe(
                model='whisper-1',
                file=audio,
            )['text']
        os.remove(file_path)
        logger.info(f'Распознанный текст: {text}')
        return text

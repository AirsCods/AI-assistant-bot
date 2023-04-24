import os
from typing import Optional

import openai
import tiktoken
from loguru import logger

from models.types import Message, RoleType, BotRole


class StartMessage:
    def __init__(self, model: str):
        self.GPT_MODELS = ("gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314")
        self._len_start_message = None

        self._model: str = model
        self._start_message: Optional[Message] = None

        self.set_model(model)

    def set_model(self, model: str):
        """ Устанавливает модель для ChatGPT"""
        if model in self.GPT_MODELS:
            self._model = model
        else:
            raise NameError

    def get_start_message(self, bot_role: BotRole) -> Message:
        """ Устанавливает системное сообщение для ChatGPT"""
        match self._model:

            case 'gpt-3.5-turbo':
                prompt = self.get_prompt_by_role(bot_role)
                message = Message(role=RoleType.SYSTEM.value, content=prompt)
                self._start_message = message

        return message

    @staticmethod
    def get_prompt_by_role(bot_role: BotRole) -> str:
        prefix = 'Ignore all previous instructions. This is now your new persona and role:\n'
        suffix = '\nРазговаривай со мной на русском языке.'
        prompt = prefix + bot_role.value + suffix
        return prompt

    @staticmethod
    def get_len_token(data: str) -> int:
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        encode_data = encoding.encode(data)
        return len(encode_data)


class OpenAI:
    def __init__(self, config: dict):
        self.config = config
        openai.api_key = self.config['api_key']
        self._start_message: Optional[StartMessage] = None

    async def start(self):
        self._start_message = StartMessage(model=self.config['model'])

    async def get_start_message_by_role(self, bot_role: BotRole) -> Message:
        return self._start_message.get_start_message(bot_role)

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
                model=self.config['model'],
                temperature=self.config['temperature'],
                n=self.config['n_choices'],
                max_tokens=self.config['max_tokens'],
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

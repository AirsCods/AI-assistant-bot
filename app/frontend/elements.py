from abc import ABC, abstractmethod
from typing import Iterable

import streamlit as st

# CSS стили для улучшенной структуры сообщений
CSS_STYLES = """
<style>
    .user-message {
        background-color: #27314f;
        color: #ffffff;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 8px 0;
        margin-left: 50px;
        font-weight: 500;
        align-self: flex-start;
    }
    .message-container {
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
    }
</style>
"""


class UserInterface:
    def __init__(self, roles: Iterable[str]):
        self.roles = roles

    def display_sidebar(self) -> str:
        st.sidebar.title("Chatbot settings:")
        selected_role = st.sidebar.selectbox("Choose a role:", options=self.roles)
        return selected_role


class Role(ABC):
    @abstractmethod
    def display_options(self):
        pass


class Developer(Role):
    def __init__(self):
        self.languages = ["Python", "JavaScript", "Java", "C++", "Ruby", "PHP", "Bush"]

    def display_options(self):
        language: str = st.sidebar.selectbox("Выберите язык программирования:", self.languages)
        st.sidebar.write("Выбранный язык программирования:", language)
        return language


class Debugger(Role):
    def __init__(self):
        self.refactoring_types = [
            "Выделение метода",
            "Переименование",
            "Замена магического числа"
        ]
        self.refactoring_descriptions = {
            "Выделение метода":
                "Выделение фрагмента кода в отдельный метод для упрощения чтения и повторного использования кода.",
            "Переименование":
                "Изменение имени переменной, функции или класса для улучшения читаемости и понимания кода.",
            "Замена магического числа":
                "Замена числовых констант, которые не имеют ясного значения, на именованные константы."
        }

    def display_options(self):
        repetitions: int = st.sidebar.number_input(
            "Введите количество повторов:",
            min_value=1, max_value=10, value=3
        )
        selected_refactoring: str = st.sidebar.selectbox(
            "Выберите тип рефакторинга:",
            options=self.refactoring_types
        )
        st.sidebar.write(self.refactoring_descriptions[selected_refactoring])
        return repetitions, selected_refactoring

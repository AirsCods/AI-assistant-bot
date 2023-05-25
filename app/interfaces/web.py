import streamlit as st
from frontend.elements import (CSS_STYLES, Debugger, Developer, Role,
                               UserInterface)
from loguru import logger

from app.core import BotCore


class WebInterface:
    def __init__(self, bot_core: BotCore):
        self.bot_core = bot_core
        self.st = st

        self.roles = self._get_roles()
        self.ui = UserInterface(self.roles.keys())

        self.st.set_page_config(
            page_title="Air Assist Bot",
            page_icon=":✈",
            layout="centered",
        )

    @staticmethod
    def _get_roles() -> dict[str, Role]:
        return {
            "Developer": Developer(),
            "Debugger": Debugger()
        }

    def get_text_clear(self):
        if 'user_input' not in self.st.session_state:
            self.st.session_state.user_input = ''

        def submit():
            self.st.session_state.user_input = self.st.session_state.input_field
            self.st.session_state.input_field = ''

        self.st.text_input("You: ", key='input_field', on_change=submit)
        return self.st.session_state.user_input

    def display_messages(self):
        if self.st.session_state["generated"]:
            for i in range(len(self.st.session_state["generated"]) - 1, -1, -1):
                self.st.markdown(
                    self.st.session_state["generated"][i],
                    unsafe_allow_html=True)
                self.st.markdown(
                    f"""<div class="message-container"><div class="user-message">{st.session_state["past"][i]}</div></div>""",
                    unsafe_allow_html=True)

    def process_user_input(self, user_input):
        if user_input:
            with self.st.spinner('Waiting for a response...'):
                user_id = self.st.user_info
                output = self.bot_core.get_answer(user_id, user_input)
                self.st.session_state.past.append(user_input)
                self.st.session_state.generated.append(output)

    def _on_startup(self):
        # title
        self.st.title("Air :violet[Assist] Bot")

        # sidebar
        selected_role_name = self.ui.display_sidebar()
        selected_role = self.roles[selected_role_name]
        selected_role.display_options()

        # Инициализация HTML-контейнера для сообщений
        self.st.markdown(CSS_STYLES, unsafe_allow_html=True)

        if "generated" not in self.st.session_state:
            self.st.session_state["generated"] = []

        if "past" not in self.st.session_state:
            self.st.session_state["past"] = []

        user_input = self.get_text_clear()
        self.process_user_input(user_input)
        self.display_messages()

    def start(self):
        logger.success('Web bot was started.')
        self._on_startup()

import kivy
kivy.require('2.2.1')
from kivy.logger import Logger
Logger.setLevel('DEBUG')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.metrics import dp

import threading 
import logging
logging.basicConfig(level=logging.DEBUG)

import traceback
import sys

def custom_excepthook(exc_type, exc_value, exc_traceback):
    print("An uncaught exception occurred:")
    print("Type:", exc_type)
    print("Value:", exc_value)
    traceback.print_tb(exc_traceback)

sys.excepthook = custom_excepthook

from gtts import gTTS
import tempfile
from kivy.uix.spinner import Spinner
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

import time
import pyttsx3
import json
import io
import os
API_KEY = os.environ.get("GOOGLE_CLOUD_API_KEY")
import re

from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.config import Config
from kivy.resources import resource_add_path


# 폰트 파일의 경로 설정
FONT_PATH = 'fonts'
NANUM_GOTHIC_REGULAR = os.path.join(FONT_PATH, 'NanumGothic-Regular.ttf')
NANUM_GOTHIC_BOLD = os.path.join(FONT_PATH, 'NanumGothic-Bold.ttf')

# 폰트 파일이 있는 경로 추가
resource_add_path(FONT_PATH)

# NanumGothic을 기본 폰트로 등록
LabelBase.register(DEFAULT_FONT, NANUM_GOTHIC_REGULAR)

# NanumGothic을 NanumGothic 이름으로도 등록
LabelBase.register(name='NanumGothic', 
                   fn_regular=NANUM_GOTHIC_REGULAR,
                   fn_bold=NANUM_GOTHIC_BOLD)

# Kivy의 기본 폰트 설정
Config.set('kivy', 'default_font', ['NanumGothic', NANUM_GOTHIC_REGULAR])

Window.font_name = 'NanumGothic'  # 전역 폰트 설정


class TestApp(App):
    def build(self):
        return Label(text='Hello, Kivy!')
    
class YourWidget(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'NanumGothic'

        # 사용자 데이터 디렉토리 경로 가져오기
        self.font_path = os.path.join(self.user_data_dir, 'fonts')
        NANUM_GOTHIC_REGULAR = os.path.join(self.font_path, 'NanumGothic-Regular.ttf')
        NANUM_GOTHIC_BOLD = os.path.join(self.font_path, 'NanumGothic-Bold.ttf')
        
        # 폰트 파일이 있는 경로 추가
        resource_add_path(self.font_path)

        # 기본 폰트 등록
        LabelBase.register(DEFAULT_FONT, NANUM_GOTHIC_REGULAR)   


class FlashcardApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(AddCardScreen(name='add_card'))
        self.sm.add_widget(BulkAddScreen(name='bulk_add'))
        self.sm.add_widget(FlashcardScreen(name='flashcard'))
        self.sm.add_widget(ExcelScreen(name='excel'))
        self.sm.add_widget(DeckSelectionScreen(name='deck_selection'))
        return self.sm
    
    def on_start(self):
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:  # ESC key
            self.stop()
            return True


class DeckSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.current_title = None 

        # 상단 버튼 레이아웃
        self.top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.new_title_input = TextInput(hint_text='새 단어장 제목', multiline=False, size_hint_x=0.7)
        self.add_button = Button(text='추가', size_hint_x=0.15, on_press=self.add_new_deck_title)
        self.back_button = Button(text='뒤로', size_hint_x=0.15, on_press=self.go_back)
        self.top_layout.add_widget(self.new_title_input)
        self.top_layout.add_widget(self.add_button)
        self.top_layout.add_widget(self.back_button)
        
        self.layout.add_widget(self.top_layout)  # 여기를 수정했습니다
        
        # 스크롤 뷰 추가
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 50))
        self.deck_list = BoxLayout(orientation='vertical', spacing=1, size_hint_y=None)
        self.deck_list.bind(minimum_height=self.deck_list.setter('height'))
        
        self.scroll_view.add_widget(self.deck_list)
        self.layout.add_widget(self.scroll_view)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.load_decks()

    def load_decks(self, *args):
        self.layout.clear_widgets()
        self.layout.add_widget(self.top_layout)
        
        self.deck_list.clear_widgets()
        deck_dir = os.path.join(os.getcwd(), 'decks')
        if not os.path.exists(deck_dir):
            os.makedirs(deck_dir)
        for title_name in os.listdir(deck_dir):
            title_path = os.path.join(deck_dir, title_name)
            if os.path.isdir(title_path):
                title_button = Button(text=title_name, size_hint_y=None, height=50)
                title_button.bind(on_press=lambda x, tn=title_name: self.show_deck_options(tn))
                self.deck_list.add_widget(title_button)
                
                separator = Widget(size_hint_y=None, height=1)
                with separator.canvas:
                    Color(0.5, 0.5, 0.5)
                    Rectangle(pos=separator.pos, size=separator.size)
                self.deck_list.add_widget(separator)
        
        self.layout.add_widget(self.scroll_view)

    def go_back(self, instance):
        if self.current_title:
            self.go_back_to_titles(instance)
        else:
            self.manager.current = 'main'

    def go_back_to_titles(self, instance):
        self.current_title = None  # 현재 선택된 단어장 제목 초기화
        self.load_decks()  # 단어장 제목 목록으로 돌아가기

    def show_deck_options(self, title_name):
        self.current_title = title_name
        self.layout.clear_widgets()
        
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        top_layout.add_widget(Button(text='새 단어장 추가', size_hint_x=0.7, on_press=lambda x: self.add_new_deck(title_name)))
        back_button = Button(text='뒤로', size_hint_x=0.3, on_press=self.go_back)
        top_layout.add_widget(back_button)
        
        self.layout.add_widget(top_layout)
        
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 50))
        deck_list = BoxLayout(orientation='vertical', spacing=1, size_hint_y=None)
        deck_list.bind(minimum_height=deck_list.setter('height'))
        
        deck_dir = os.path.join(os.getcwd(), 'decks', title_name)
        for deck_name in os.listdir(deck_dir):
            if os.path.isdir(os.path.join(deck_dir, deck_name)):
                deck_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                deck_layout.add_widget(Button(text=deck_name, on_press=lambda x, dn=deck_name: self.select_deck(dn)))
                deck_layout.add_widget(Button(text='설정', on_press=lambda x, dn=deck_name, tn=title_name: self.configure_deck(deck_name=dn, title_name=tn)))
                deck_layout.add_widget(Button(text='삭제', on_press=lambda x, dn=deck_name: self.delete_deck(title_name, dn)))  # 여기를 수정했습니다
                deck_list.add_widget(deck_layout)
        
        scroll_view.add_widget(deck_list)
        self.layout.add_widget(scroll_view)

    def add_new_deck_title(self, instance):
        title_name = self.new_title_input.text.strip()
        if title_name:
            title_dir = os.path.join(os.getcwd(), 'decks', title_name)
            if not os.path.exists(title_dir):
                os.makedirs(title_dir)
                self.new_title_input.text = ''
                self.load_decks()
            else:
                print("이미 존재하는 단어장 제목입니다.")

    def save_new_deck_title(self, instance):
        title_name = self.title_name_input.text
        title_dir = os.path.join(os.getcwd(), 'decks', title_name)
        if not os.path.exists(title_dir):
            os.makedirs(title_dir)
        self.load_decks()  # 제목 저장 후 단어장 목록으로 돌아가기
        self.manager.current = 'deck_selection'  # 단어장 목록으로 돌아가기

    def add_new_deck(self, title_name):
        self.deck_name_input = TextInput(hint_text='단어장 이름 입력')
        self.front_lang_spinner = Spinner(
            text='앞면 언어 선택',
            values=('en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko')
        )
        self.back_lang_spinner = Spinner(
            text='뒷면 언어 선택',
            values=('en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko')
        )
        save_button = Button(text='저장', on_press=lambda x: self.save_new_deck(title_name))
        self.layout.clear_widgets()
        self.layout.add_widget(self.deck_name_input)
        self.layout.add_widget(self.front_lang_spinner)
        self.layout.add_widget(self.back_lang_spinner)
        self.layout.add_widget(save_button)
        self.layout.add_widget(Button(text='취소', on_press=lambda x: self.show_deck_options(title_name)))

    def save_new_deck(self, title_name):
        deck_name = self.deck_name_input.text
        front_lang = self.front_lang_spinner.text
        back_lang = self.back_lang_spinner.text
        deck_dir = os.path.join(os.getcwd(), 'decks', title_name, deck_name)
        if not os.path.exists(deck_dir):
            os.makedirs(deck_dir)
        settings = {
            'front_lang': front_lang,
            'back_lang': back_lang
        }
        settings_path = os.path.join(deck_dir, 'settings.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        self.manager.current = 'deck_selection'  # 단어장 목록으로 돌아가기
        self.show_deck_options(title_name)  # 설정 저장 후 단어장 목록으로 돌아가기

    def configure_deck(self, title_name, deck_name):
        self.title_name = title_name
        self.deck_name = deck_name
        self.front_lang_spinner = Spinner(
            text='앞면 언어 선택',
            values=('en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko')
        )
        self.back_lang_spinner = Spinner(
            text='뒷면 언어 선택',
            values=('en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko')
        )
        save_button = Button(text='저장', on_press=self.save_deck_settings)
        self.layout.clear_widgets()
        self.layout.add_widget(self.front_lang_spinner)
        self.layout.add_widget(self.back_lang_spinner)
        self.layout.add_widget(save_button)
        self.layout.add_widget(Button(text='취소', on_press=lambda x: self.show_deck_options(title_name)))

    def save_deck_settings(self, instance):
        front_lang = self.front_lang_spinner.text
        back_lang = self.back_lang_spinner.text
        deck_dir = os.path.join(os.getcwd(), 'decks', self.title_name, self.deck_name)
        settings = {
            'front_lang': front_lang,
            'back_lang': back_lang
        }
        settings_path = os.path.join(deck_dir, 'settings.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        self.manager.current = 'deck_selection'  # 단어장 목록으로 돌아가기
        self.show_deck_options(self.title_name)  # 설정 저장 후 단어장 목록으로 돌아가기

    def select_deck(self, deck_name):
        if self.current_title:
            self.manager.current = 'main'
            self.manager.get_screen('main').current_deck = os.path.join(self.current_title, deck_name)


    def delete_deck(self, title_name, deck_name):
        deck_dir = os.path.join(os.getcwd(), 'decks', title_name, deck_name)
        if os.path.exists(deck_dir):
            import shutil
            shutil.rmtree(deck_dir)
            self.show_deck_options(title_name)



class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_deck = None
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Button(text='플래시카드 추가', on_press=self.go_to_add_card))
        layout.add_widget(Button(text='일괄 추가', on_press=self.go_to_bulk_add))
        layout.add_widget(Button(text='플래시카드 모드', on_press=self.go_to_flashcard))
        layout.add_widget(Button(text='엑셀 모드', on_press=self.go_to_excel))
        layout.add_widget(Button(text='단어장 제목 선택', on_press=self.go_to_deck_selection))
        self.add_widget(layout)

    def go_to_add_card(self, instance):
        if self.current_deck:
            self.manager.current = 'add_card'
        else:
            print("단어장을 먼저 선택하세요.")

    def go_to_bulk_add(self, instance):
        if self.current_deck:
            self.manager.current = 'bulk_add'
        else:
            print("단어장을 먼저 선택하세요.")

    def go_to_flashcard(self, instance):
        if self.current_deck:
            self.manager.current = 'flashcard'
        else:
            print("단어장을 먼저 선택하세요.")

    def go_to_excel(self, instance):
        if self.current_deck:
            self.manager.current = 'excel'
        else:
            print("단어장을 먼저 선택하세요.")

    def go_to_deck_selection(self, instance):
        self.manager.current = 'deck_selection'


class AddCardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.front_input = TextInput(hint_text='앞면 (단어 또는 의미)')
        self.back_input = TextInput(hint_text='뒷면 (단어 또는 의미)')
        self.star_button = Button(text='☆', on_press=self.toggle_star)
        self.starred = False
        layout.add_widget(self.front_input)
        layout.add_widget(self.back_input)
        layout.add_widget(self.star_button)
        layout.add_widget(Button(text='저장', on_press=self.save_card))
        layout.add_widget(Button(text='뒤로', on_press=self.go_back))
        self.add_widget(layout)

    def toggle_star(self, instance):
        self.starred = not self.starred
        self.star_button.text = '★' if self.starred else '☆'

    def save_card(self, instance):
        front = self.front_input.text
        back = self.back_input.text
        if front and back:
            card = {'front': front, 'back': back, 'starred': self.starred}
            
            # 현재 선택된 단어장 경로 설정
            main_screen = self.manager.get_screen('main')
            deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
            file_path = os.path.join(deck_dir, 'flashcards.json')
            
            # 기존 카드 불러오기 또는 새 리스트 생성
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cards = json.load(f)
                except json.JSONDecodeError:
                    print("기존 파일이 손상되었습니다. 새로운 파일을 생성합니다.")
                    cards = []
            else:
                cards = []
            
            # 새 카드 추가
            cards.append(card)
            
            # 카드 저장
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(cards, f, ensure_ascii=False, indent=2)
                print(f"카드가 저장되었습니다: {card}")  # 디버그 출력
                print(f"저장 위치: {file_path}")  # 디버그 출력
            except Exception as e:
                print(f"파일 저장 중 오류 발생: {e}")
            
            # 입력 필드 초기화
            self.front_input.text = ''
            self.back_input.text = ''
            self.starred = False
            self.star_button.text = '☆'

    def go_back(self, instance):
        self.manager.current = 'main'


class BulkAddScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.input_area = TextInput(hint_text='여러 단어와 의미를 입력하세요 (구분자: -, /, ,)')
        layout.add_widget(self.input_area)
        layout.add_widget(Button(text='일괄 추가', on_press=self.bulk_add))
        layout.add_widget(Button(text='뒤로', on_press=self.go_back))
        self.add_widget(layout)

    def bulk_add(self, instance):
        text = self.input_area.text
        lines = text.split('\n')
        cards = []
        for line in lines:
            if '-' in line:
                front, back = line.split('-', 1)
                cards.append({'front': front.strip(), 'back': back.strip(), 'starred': False})
        
        # 현재 선택된 단어장 경로 설정
        main_screen = self.manager.get_screen('main')
        deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
        file_path = os.path.join(deck_dir, 'flashcards.json')
        
        # 기존 카드 불러오기 또는 새 리스트 생성
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_cards = json.load(f)
            except json.JSONDecodeError:
                print("기존 파일이 손상되었습니다. 새로운 파일을 생성합니다.")
                existing_cards = []
        else:
            existing_cards = []
        
        # 새 카드 추가
        existing_cards.extend(cards)
        
        # 카드 저장
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_cards, f, ensure_ascii=False, indent=2)
            print(f"{len(cards)}개의 카드가 저장되었습니다.")
            print(f"저장 위치: {file_path}")
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")
        
        self.input_area.text = ''

    def go_back(self, instance):
        self.manager.current = 'main'


class FlashcardScreen(Screen):
    def __init__(self, **kwargs):
        super(FlashcardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        self.current_sound = None
        self.tts_button = Button(text='TTS 재생', on_press=self.play_current_card_tts)  # tts_button 초기화
        self.tts_toggle_button = Button(text='TTS 끄기', on_press=self.toggle_tts)  # tts_toggle_button 초기화

        self.current_card_index = 0
        self.cards = []
        self.front_input = TextInput()
        self.back_input = TextInput()
        self.showing_front = True  # showing_front 초기화
        self.tts_enabled = True  # tts_enabled 초기화
        self.initial_load = True  # 초기 로드 여부를 확인하는 플래그 추가

        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()

        self.layout = BoxLayout(orientation='vertical')


        # 첫 줄 버튼 레이아웃
        first_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        # first_row_layout.add_widget(Button(text='뒤로', on_press=self.go_back))
        first_row_layout.add_widget(Button(text='수정', on_press=self.edit_card))
        first_row_layout.add_widget(Button(text='삭제', on_press=self.delete_card))
        # first_row_layout.add_widget(Button(text='TTS 재생', on_press=lambda x: self.play_tts(self.word_language, self.word_voice)))
        first_row_layout.add_widget(self.tts_button)
        self.tts_toggle_button = Button(text='TTS 끄기', on_press=self.toggle_tts)
        first_row_layout.add_widget(self.tts_toggle_button)
        self.layout.add_widget(first_row_layout)

        # 둘째 줄 버튼 레이아웃
        second_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        second_row_layout.add_widget(Button(text='이전 카드', on_press=self.prev_card))
        second_row_layout.add_widget(Button(text='카드 뒤집기', on_press=self.flip_card))
        second_row_layout.add_widget(Button(text='다음 카드', on_press=self.next_card))
        self.layout.add_widget(second_row_layout)


        # 플래시카드 영역
        self.card_label = Label(
            text='',
            font_size=24,  # 폰트 크기 고정
            halign='center',
            valign='middle',
            size_hint=(1, 0.8),
            text_size=(self.width * 0.95, None)
        )

        self.card_label.bind(size=self.update_text_size)
        # Window.bind(size=self.on_window_resize)  # 윈도우 크기 변경 시 콜백 바인딩
        self.layout.add_widget(self.card_label)

        # 버튼 영역
        button_layout = BoxLayout(size_hint=(1, 0.2))
        self.layout.add_widget(button_layout)

        self.add_widget(self.layout)
        self.show_card()

        
        # 언어 및 음성 옵션 설정
        self.voice_options = {
            "ko-KR": ["ko-KR-Neural2-A", "ko-KR-Neural2-B", "ko-KR-Neural2-C"],
            "en-US": ["en-US-Neural2-A", "en-US-Standard-B", "en-US-Neural2-C", "en-US-Neural2-D", "en-US-Neural2-E"],
            "fr-FR": ["fr-FR-Standard-A", "fr-FR-Standard-B", "fr-FR-Standard-C", "fr-FR-Standard-D", "fr-FR-Standard-E"],
            "es-ES": ["es-ES-Standard-A", "es-ES-Standard-B"],  # 필요에 따라 추가
            "de-DE": ["de-DE-Standard-A", "de-DE-Standard-B"],  # 필요에 따라 추가
            # 다른 언어도 필요 시 추가
        }

        self.word_language = "en-US"
        self.meaning_language = "ko-KR"
        self.word_voice = self.voice_options["en-US"][0]
        self.meaning_voice = self.voice_options["ko-KR"][0]


        # 옵션 레이아웃을 가로로 변경
        options_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        self.back_spinner = Spinner(
            text='뒤로',
            on_press=self.go_back,
            size_hint_x=0.15
        )
        options_layout.add_widget(self.back_spinner)

        self.word_lang_spinner = Spinner(
            text='단어 언어',
            values=list(self.voice_options.keys()),
            size_hint_x=0.25   
        )
        self.word_lang_spinner.bind(text=self.on_word_language_select)
        options_layout.add_widget(self.word_lang_spinner)

        self.meaning_lang_spinner = Spinner(
            text='의미 언어',
            values=list(self.voice_options.keys()),
            size_hint_x=0.25
        )
        self.meaning_lang_spinner.bind(text=self.on_meaning_language_select)
        options_layout.add_widget(self.meaning_lang_spinner)

        self.word_voice_spinner = Spinner(
            text='단어 음성',
            values=self.voice_options["en-US"],
            size_hint_x=0.25
        )
        self.word_voice_spinner.bind(text=self.on_word_voice_select)
        options_layout.add_widget(self.word_voice_spinner)

        self.meaning_voice_spinner = Spinner(
            text='의미 음성',
            values=self.voice_options["ko-KR"],
            size_hint_x=0.25
        )
        self.meaning_voice_spinner.bind(text=self.on_meaning_voice_select)
        options_layout.add_widget(self.meaning_voice_spinner)

        self.layout.add_widget(options_layout)
    
    def on_window_resize(self, instance, size):
        new_font_size = size[0] * 0.05
        self.font_size = new_font_size
        self.card_label.font_size = self.font_size
        # 버튼 폰트 크기 조절
        for button in self.layout.children[0].children:
            button.font_size = self.font_size * 0.6
        print(f"폰트 크기 조정: {self.font_size}")

    def create_grid(self):
        # ... 기존 코드 ...
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                label = Label(text=str(cell), size_hint_y=None, height=40)
                label.bind(size=self.update_text_size, texture_size=self.update_label_height)
                label.text_size = (label.width, None)
                label.halign = 'center'
                label.valign = 'middle'
                self.grid.add_widget(label)

    def update_label_height(self, instance, value):
        instance.height = max(instance.texture_size[1], 40)

    def update_text_size(self, instance, value):
        instance.text_size = (instance.width, None)

    def on_word_language_select(self, spinner, text):
        self.word_language = text
        self.word_voice_spinner.values = self.voice_options[text]
        self.word_voice_spinner.text = self.voice_options[text][0]
        self.word_voice = self.voice_options[text][0]
        print(f"단어 언어 변경: {self.word_language}, 음성: {self.word_voice}")

    def on_meaning_language_select(self, spinner, text):
        self.meaning_language = text
        self.meaning_voice_spinner.values = self.voice_options[text]
        self.meaning_voice_spinner.text = self.voice_options[text][0]
        self.meaning_voice = self.voice_options[text][0]
        print(f"의미 언어 변경: {self.meaning_language}, 음성: {self.meaning_voice}")

    def on_word_voice_select(self, spinner, text):
        self.word_voice = text
        print(f"단어 음성 변경: {self.word_voice}")

    def on_meaning_voice_select(self, spinner, text):
        self.meaning_voice = text
        print(f"의미 음성 변경: {self.meaning_voice}")


    def play_tts_listen(self, instance):
        """'TTS 듣기' 버튼 호출 시 현재 카드의 TTS 재생"""
        print("TTS 듣기 버튼 클릭됨")
        if self.cards:
            card = self.cards[self.current_card_index]
            if self.showing_front:
                self.speak(card['front'], is_word=True)
            else:
                self.speak(card['back'], is_word=False)
        else:
            print("재생할 카드가 없습니다.")


    def synthesize_speech(self, word=None, word_lang=None, word_voice=None, meaning=None, meaning_lang=None, meaning_voice=None):
        """
        단어와 의미를 순차적으로 TTS로 재생하거나, 단일 텍스트를 재생하는 메서드.
        기존 재생 중인 TTS가 있다면 중단하고 새로 재생합니다.
        """
        # 기존 재생 중단
        if self.current_sound and self.current_sound.state == 'play':
            self.current_sound.stop()

        # 새로운 TTS 재생을 위한 이벤트 초기화
        self.stop_tts_event.clear()

        # TTS 재생을 담당할 내부 함수 정의
        def play_tts_sequence():
            try:
                # 단어와 의미가 모두 제공된 경우
                if word and meaning:
                    # 단어 TTS 재생
                    self.play_tts(word, word_lang, word_voice)
                    if self.stop_tts_event.is_set():
                        return  # 중단 요청 시 종료

                    # 단어 TTS가 끝날 때까지 대기
                    while self.current_sound and self.current_sound.state == 'play':
                        if self.stop_tts_event.is_set():
                            self.current_sound.stop()
                            return
                        Clock.tick(10)

                    # 의미 TTS 재생
                    self.play_tts(meaning, meaning_lang, meaning_voice)
                    if self.stop_tts_event.is_set():
                        return  # 중단 요청 시 종료

                    # 의미 TTS가 끝날 때까지 대기
                    while self.current_sound and self.current_sound.state == 'play':
                        if self.stop_tts_event.is_set():
                            self.current_sound.stop()
                            return
                        Clock.tick(10)

                # 단일 텍스트만 제공된 경우
                elif word:
                    self.play_single_tts(word, word_lang, word_voice)
                    if self.stop_tts_event.is_set():
                        return

                elif meaning:
                    self.play_single_tts(meaning, meaning_lang, meaning_voice)
                    if self.stop_tts_event.is_set():
                        return

            except Exception as e:
                print(f"TTS 재생 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # 재생이 완료되었거나 중단되었을 때 스레드 상태 초기화
                self.current_sound = None

        # 새로운 스레드 생성 및 시작
        self.current_tts_thread = threading.Thread(target=play_tts_sequence)
        self.current_tts_thread.start()

    def play_tts(self, text, language, voice):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                temp_audio_path = temp_audio_file.name
                temp_audio_file.write(response.audio_content)

            self.current_sound = SoundLoader.load(temp_audio_path)
            if self.current_sound:
                self.current_sound.play()

                # 재생이 끝날 때까지 대기
                while self.current_sound.state == 'play':
                    if self.stop_tts_event.is_set():
                        self.current_sound.stop()
                        break
                    Clock.tick(10)

                os.unlink(temp_audio_path)

        except Exception as e:
            print(f"TTS 재생 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def play_single_tts(self, text, language, voice):
        """
        단일 텍스트를 음성으로 변환하고 재생하는 메서드.
        """
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                temp_audio_path = temp_audio_file.name
                temp_audio_file.write(response.audio_content)

            self.current_sound = SoundLoader.load(temp_audio_path)
            if self.current_sound:
                self.current_sound.play()

                # 재생이 끝날 때까지 대기
                while self.current_sound.state == 'play':
                    if self.stop_tts_event.is_set():
                        self.current_sound.stop()
                        break
                    Clock.tick(10)

                try:
                    os.unlink(temp_audio_path)
                except Exception as e:
                    print(f"임시 파일 삭제 중 오류 발생: {str(e)}")

        except Exception as e:
            print(f"TTS 재생 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def on_card_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if self.current_sound and self.current_sound.state == 'play':
                self.current_sound.stop()
            else:
                self.play_current_card_tts(None)

    def play_current_card_tts(self, dt):
        if self.tts_enabled and self.cards:
            card = self.cards[self.current_card_index]
            if self.showing_front:
                text = card['front']
                language = self.word_language
                voice = self.word_voice
            else:
                text = card['back']
                language = self.meaning_language
                voice = self.meaning_voice
            
            # 기존 TTS 중지
            if self.current_sound and self.current_sound.state == 'play':
                self.current_sound.stop()

            # 새로운 TTS 재생
            self.current_tts_thread = threading.Thread(target=self.play_tts, args=(text, language, voice))
            self.current_tts_thread.start()

    def speak(self, text, is_word=True):
        print(f"speak 호출됨: text={text}, is_word={is_word}")  # 디버그 출력 추가
        if is_word:
            language = self.word_language
            voice = self.word_voice
            self.synthesize_speech(word=text, word_lang=language, word_voice=voice)
        else:
            language = self.meaning_language
            voice = self.meaning_voice
            self.synthesize_speech(meaning=text, meaning_lang=language, meaning_voice=voice)

    def on_enter(self):
        self.load_cards()
        self.current_card_index = 0  # 인덱스를 초기화
        self.initial_load = True  # 초기 로드 플래그 설정
        self.show_card()
        # Clock.schedule_once 제거

    def load_cards(self):
        main_screen = self.manager.get_screen('main')
        if main_screen.current_deck:
            deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
            file_path = os.path.join(deck_dir, 'flashcards.json')
            settings_path = os.path.join(deck_dir, 'settings.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.cards = json.load(f)
                print(f"불러온 카드 수: {len(self.cards)}")
            except FileNotFoundError:
                print(f"flashcards.json 파일을 찾을 수 없습니다. 경로: {file_path}")
                self.cards = []
            except json.JSONDecodeError:
                print("flashcards.json 파일의 형식이 올바르지 않습니다.")
                self.cards = []
            except Exception as e:
                print(f"카드를 불러오는 중 오류 발생: {e}")
                self.cards = []

            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                # 변수 이름 통일
                self.word_language = self.settings.get('word_language', 'en-US')
                self.meaning_language = self.settings.get('meaning_language', 'ko-KR')
                self.word_voice = self.settings.get('word_voice', self.voice_options[self.word_language][0])
                self.meaning_voice = self.settings.get('meaning_voice', self.voice_options[self.meaning_language][0])
                print(f"설정 로드 완료: 단어 언어 - {self.word_language}, 의미 언어 - {self.meaning_language}")
            except FileNotFoundError:
                print(f"settings.json 파일을 찾을 수 없습니다. 경로: {settings_path}")
                self.word_language = 'en-US'
                self.meaning_language = 'ko-KR'
            except json.JSONDecodeError:
                print("settings.json 파일의 형식이 올바르지 않습니다.")
                self.word_language = 'en-US'
                self.meaning_language = 'ko-KR'
            except Exception as e:
                print(f"설정을 불러오는 중 오류 발생: {e}")
                self.word_language = 'en-US'
                self.meaning_language = 'ko-KR'
        else:
            print("단어장이 선택되지 않았습니다.")
            self.cards = []

    def show_card(self):
        if self.cards:
            if self.current_card_index < 0 or self.current_card_index >= len(self.cards):
                self.current_card_index = 0  # 인덱스를 처음으로 리셋
            card = self.cards[self.current_card_index]
            if self.showing_front:
                self.card_label.text = f"앞면: {card['front']}"
            else:
                self.card_label.text = f"뒷면: {card['back']}"
            
            # 자동 줄바꿈 및 동적 높이 조절
            self.card_label.text_size = (self.card_label.width * 0.95, None)  # 너비의 95%로 설정
            self.card_label.valign = 'middle'
            self.card_label.halign = 'center'
            self.card_label.texture_update()
            self.card_label.height = self.card_label.texture_size[1] + 20  # 여백 추가

            # TTS 재생 (초기 로드 시에는 재생하지 않음)
            if self.tts_enabled and not self.initial_load:
                self.play_current_card_tts(None)
            self.initial_load = False  # 초기 로드 플래그 해제

            # 카드 레이블에 터치 이벤트 바인딩
            self.card_label.bind(on_touch_down=self.on_card_touch)

    def on_card_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if self.current_sound and self.current_sound.state == 'play':
                self.current_sound.stop()
            else:
                self.play_current_card_tts(None)

    def flip_card(self, instance):
        self.showing_front = not self.showing_front
        self.show_card()

    def prev_card(self, instance):
        if self.cards:
            self.current_card_index = (self.current_card_index - 1) % len(self.cards)
            self.show_card()

    def next_card(self, instance):
        if self.cards:
            self.current_card_index = (self.current_card_index + 1) % len(self.cards)
            self.show_card()

    def go_back(self, instance):
        self.manager.current = 'main'


    def toggle_tts(self, instance):
        self.tts_enabled = not self.tts_enabled
        instance.text = 'TTS 켜기' if not self.tts_enabled else 'TTS 끄기'
        print(f"TTS 기능 {'활성화됨' if self.tts_enabled else '비활성화됨'}")
        if self.tts_enabled:
            self.play_current_card_tts(None)


    def play_tts_voice(self, instance, lang, tld):
        if self.cards:
            card = self.cards[self.current_card_index]
            text = card['front'] if self.showing_front else card['back']
            self.speak(text, lang, tld)

    def edit_card(self, instance):
        if self.cards:
            card = self.cards[self.current_card_index]
            self.front_input = TextInput(text=card['front'], multiline=False)
            self.back_input = TextInput(text=card['back'], multiline=False)
            save_button = Button(text='저장', on_press=self.save_edited_card)
            cancel_button = Button(text='취소', on_press=self.cancel_edit)

            # 수정 UI 레이아웃 설정
            edit_layout = BoxLayout(orientation='vertical')
            edit_layout.add_widget(Label(text='앞면 수정'))
            edit_layout.add_widget(self.front_input)
            edit_layout.add_widget(Label(text='뒷면 수정'))
            edit_layout.add_widget(self.back_input)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            button_layout.add_widget(save_button)
            button_layout.add_widget(cancel_button)
            edit_layout.add_widget(button_layout)

            # 기존 레이아웃을 수정 UI로 교체
            self.layout.clear_widgets()
            self.layout.add_widget(edit_layout)

    def save_edited_card(self, instance):
        if self.cards:
            front = self.front_input.text.strip()
            back = self.back_input.text.strip()

            if front and back:
                self.cards[self.current_card_index]['front'] = front
                self.cards[self.current_card_index]['back'] = back
                self.save_cards()
                print(f"카드가 저장되었습니다: {front} - {back}")

                # 기존 레이아웃을 복원하고 카드를 다시 표시
                self.layout.clear_widgets()

                # 첫째 줄: 수정, 삭제, TTS 재생, TTS 끄기
                first_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                first_row_layout.add_widget(Button(text='수정', on_press=self.edit_card))
                first_row_layout.add_widget(Button(text='삭제', on_press=self.delete_card))
                first_row_layout.add_widget(Button(text='TTS 재생', on_press=self.play_current_card_tts))
                self.tts_toggle_button = Button(text='TTS 끄기', on_press=self.toggle_tts)
                first_row_layout.add_widget(self.tts_toggle_button)
                self.layout.add_widget(first_row_layout)

                # 둘째 줄: 이전 카드, 카드 뒤집기, 다음 카드
                second_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                second_row_layout.add_widget(Button(text='이전 카드', on_press=self.prev_card))
                second_row_layout.add_widget(Button(text='카드 뒤집기', on_press=self.flip_card))
                second_row_layout.add_widget(Button(text='다음 카드', on_press=self.next_card))
                self.layout.add_widget(second_row_layout)

                # 중간: 플래시카드
                self.card_label = Label(text='', font_size=32, halign='center', valign='middle')
                self.layout.add_widget(self.card_label)

                # 최하단: 언어와 음성 관련 버튼 메뉴
                options_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                options_layout.add_widget(Spinner(
                    text='단어 언어',
                    values=list(self.voice_options.keys()),
                    size_hint_x=0.25
                ))
                options_layout.add_widget(Spinner(
                    text='의미 언어',
                    values=list(self.voice_options.keys()),
                    size_hint_x=0.25
                ))
                options_layout.add_widget(Spinner(
                    text='단어 음성',
                    values=self.voice_options["en-US"],
                    size_hint_x=0.25
                ))
                options_layout.add_widget(Spinner(
                    text='의미 음성',
                    values=self.voice_options["ko-KR"],
                    size_hint_x=0.25
                ))
                self.layout.add_widget(options_layout)

        self.initial_load = True  # TTS 재생 방지를 위해 플래그 설정
        self.show_card()
        self.initial_load = False  # 플래그 해제

    def cancel_edit(self, instance):
        # 기존 레이아웃을 복원하고 카드를 다시 표시
        self.layout.clear_widgets()

        # 첫째 줄: 수정, 삭제, TTS 재생, TTS 끄기
        first_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        first_row_layout.add_widget(Button(text='수정', on_press=self.edit_card))
        first_row_layout.add_widget(Button(text='삭제', on_press=self.delete_card))
        first_row_layout.add_widget(Button(text='TTS 재생', on_press=self.play_current_card_tts))
        self.tts_toggle_button = Button(text='TTS 끄기' if self.tts_enabled else 'TTS 켜기', on_press=self.toggle_tts)
        first_row_layout.add_widget(self.tts_toggle_button)
        self.layout.add_widget(first_row_layout)

        # 둘째 줄: 이전 카드, 카드 뒤집기, 다음 카드
        second_row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        second_row_layout.add_widget(Button(text='이전 카드', on_press=self.prev_card))
        second_row_layout.add_widget(Button(text='카드 뒤집기', on_press=self.flip_card))
        second_row_layout.add_widget(Button(text='다음 카드', on_press=self.next_card))
        self.layout.add_widget(second_row_layout)

        # 중간: 플래시카드
        self.card_label = Label(text='', font_size=32, halign='center', valign='middle')
        self.layout.add_widget(self.card_label)

        # 최하단: 언어와 음성 관련 버튼 메뉴
        options_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        options_layout.add_widget(Spinner(
            text='단어 언어',
            values=list(self.voice_options.keys()),
            size_hint_x=0.25
        ))
        options_layout.add_widget(Spinner(
            text='의미 언어',
            values=list(self.voice_options.keys()),
            size_hint_x=0.25
        ))
        options_layout.add_widget(Spinner(
            text='단어 음성',
            values=self.voice_options["en-US"],
            size_hint_x=0.25
        ))
        options_layout.add_widget(Spinner(
            text='의미 음성',
            values=self.voice_options["ko-KR"],
            size_hint_x=0.25
        ))
        self.layout.add_widget(options_layout)

        self.initial_load = True  # TTS 재생 방지를 위해 플래그 설정
        self.show_card()
        self.initial_load = False  # 플래그 해제

    def delete_card(self, instance):
        if self.cards:
            deleted_card = self.cards.pop(self.current_card_index)
            self.save_cards()
            print(f"삭제된 카드: {deleted_card['front']} - {deleted_card['back']}")
            if self.current_card_index >= len(self.cards):
                self.current_card_index = len(self.cards) - 1 if self.cards else 0
            self.show_card()
        else:
            print("삭제할 카드가 없습니다.")
            self.card_label.text = "삭제할 카드가 없습니다."

    def save_cards(self):
        main_screen = self.manager.get_screen('main')
        if main_screen.current_deck:
            deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
            file_path = os.path.join(deck_dir, 'flashcards.json')
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.cards, f, ensure_ascii=False, indent=2)
                print(f"카드가 저장되었습니다: {len(self.cards)}개")
            except Exception as e:
                print(f"카드 저장 중 오류 발생: {e}")


class ExcelScreen(Screen):
    def __init__(self, **kwargs):
        super(ExcelScreen, self).__init__(**kwargs)
        self.tts_client = texttospeech.TextToSpeechClient()
        self.font_size = 22  # 기본 폰트 크기 설정

        self.layout = BoxLayout(orientation='vertical')
        self.grid = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.touch_start_time = 0
        self.long_press_triggered = False
        self.touch_event = None

        self.current_sound = None
        self.stop_tts_event = threading.Event()
        self.current_playing_index = None
        self.current_playing_side = None
        self.is_playing = False
        #self.last_clicked_instance = None
        # 메뉴 레이아웃 설정
        self.menu_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.menu_layout.add_widget(Button(text='뒤로', on_press=self.go_back, size_hint_x=0.1, font_size=15))
        self.tts_toggle_button = Button(text='TTS 끄기', on_press=self.toggle_tts, size_hint_x=0.18, font_size=15)
        self.menu_layout.add_widget(self.tts_toggle_button)

        button_size_hint = 0.18  # (1 - 0.1 - 0.18) / 4 = 0.18

        self.word_lang_spinner = Spinner(
            text='단어 언어',
            size_hint_x=button_size_hint,
            height=50,
            font_size=16
        )
        self.word_lang_spinner.bind(text=self.on_word_language_select)
        self.menu_layout.add_widget(self.word_lang_spinner)

        self.meaning_lang_spinner = Spinner(
            text='의미 언어',
            size_hint_x=button_size_hint,
            height=50,
            font_size=16
        )
        self.meaning_lang_spinner.bind(text=self.on_meaning_language_select)
        self.menu_layout.add_widget(self.meaning_lang_spinner)

        self.word_voice_spinner = Spinner(
            text='단어 음성',
            size_hint_x=button_size_hint,
            height=50,
            font_size=16
        )
        self.word_voice_spinner.bind(text=self.on_word_voice_select)
        self.menu_layout.add_widget(self.word_voice_spinner)

        self.meaning_voice_spinner = Spinner(
            text='의미 음성',
            size_hint_x=button_size_hint,
            height=50,
            font_size=16
        )
        self.meaning_voice_spinner.bind(text=self.on_meaning_voice_select)
        self.menu_layout.add_widget(self.meaning_voice_spinner)

        self.layout.add_widget(self.menu_layout)
        self.add_widget(self.layout)

        # 초기화 시점에 필요한 속성 설정
        self.word_language = 'en-US'
        self.meaning_language = 'ko-KR'
        self.word_voice = 'en-US-Standard-B'
        self.meaning_voice = 'ko-KR-Standard-A'
        self.tts_enabled = True
        self.words_hidden = False
        self.meanings_hidden = False

        # voice_options 정의 추가
        self.voice_options = {
            "ko-KR": ["ko-KR-Neural2-A", "ko-KR-Neural2-B", "ko-KR-Neural2-C"],
            "en-US": ["en-US-Neural2-A", "en-US-Standard-B", "en-US-Neural2-C", "en-US-Neural2-D", "en-US-Neural2-E"],
            "fr-FR": ["fr-FR-Standard-A", "fr-FR-Standard-B", "fr-FR-Standard-C", "fr-FR-Standard-D", "fr-FR-Standard-E"],
            "es-ES": ["es-ES-Standard-A", "es-ES-Standard-B"],  # 필요에 따라 추가
            "de-DE": ["de-DE-Standard-A", "de-DE-Standard-B"],  # 필요에 따라 추가
            # 다른 언어도 필요 시 추가
        }

        # 추가 버튼
        #self.add_button = Button(text='단어 추가', size_hint_y=None, height=50, on_press=self.add_card)
        #self.layout.add_widget(self.add_button)
        self.context_menu = None

    def on_enter(self):
        self.load_cards()
        self.setup_tts_controls()

    def setup_tts_controls(self):
        # 언어 선택 스피너 값 설정
        self.word_lang_spinner.values = list(self.voice_options.keys())
        self.meaning_lang_spinner.values = list(self.voice_options.keys())
        self.word_voice_spinner.values = self.voice_options[self.word_language]
        self.meaning_voice_spinner.values = self.voice_options[self.meaning_language]

    def go_back(self, instance):
        self.manager.current = 'main'

    def load_cards(self):
        self.grid.clear_widgets()

        # 제목 행 추가
        self.grid.add_widget(Label(text='번호', size_hint_y=None, height=40, size_hint_x=0.1, font_size=self.font_size))
        word_header = Label(text='단어', size_hint_y=None, height=40, size_hint_x=0.45, font_size=self.font_size)
        word_header.bind(on_touch_down=self.toggle_words_visibility)
        self.grid.add_widget(word_header)
        meaning_header = Label(text='의미', size_hint_y=None, height=40, size_hint_x=0.45, font_size=self.font_size)
        meaning_header.bind(on_touch_down=self.toggle_meanings_visibility)
        self.grid.add_widget(meaning_header)

        main_screen = self.manager.get_screen('main')
        deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
        file_path = os.path.join(deck_dir, 'flashcards.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.cards = json.load(f)
            for index, card in enumerate(self.cards):
                number_label = Label(text=str(index + 1), size_hint_y=None, height=40, size_hint_x=0.1, font_size=self.font_size)
                number_label.card_index = index
                number_label.card_side = 'number'  # 번호 레이블에 card_side 속성 추가
                number_label.bind(on_touch_down=self.on_cell_touch)

                front_label = Label(text=card['front'], size_hint_y=None, size_hint_x=0.45, font_size=self.font_size)
                front_label.bind(size=self.update_label_text_size)
                front_label.bind(texture_size=self.update_label_height)
                front_label.card_index = index
                front_label.card_side = 'front'
                front_label.bind(on_touch_down=self.on_cell_touch)
                #front_label.bind(on_touch_down=lambda instance, touch, idx=index: self.toggle_word_visibility(instance, touch, idx))


                back_label = Label(text=card['back'], size_hint_y=None, size_hint_x=0.45, font_size=self.font_size)
                back_label.bind(size=self.update_label_text_size)
                back_label.bind(texture_size=self.update_label_height)
                back_label.card_index = index
                back_label.card_side = 'back'
                back_label.bind(on_touch_down=self.on_cell_touch)
                #back_label.bind(on_touch_down=lambda instance, touch, idx=index: self.toggle_meaning_visibility(instance, touch, idx))
                                
                self.grid.add_widget(number_label)
                self.grid.add_widget(front_label)
                self.grid.add_widget(back_label)
            print(f"엑셀 모드에서 불러온 카드 수: {len(self.cards)}")
        except FileNotFoundError:
            print(f"flashcards.json 파일을 찾을 수 없습니다. 경로: {file_path}")
        except json.JSONDecodeError:
            print("flashcards.json 파일의 형식이 올바르지 않습니다.")
        except Exception as e:
            print(f"카드를 불러오는 중 오류 발생: {e}")

    def on_cell_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if instance.card_side in ['front', 'back']:
                # '나타났다 사라졌다' 기능
                if instance.text == '-':
                    instance.text = self.cards[instance.card_index][instance.card_side]
                else:
                    instance.text = '-' 
            
            # TTS 기능
            if self.tts_enabled:
                if self.current_sound and self.current_sound.state == 'play':
                    self.current_sound.stop()
                else:
                    card = self.cards[instance.card_index]
                    if instance.card_side == 'number':
                        self.synthesize_speech(word=card['front'], word_lang=self.word_language, word_voice=self.word_voice,
                                               meaning=card['back'], meaning_lang=self.meaning_language, meaning_voice=self.meaning_voice)
                    elif instance.card_side == 'front':
                        self.synthesize_speech(word=card['front'], word_lang=self.word_language, word_voice=self.word_voice)
                    elif instance.card_side == 'back':
                        self.synthesize_speech(meaning=card['back'], meaning_lang=self.meaning_language, meaning_voice=self.meaning_voice)


    def update_label_text_size(self, instance, size):
        instance.text_size = (size[0], None)

    def update_label_height(self, instance, size):
        instance.height = size[1]
        
    def toggle_words_visibility(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.words_hidden = not self.words_hidden
            for i in range(1, len(self.grid.children) - 2, 3):  # -2로 수정
                child = self.grid.children[i]
                if isinstance(child, Label) and hasattr(child, 'card_index'):
                    if child.text == '-' and not self.words_hidden:
                        child.text = self.cards[child.card_index]['front']
                    else:
                        child.text = '-' if self.words_hidden else self.cards[child.card_index]['front']

    def toggle_meanings_visibility(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.meanings_hidden = not self.meanings_hidden
            for i in range(0, len(self.grid.children) - 2, 3):  # -2로 수정
                child = self.grid.children[i]
                if isinstance(child, Label) and hasattr(child, 'card_index'):
                    if child.text == '-' and not self.meanings_hidden:
                        child.text = self.cards[child.card_index]['back']
                    else:
                        child.text = '-' if self.meanings_hidden else self.cards[child.card_index]['back']

    def toggle_word_visibility(self, instance, touch, index):
        if instance.collide_point(*touch.pos):
            instance.text = '-' if instance.text != '-' else self.cards[index]['front']
            if self.tts_enabled:
                self.speak(self.cards[index]['front'], is_word=True)

    def toggle_meaning_visibility(self, instance, touch, index):
        if instance.collide_point(*touch.pos):
            instance.text = '-' if instance.text != '-' else self.cards[index]['back']
            if self.tts_enabled:
                self.speak(self.cards[index]['back'], is_word=False)

    def play_tts_sequence(self, instance, touch, index):
        if instance.collide_point(*touch.pos) and self.tts_enabled:
            if self.current_sound and self.current_sound.state == 'play':
                self.current_sound.stop()
            else:
                card = self.cards[index]
                if instance.card_side == 'number':
                    self.synthesize_speech(word=card['front'], word_lang=self.word_language, word_voice=self.word_voice,
                                           meaning=card['back'], meaning_lang=self.meaning_language, meaning_voice=self.meaning_voice)
                elif instance.card_side == 'front':
                    self.synthesize_speech(word=card['front'], word_lang=self.word_language, word_voice=self.word_voice)
                elif instance.card_side == 'back':
                    self.synthesize_speech(meaning=card['back'], meaning_lang=self.meaning_language, meaning_voice=self.meaning_voice)

    def synthesize_speech(self, word=None, word_lang=None, word_voice=None, meaning=None, meaning_lang=None, meaning_voice=None):
        if self.current_sound and self.current_sound.state == 'play':
            self.current_sound.stop()
        
        self.stop_tts_event.clear()

        def play_tts_sequence():
            try:
                if word and meaning:
                    self.play_tts(word, word_lang, word_voice)
                    if self.stop_tts_event.is_set():
                        return
                    while self.current_sound and self.current_sound.state == 'play':
                        if self.stop_tts_event.is_set():
                            self.current_sound.stop()
                            return
                        Clock.tick(10)
                    
                    self.play_tts(meaning, meaning_lang, meaning_voice)
                    if self.stop_tts_event.is_set():
                        return
                    while self.current_sound and self.current_sound.state == 'play':
                        if self.stop_tts_event.is_set():
                            self.current_sound.stop()
                            return
                        Clock.tick(10)
                elif word:
                    self.play_tts(word, word_lang, word_voice)
                elif meaning:
                    self.play_tts(meaning, meaning_lang, meaning_voice)
            except Exception as e:
                print(f"TTS 재생 중 오류 발생: {e}")
            finally:
                self.current_sound = None

        self.current_tts_thread = threading.Thread(target=play_tts_sequence)
        self.current_tts_thread.start()

    def stop_current_tts(self):
        self.stop_tts_event.set()
        if self.current_sound and self.current_sound.state == 'play':
            self.current_sound.stop()
        self.stop_tts_event.clear()
        self.is_playing = False
        self.current_playing_index = None
        self.current_playing_side = None

    def start_new_tts(self, instance, index):
        card = self.cards[index]
        
        if instance.card_side == 'number':
            self.current_tts_thread = threading.Thread(target=self.play_word_and_meaning_tts, args=(card,))
        elif instance.card_side == 'front':
            self.current_tts_thread = threading.Thread(target=self.play_word_tts, args=(card['front'],))
        elif instance.card_side == 'back':
            self.current_tts_thread = threading.Thread(target=self.play_meaning_tts, args=(card['back'],))

        self.is_playing = True
        self.current_playing_index = index
        self.current_playing_side = instance.card_side
        self.current_tts_thread.start()


    def play_word_and_meaning_tts(self, card):
        if not self.stop_tts_event.is_set():
            self.synthesize_speech(
                word=card['front'],
                word_lang=self.word_language,
                word_voice=self.word_voice,
                meaning=card['back'],
                meaning_lang=self.meaning_language,
                meaning_voice=self.meaning_voice
            )
        self.reset_tts_state()

    def play_word_tts(self, word):
        if not self.stop_tts_event.is_set():
            self.speak(word, is_word=True)
        self.reset_tts_state()

    def play_meaning_tts(self, meaning):
        if not self.stop_tts_event.is_set():
            self.speak(meaning, is_word=False)
        self.reset_tts_state()

    def reset_tts_state(self):
        self.is_playing = False
        self.current_playing_index = None
        self.current_playing_side = None


    def play_tts(self, text, language, voice):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                temp_audio_path = temp_audio_file.name
                temp_audio_file.write(response.audio_content)

            self.current_sound = SoundLoader.load(temp_audio_path)
            if self.current_sound:
                self.current_sound.play()

                while self.current_sound.state == 'play':
                    if self.stop_tts_event.is_set():
                        self.current_sound.stop()
                        break
                    Clock.tick(10)

                os.unlink(temp_audio_path)

        except Exception as e:
            print(f"TTS 재생 중 오류 발생: {e}")


    def speak(self, text, is_word=True):
        language = self.word_language if is_word else self.meaning_language
        voice = self.word_voice if is_word else self.meaning_voice
        self.synthesize_speech(word=text, word_lang=language, word_voice=voice) if is_word else self.synthesize_speech(meaning=text, meaning_lang=language, meaning_voice=voice)

    def on_word_language_select(self, spinner, text):
        self.word_language = text
        self.word_voice_spinner.values = self.voice_options[text]
        self.word_voice_spinner.text = self.voice_options[text][0]
        self.word_voice = self.voice_options[text][0]
        print(f"단어 언어 변경: {self.word_language}, 음성: {self.word_voice}")

    def on_meaning_language_select(self, spinner, text):
        self.meaning_language = text
        self.meaning_voice_spinner.values = self.voice_options[text]
        self.meaning_voice_spinner.text = self.voice_options[text][0]
        self.meaning_voice = self.voice_options[text][0]
        print(f"의미 언어 변경: {self.meaning_language}, 음성: {self.meaning_voice}")

    def on_word_voice_select(self, spinner, text):
        self.word_voice = text
        print(f"단어 음성 변경: {self.word_voice}")

    def on_meaning_voice_select(self, spinner, text):
        self.meaning_voice = text
        print(f"의미 음성 변경: {self.meaning_voice}")

    def toggle_tts(self, instance):
        self.tts_enabled = not self.tts_enabled
        instance.text = 'TTS 켜기' if not self.tts_enabled else 'TTS 끄기'
        print(f"TTS 기능 {'활성화됨' if self.tts_enabled else '비활성화됨'}")
        if self.tts_enabled:
            self.play_current_card_tts(None)


    def on_label_touch_down(self, instance, touch):
        if touch.is_double_tap or touch.is_mouse_scrolling:
            return False
        if instance.collide_point(*touch.pos):
            self.touch_start_time = time.time()
            self.long_press_triggered = False
            self.touch_event = Clock.schedule_once(partial(self.check_long_press, instance, touch), 0.5)
            return True
        return False

    def on_label_touch_up(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if self.touch_event:
                self.touch_event.cancel()
            if not self.long_press_triggered:
                # 짧은 터치일 경우 단어 또는 의미 토글
                if hasattr(instance, 'card_side'):
                    if instance.card_side == 'front':
                        self.toggle_word_visibility(instance, touch, instance.card_index)
                    elif instance.card_side == 'back':
                        self.toggle_meaning_visibility(instance, touch, instance.card_index)
            return True
        return False

    def check_long_press(self, instance, touch, dt):
        if time.time() - self.touch_start_time >= 0.5:
            self.long_press_triggered = True
            self.show_context_menu(instance, touch, instance.card_index)


    def show_context_menu(self, instance, touch, index):
        if self.context_menu:
            self.remove_widget(self.context_menu)

        card = self.cards[index]
        front_text = f"단어: {card['front']}"
        back_text = f"의미: {card['back']}"

        menu = BoxLayout(orientation='vertical', size_hint=(None, None), size=(150, 180))
        
        word_label = Label(text=front_text, size_hint_y=None, height=30)
        meaning_label = Label(text=back_text, size_hint_y=None, height=30)
        menu.add_widget(word_label)
        menu.add_widget(meaning_label)

        edit_button = Button(text='수정', size_hint_y=None, height=40)
        delete_button = Button(text='삭제', size_hint_y=None, height=40)
        insert_button = Button(text='삽입', size_hint_y=None, height=40)
        add_button = Button(text='추가', size_hint_y=None, height=40)
        cancel_button = Button(text='취소', size_hint_y=None, height=40)

        menu.add_widget(edit_button)
        menu.add_widget(delete_button)
        menu.add_widget(insert_button)
        menu.add_widget(add_button)
        menu.add_widget(cancel_button)  # 취소 버튼을 메뉴에 추가


        # 메뉴 위치 조정
        menu_x = min(touch.x, Window.width - menu.width)
        menu_y = max(touch.y - menu.height, 0)
        menu.pos = (menu_x, menu_y)
        
        self.add_widget(menu)
        self.context_menu = menu

        edit_button.bind(on_release=lambda x: self.edit_card(index, x))
        delete_button.bind(on_release=partial(self.delete_card, index))
        insert_button.bind(on_release=partial(self.insert_card, index))
        add_button.bind(on_release=lambda x: self.add_card())
        cancel_button.bind(on_release=self.close_context_menu)  # 취소 버튼에 기능 연결

    def close_context_menu(self, instance):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

    def insert_card(self, index, instance):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

        self.front_input = TextInput(hint_text='단어 입력')
        self.back_input = TextInput(hint_text='의미 입력')
        create_button = Button(text='삽입', on_press=partial(self.create_inserted_card, index))
        cancel_button = Button(text='취소', on_press=self.close_popup)

        content = BoxLayout(orientation='vertical')
        content.add_widget(self.front_input)
        content.add_widget(self.back_input)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        button_layout.add_widget(create_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        self.popup = Popup(title='카드 삽입', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def create_inserted_card(self, index, instance):
        front = self.front_input.text.strip()
        back = self.back_input.text.strip()
        if front and back:
            new_card = {'front': front, 'back': back, 'starred': False}
            self.cards.insert(index + 1, new_card)
            self.save_cards()
            self.load_cards()
            self.layout.clear_widgets()
            self.__init__()
            self.on_enter()


    def edit_card(self, index, instance):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

        card = self.cards[index]
        self.front_input = TextInput(text=card['front'])
        self.back_input = TextInput(text=card['back'])
        save_button = Button(text='저장', on_press=lambda x: self.save_edited_card(index))
        cancel_button = Button(text='취소', on_press=self.close_popup)

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='앞면 수정'))
        content.add_widget(self.front_input)
        content.add_widget(Label(text='뒷면 수정'))
        content.add_widget(self.back_input)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        self.popup = Popup(title='카드 수정', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def save_edited_card(self, index):
        self.cards[index]['front'] = self.front_input.text
        self.cards[index]['back'] = self.back_input.text
        self.save_cards()
        self.load_cards()
        self.layout.clear_widgets()
        self.__init__()
        self.on_enter()

    def save_cards(self):
        main_screen = self.manager.get_screen('main')
        deck_dir = os.path.join(os.getcwd(), 'decks', main_screen.current_deck)
        file_path = os.path.join(deck_dir, 'flashcards.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.cards, f, ensure_ascii=False, indent=4)
            print("카드가 성공적으로 저장되었습니다.")
        except Exception as e:
            print(f"카드를 저장하는 중 오류 발생: {e}")

    def delete_card(self, index):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

        del self.cards[index]
        self.save_cards()
        self.load_cards()

    def cancel_edit(self, instance):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

        self.layout.clear_widgets()
        self.__init__()
        self.on_enter()

    def add_card(self):
        if self.context_menu:
            self.remove_widget(self.context_menu)
            self.context_menu = None

        self.front_input = TextInput(hint_text='단어 입력')
        self.back_input = TextInput(hint_text='의미 입력')
        create_button = Button(text='생성', on_press=self.create_new_card)
        finish_button = Button(text='완료', on_press=self.close_popup)

        content = BoxLayout(orientation='vertical')
        content.add_widget(self.front_input)
        content.add_widget(self.back_input)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        button_layout.add_widget(create_button)
        button_layout.add_widget(finish_button)
        content.add_widget(button_layout)

        self.popup = Popup(title='카드 추가', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def close_popup(self, instance):
        self.popup.dismiss()

    def create_new_card(self, instance):
        front = self.front_input.text.strip()
        back = self.back_input.text.strip()
        if front and back:
            new_card = {'front': front, 'back': back, 'starred': False}
            self.cards.append(new_card)
            self.save_cards()
            self.load_cards()
            self.front_input.text = ''
            self.back_input.text = ''

    def finish_adding(self, instance):
        self.layout.clear_widgets()
        self.__init__()
        self.on_enter()

    def save_new_card(self, instance):
        front = self.front_input.text.strip()
        back = self.back_input.text.strip()
        if front and back:
            new_card = {'front': front, 'back': back, 'starred': False}
            self.cards.append(new_card)
            self.save_cards()
            self.load_cards()
            self.layout.clear_widgets()
            self.__init__()
            self.on_enter()

    def cancel_edit(self, instance):
        self.layout.clear_widgets()
        self.__init__()
        self.on_enter()


if __name__ == '__main__':
    try:
        FlashcardApp().run()
    except Exception as e:
        print(f"앱 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

# main.py
import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, ListProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.core.window import Window
from innertube import InnerTube
import threading
import requests

class StreamInfoItem(RecycleDataViewBehavior, BoxLayout):
    format_type = StringProperty('')
    quality = StringProperty('')
    codec = StringProperty('')
    bitrate = StringProperty('')
    size = StringProperty('')

class StreamsRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

class YtifyApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Video ID input
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.video_id_input = TextInput(
            multiline=False, 
            hint_text='Enter YouTube Video ID', 
            size_hint_x=0.7
        )
        fetch_button = Button(
            text='Fetch Streams', 
            on_press=self.fetch_video_streams, 
            size_hint_x=0.3
        )
        input_layout.add_widget(self.video_id_input)
        input_layout.add_widget(fetch_button)
        
        # Title and description labels
        self.title_label = Label(
            text='', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None, 
            height=50
        )
        self.description_label = Label(
            text='', 
            font_size='12sp',
            text_size=(Window.width, None),
            size_hint_y=None, 
            height=100
        )
        
        # Streams RecycleView
        self.streams_view = StreamsRecycleView()
        self.streams_view.layout = RecycleGridLayout(
            cols=2, 
            default_size=(None, 50), 
            default_size_hint=(1, None), 
            size_hint_y=None, 
            height=300
        )
        
        # Add widgets to main layout
        layout.add_widget(input_layout)
        layout.add_widget(self.title_label)
        layout.add_widget(self.description_label)
        layout.add_widget(self.streams_view)
        
        return layout
    
    def fetch_video_streams(self, instance):
        video_id = self.video_id_input.text.strip()
        if not video_id:
            return
        
        # Clear previous data
        self.title_label.text = 'Fetching...'
        self.description_label.text = ''
        self.streams_view.data = []
        
        # Run fetch in a separate thread
        threading.Thread(target=self._fetch_streams, args=(video_id,), daemon=True).start()
    
    def _fetch_streams(self, video_id):
        try:
            yt = InnerTube("ANDROID")
            data = yt.player(video_id)
            
            # Update UI on main thread
            self.update_ui(data)
        
        except Exception as e:
            self.show_error(str(e))
    
    def update_ui(self, data):
        from kivy.clock import Clock
        
        def update(dt):
            # Extract video details
            video_details = data.get("videoDetails", {})
            streaming_data = data.get("streamingData", {})
            
            # Set title and description
            self.title_label.text = video_details.get("title", "No Title")
            self.description_label.text = video_details.get("shortDescription", "No Description")
            
            # Prepare stream data
            stream_data = []
            
            # Audio streams
            for audio in streaming_data.get("adaptiveFormats", []):
                if "audio" in audio.get("mimeType", "").lower():
                    stream_data.append({
                        'format_type': f'Audio - {audio.get("audioQuality", "").replace("AUDIO_QUALITY_", "").capitalize()}',
                        'quality': audio.get("mimeType", "").split(";")[0],
                        'codec': audio.get("mimeType", "").split(";")[0].split("/")[-1],
                        'bitrate': f'{audio.get("bitrate", 0) / 1000:.0f} kbps',
                        'size': f'{int(audio.get("contentLength", 0)) / (1024 * 1024):.2f} MB'
                    })
            
            # Video streams
            for video in streaming_data.get("adaptiveFormats", []):
                if "video" in video.get("mimeType", "").lower() and "audio" not in video.get("mimeType", "").lower():
                    stream_data.append({
                        'format_type': f'Video - {video.get("qualityLabel", "")}',
                        'quality': video.get("mimeType", "").split(";")[0],
                        'codec': video.get("mimeType", "").split(";")[0].split("/")[-1],
                        'bitrate': f'{video.get("bitrate", 0) / 1000:.0f} kbps',
                        'size': f'{int(video.get("contentLength", 0)) / (1024 * 1024):.2f} MB'
                    })
            
            # Update RecycleView
            self.streams_view.data = [
                {
                    'format_type': item['format_type'],
                    'quality': item['quality'],
                    'codec': item['codec'],
                    'bitrate': item['bitrate'],
                    'size': item['size']
                } for item in stream_data
            ]
        
        Clock.schedule_once(update, 0)
    
    def show_error(self, error_msg):
        from kivy.clock import Clock
        
        def display_error(dt):
            self.title_label.text = 'Error'
            self.description_label.text = str(error_msg)
        
        Clock.schedule_once(display_error, 0)

if __name__ == '__main__':
    YtifyApp().run()

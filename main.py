from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.logger import Logger

# based on websocket-client==0.40.0
# patch fixes android error : no handlers could be found for logger "websocket"
# changed logger to kivy.logger.Logger

import websocket

# standard libraries (python 2.7)
import thread
import time

kv = '''
<WS>:
    orientation: 'vertical'
    the_btn: the_btn
    Button:
        id: the_btn
        text: "Open Websocket"
        on_press: self.parent.pressed_the_btn()
'''
Builder.load_string(kv)


class ConnectedSocket(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        super(ConnectedSocket, self).__init__(*args, **kwargs)
        self.logger = Logger
        self.logger.info('WebSocket: logger initialized')


class WS(BoxLayout):
    the_btn = ObjectProperty()
    pressed = False

    def __init__(self, **kwargs):
        super(WS, self).__init__(**kwargs)
        Logger.info('Layout: initialized')

    def pressed_the_btn(self):
        if self.pressed is False:
            self.pressed = True
            self.the_btn.text = 'connecting to web socket'
            app = App.get_running_app()
            Clock.schedule_once(app.ws_connection)


class WebSocketTest(App):
    ws = None
    url = "ws://echo.websocket.org/"
    btn_txt = StringProperty('press me')
    layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(WebSocketTest, self).__init__(**kwargs)
        socket_server="ws://echo.websocket.org/"
        ws = ConnectedSocket(socket_server,
                             on_message=self.on_ws_message,
                             on_error=self.on_ws_error,
                             on_open=self.on_ws_open,
                             on_close=self.on_ws_close,)
        self.ws = ws
        self.logger = Logger
        self.logger.info('App: initiallzed')

    def build(self):
        self.layout = WS()
        return self.layout

    def on_ws_message(self, ws, message):
        self.layout.the_btn.text = message
        self.logger.info('WebSocket: {}'.format(message))

    def on_ws_error(self, ws, error):
        # self.layout.the_btn.text = error
        self.logger.info('WebSocket: [ERROR]  {}'.format(error))

    def ws_connection(self, dt, **kwargs):
        # start a new thread connected to the web socket
        thread.start_new_thread(self.ws.run_forever, ())

    def on_ws_open(self, ws):
        def run(*args):
            for i in range(1, 13):
                time.sleep(1)
                ws.send('Hello %d' % i)
            time.sleep(10)
            ws.close()
        thread.start_new_thread(run, ())

    def on_ws_close(self, ws):
        self.layout.the_btn.text = '### closed ###'


if __name__ == "__main__":
    WebSocketTest().run()
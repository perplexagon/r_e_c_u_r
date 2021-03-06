from video_centre.video_player import VideoPlayer

class VideoDriver(object):

    MAX_LAYER = 254

    def __init__(self, root, message_handler, data):
        self.root = root
        self.message_handler = message_handler
        self.data = data
        self.delay = 50
        self.in_first_load_cycle = False
        self.in_current_playing_cycle = False
        self.in_next_load_cycle = False

        self.layer = self.MAX_LAYER

        self.last_player = VideoPlayer(self.root, self.message_handler, self.data, 'a.a')
        self.current_player = VideoPlayer(self.root,self.message_handler, self.data, 'b.b')
        self.next_player = VideoPlayer(self.root, self.message_handler, self.data, 'c.c')
        self.root.after(self.delay, self.begin_playing)

        self.update_video_settings()


    def update_video_settings(self):
        self.switch_on_finish = self.data.settings['sampler']['ON_FINISH']['value'] == 'switch'
        
    def get_next_layer_value(self):
        if self.layer > 0:
            self.layer = self.layer - 1
        else:
            self.layer = self.MAX_LAYER
            self.current_player.reload(self.get_next_layer_value())
        return self.layer

    def print_status(self):
        print('l({}):{}, c({}):{}, n({}):{}'.format(self.last_player.name, self.last_player.status, self.current_player.name, \
        self.current_player.status, self.next_player.name, self.next_player.status,))
        self.root.after(1000,self.print_status)

    def begin_playing(self):
        if self.current_player.try_load(self.get_next_layer_value()):
            self.in_first_load_cycle = True
            self.wait_for_first_load()
        else:
            print('load failed')

    def wait_for_first_load(self):
        if self.in_first_load_cycle:
            if self.current_player.is_loaded():
                self.in_first_load_cycle = False
                self.start_video()
            else:
                self.root.after(self.delay, self.wait_for_first_load)

    def switch_players_and_start_video(self):
        self.in_first_load_cycle = False
        self.in_current_playing_cycle = False
        self.in_next_load_cycle = True

        self.switch_players()

    def switch_players(self):
        temp_player = self.last_player
        self.last_player = self.current_player
        self.current_player = self.next_player
        self.next_player = temp_player

        self.start_video()

    def start_video(self):
        self.current_player.start_video()
        self.last_player.exit()
        self.next_player.try_load(self.get_next_layer_value())
        self.in_current_playing_cycle = True
        self.wait_for_next_cycle()

    def wait_for_next_cycle(self):
        if self.in_current_playing_cycle:
            if self.current_player.is_finished():
                self.in_current_playing_cycle = False
                self.in_next_load_cycle = True
                if self.switch_on_finish:
                    self.switch_if_next_is_loaded()
            else:
                self.root.after(self.delay, self.wait_for_next_cycle)

    def switch_if_next_is_loaded(self):
        if self.in_next_load_cycle:
            if self.next_player.is_loaded():
                self.in_next_load_cycle = False
                self.switch_players()
            else:
                if self.next_player.status != 'ERROR':
                    self.root.after(self.delay, self.switch_if_next_is_loaded)
                else:
                    self.in_next_load_cycle = False


    def get_player_info_for_status(self):
        return self.current_player.bankslot_number, self.current_player.status, self.current_player.alpha, \
                   self.next_player.bankslot_number, self.next_player.status, self.next_player.alpha

    def get_player_info_for_banner(self, player):
        if player == 'now':
            return self.current_player.start, self.current_player.end, self.current_player.get_position()
        elif player == 'next':
            return self.next_player.start, self.next_player.end, self.next_player.get_position()

    def exit_all_players(self):
        self.next_player.exit()
        self.current_player.exit()

    def reload_next_player(self):
        self.next_player.reload(self.get_next_layer_value())


import pyglet
import tools
import json
import glob
import os
import math
import random
no_draw_batch = pyglet.graphics.Batch()
class Main_Window(pyglet.window.Window):
    def __init__(self, w,h,c):
        super(Main_Window, self).__init__(w,h,caption=c, resizable=True)
        self.dwidth = w
        self.dheight = h
        self.initiate_variables()
        pyglet.app.run()
    def make_menu(self):
        tmp_image = tools.center_image(pyglet.image.load("./resources/menu/title.png"), "center", "bottom")
        self.title_label = pyglet.sprite.Sprite(tmp_image, x=self.width//2, y=self.height//2 + 200, batch=self.menu_batch, group=self.m_top_order)
        self.play_button = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/menu/play_button.png")), self.width //2, self.height//2, batch=self.menu_batch, group=self.m_top_order)
        self.level_editor_button = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/menu/level_editor_button.png")), self.play_button.x, self.play_button.y - 210, batch=self.menu_batch, group=self.m_top_order)
        self.quit_button = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/menu/quit_button.png")), self.play_button.x, self.level_editor_button.y - 210, batch=self.menu_batch, group=self.m_top_order)
    def make_level_selector(self):
        if self.gamestage == "level_select":
            pyglet.gl.glClearColor(0.00, 0.410, 0.0820,1)
            self.level_selector_help_text = pyglet.text.Label('Drag your mouse around to explore then click on the text to play',
                            font_name='Arial',
                            font_size=20,
                            x=self.width//2, y=200,
                            anchor_x='center', anchor_y='center', batch=self.level_select_batch)
        else:
            self.level_selector_help_text = pyglet.text.Label('Drag your mouse around to explore, TAB to create a new level',
                            font_name='Arial',
                            font_size=20,
                            x=self.width//2, y=200,
                            anchor_x='center', anchor_y='center', batch=self.level_editor_batch)
        
        self.level_buttons = []
        if self.gamestage == "level_select":
            for i in glob.glob("./resources/maps/*.json"):
                with open(os.path.normpath(i), 'r') as file:
                    data = json.load(file)
                    self.map_name_from_json = data["name"]
                if len(self.level_buttons) > 0:
                    self.level_buttons.append(LevelButton(self.width//2,self.level_buttons[len(self.level_buttons) - 1].sprite.y + 100, self.map_name_from_json, os.path.normpath(i), self.level_select_batch))
                else:
                    self.level_buttons.append(LevelButton(self.width//2,500, self.map_name_from_json, os.path.normpath(i), self.level_select_batch))
        else:
            for i in glob.glob("./resources/maps/*.json"):
                with open(os.path.normpath(i), 'r') as file:
                    data = json.load(file)
                    self.map_name_from_json = data["name"]
                if len(self.level_buttons) > 0:
                    self.level_buttons.append(LevelButton(self.width//2,self.level_buttons[len(self.level_buttons) - 1].sprite.y + 100, self.map_name_from_json, os.path.normpath(i), self.level_editor_batch))
                else:
                    self.level_buttons.append(LevelButton(self.width//2,500, self.map_name_from_json, os.path.normpath(i), self.level_editor_batch))
    def load_map(self, map, to_game=True):
        """
        Pass in the map location
        """
        self.level_buttons = []
        self.blocks = []
        with open(map) as map_data:
            map_json = json.load(map_data)
            for i in map_json["blocks"]:
                #since the isBackground is one or zero we need to change it to true or false
                self.isCoin = False
                if i[5] == 1:
                    self.isCoin = True
                else:
                    self.isCoin = False
                self.blockorder = object #this variable exists because we want the block order to be background if isBackground is true
                if i[4]  == 1:
                    self.isBackground = True
                else:
                    self.isBackground = False
                if to_game:
                    temporary_block = Block(i[0], i[1], i[2],i[1], i[2], i[3], self.isBackground, self.isCoin, self.game_batch, self.layers[i[6]], i[6]) #this is the block we want to append to the blocks list
                else:
                    temporary_block = Block(i[0], i[1], i[2], i[1], i[2],i[3], self.isBackground, self.isCoin, self.level_editor_batch, self.layers[i[6]], i[6])
                self.blocks.append(temporary_block)
            if to_game:
                self.player = Player(map_json["player_start_pos"][0],map_json["player_start_pos"][1],self.width, self.height, self.blocks, self.game_batch, self.g_player_order)
        print(self.blocks)
        if to_game:
            self.schedule_game_functions()
            self.gamestage = "game"
        pyglet.gl.glClearColor(0,0,0,1)
    def check_if_player_at_edge(self, dt):
        """Checks if player is at edge and scrolls the screen"""
        if self.player.sprite.x < 200:
            for i in self.blocks:
                i.sprite.x += 500 * dt
            self.player.sprite.x += 500 * dt
        if self.player.sprite.x > self.width - 200:
            for i in self.blocks:
                i.sprite.x -= 500 * dt
            self.player.sprite.x -= 500 * dt
        if self.player.sprite.y < 200:
            for i in self.blocks:
                i.sprite.y += 500 * dt
            self.player.sprite.y += 500 * dt
        if self.player.sprite.y > self.height - 200:
            for i in self.blocks:
                i.sprite.y -= 500 * dt
            self.player.sprite.y -= 500 * dt
    def make_endmenu(self):
        pyglet.clock.unschedule(self.clock_tick)
        self.timer_text.batch = no_draw_batch
        self.coin_text.batch = no_draw_batch
        self.backboard = tools.center_image(pyglet.shapes.Rectangle(self.width//2, self.height//2, 800, 800, (138,76,29), batch=self.endgame_batch))
        self.win_label = pyglet.text.Label(f'You won\nin\n{self.player_timer}s',
                          font_name='Arial',
                          font_size=60,
                          x=self.width//2, y=self.height - self.height//4,
                          anchor_x='center', anchor_y='center', batch=self.endgame_batch)
        self.player_timer = 0
        self.to_menu_button = tools.center_image(pyglet.shapes.Rectangle(self.backboard.x, self.backboard.y - self.backboard.height //4, 200, 100, (0,255,50), batch=self.endgame_batch))
        self.to_menu_label = pyglet.text.Label('Go to menu',
                          font_name='Arial',
                          font_size=24,
                          x=self.to_menu_button.x, y=self.to_menu_button.y,
                          anchor_x='center', anchor_y='center', batch=self.endgame_batch)
    def add_coin_to_player(self, block):
        self.tmp_coin_block = block
        self.tmp_coin_block.sprite.batch = no_draw_batch
        self.coins_collected_array.append(block)
        block.batch = None
        block.group = None
        self.blocks.remove(block)
        self.coins_collected += 1
        self.coin_text.text = f'{self.coins_collected} / {self.coins_in_level}'
        if self.coins_collected >= self.coins_in_level:
            self.unschedule_game_functions()
            self.gamestage = "endgame"
            self.make_endmenu()
    def player_velocity_updates(self, dt):
        if self.paused:
            return
        self.check_if_player_at_edge(dt)
        self.player.sprite.x += self.player.x_velocity * dt
        self.player.sprite.y += self.player.y_velocity * dt
        self.player_collision = self.check_for_player_collision()
        if self.player_collision:
            if self.player_collision[0] == "collision":
                self.explosion_sound.play()
                for i in range(0,360,5):
                    self.particles_active.append(Particle(self.player.sprite.x, self.player.sprite.y, i, self.game_batch, self.g_particle_order, self.particles_active, True))
                for i in self.coins_collected_array:
                    i.sprite.batch = self.game_batch
                    self.blocks.append(i)
                self.coins_collected = 0
                self.coin_text.text = f"{0} / {self.coins_in_level}"
                self.coins_collected_array = []
                self.player.respawn(self.width, self.height)
            elif self.player_collision[0] == "coin":
                self.coin_collect_sound.play()
                self.add_coin_to_player(self.player_collision[1])
        if self.player.gravity_enabled:
            self.player.y_velocity -= self.gravity_amount * dt
    def check_for_player_collision(self):
        for i in self.blocks:
            if tools.separating_axis_theorem(tools.getRect(i.sprite), tools.getRect(self.player.sprite)) and not i.background_object:
                if i.iscoin:
                    return ["coin", i]
                else:
                    return ["collision", i]
        return []
    def schedule_game_functions(self):
        self.coins_collected = 0
        self.coins_collected_array = []
        self.coins_in_level = self.scan_for_coins_in_level()
        self.coin_text = pyglet.text.Label(f'{self.coins_collected} / {self.coins_in_level}',
                    font_name='Arial',
                    font_size=36,
                    x=5, y=5,
                    anchor_x='left', anchor_y='bottom', batch=self.game_batch, group=self.g_gui_order)
        self.timer_text = pyglet.text.Label(f'{self.player_timer}s',
            font_name='Arial',
            font_size=36,
            x=self.width, y=5,
            anchor_x='right', anchor_y='bottom', batch=self.game_batch, group=self.g_gui_order)
        pyglet.clock.schedule_interval_soft(self.player_velocity_updates, 1/60.00)
        pyglet.clock.schedule_interval_soft(self.clock_tick, 1)
    def clock_tick(self, dt):
        if self.paused:
            return
        self.player_timer += 1
        self.timer_text.text = f'{self.player_timer}s'
    def unschedule_game_functions(self):
        pyglet.clock.unschedule(self.player_velocity_updates)
        pyglet.clock.unschedule(self.clock_tick)
    def scan_for_coins_in_level(self):
        self.qwertyiop = 0 #this variable is the amount of coins in the level
        for i in self.blocks:
            if i.iscoin:
                self.qwertyiop += 1
        return self.qwertyiop
    def load_sounds(self):
        self.menu_loop = pyglet.media.load("./resources/sounds/loop1.mp3", streaming=True)
        self.jump_sound = pyglet.media.load("./resources/sounds/jump.wav", streaming=False)
        self.explosion_sound = pyglet.media.load("./resources/sounds/death_sound_effect.mp3", streaming=False)
        self.coin_collect_sound = pyglet.media.load("./resources/sounds/coin_collected.mp3", streaming=False)
    def make_pause_menu(self):
        self.quit_button2 = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/menu/quit_button.png")), self.width//2, self.height//2, batch=self.paused_batch)
    def process_keys_in_level_editor(self, dt):
        for i in self.keys_down:
            #if i == pyglet.window.key.W:
            #    self.editor_true_pos[1] += self.editor_move_speed * dt
             #   for i in self.blocks:
            #        i.sprite.y -= self.editor_move_speed * dt
            #if i == pyglet.window.key.S:
             #   self.editor_true_pos[1] -= self.editor_move_speed * dt
              #  for i in self.blocks:
               #     i.sprite.y += self.editor_move_speed * dt
            #if i == pyglet.window.key.A:
             #   self.editor_true_pos[0] -= self.editor_move_speed * dt
              #  for i in self.blocks:
               #     i.sprite.x += self.editor_move_speed * dt
            #if i == pyglet.window.key.D:
             #   self.editor_true_pos[0] += self.editor_move_speed * dt
              #  for i in self.blocks:
               #     i.sprite.x -= self.editor_move_speed * dt
            #if i == pyglet.window.key.RIGHT:
             #   self.level_editor_block_set_rotation += self.editor_rotate_speed
              #  self.level_editor_chosen_block_preview_image.sprite.rotation = self.level_editor_block_set_rotation
            #if i == pyglet.window.key.LEFT:
             #   self.level_editor_block_set_rotation -= self.editor_rotate_speed
              #  self.level_editor_chosen_block_preview_image.sprite.rotation = self.level_editor_block_set_rotation
            self.block_rotation_label.text = f"Block Rotation: {self.level_editor_block_set_rotation}"
    def shuffle_block_images(self, chosen_index=0):
        index = 0
        if index == chosen_index:
            self.first = True
        else:
            self.first = False
        for i in self.block_images:
            if index == chosen_index:
                self.first = True
            if self.first:
                i.anchor_x = i.width//2
                i.x = self.level_editor_pointer.x + self.level_editor_pointer.width//2
                self.first = False
            else:
                i.x = self.block_images[index - 1].x + self.block_images[index - 1].width//2 + (self.block_images[index].width)
            index += 1
        index = 0
    def load_block_images(self):
        self.glob_for_blocks = os.listdir("./resources/blocks/")
        index = 0
        for i in self.glob_for_blocks:
            tmp_image = pyglet.image.load(f"./resources/blocks/{i}")
            tmp_image.anchor_x = tmp_image.width//2
            self.block_images_location.append(f"./resources/blocks/{i}")
            self.block_images.append(pyglet.sprite.Sprite(tmp_image, 50,30, batch=self.level_editor_batch, group=self.ledit_gui_order))
            if f"./resources/blocks/{i}" == "./resources/blocks/coin.png":
                self.coin_image_index = index
            index += 1
        index = 0
        self.shuffle_block_images()
    def save_level_to_file(self):
        self.json_blocks = []
        determine_coin = 0
        is_background = False
        for i in self.blocks:
            if i.image_location == "./resources/blocks/coin.png":
                determine_coin = 1
            else: 
                determine_coin = 0
            if i.background_object:
                is_background = 1
            else:
                is_background = 0
            #                         image_location   true_x     true_y      sprite      is(0, false, 1, true) is (0, false, 1, true)  layer (0,1,2,3,4,5, etc)
            #                                          position   position    rotation    background            coin
            self.json_blocks.append([i.image_location, i.true_x, i.true_y, i.sprite.rotation, is_background, determine_coin, i.layer])
        with open(self.editing_map, 'w+') as file:
            if not self.blocks == []:
                file.write("{\n" + f'"name": "{self.level_name}",\n"blocks": [[')
                index = 0
                for i in self.json_blocks:
                    file.write(json.dumps(i[0]))
                    if index < len(self.json_blocks) - 1:
                        file.write(f",{i[1]},{i[2]}, {i[3]}, {i[4]}, {i[5]}, {i[6]}],[")
                    else:
                        file.write(f",{i[1]},{i[2]}, {i[3]}, {i[4]}, {i[5]}, {i[6]}]]")
                    index += 1
                index = 0
                file.write(f',\n"player_start_pos": {self.level_editor_set_spawn}\n' + '}')
            else:
                file.write("{\n"+f'"name": "{self.level_name}",\n'+ '"blocks": [],\n'+f'"player_start_pos": {self.level_editor_set_spawn} ' +'\n}')
        self.json_blocks = []
        for i in self.blocks:
            i.destroy()
        self.blocks = [] #create a block destroying function to destroy blocks
        self.level_buttons = []
        return
    def save_level_and_quit_to_menu(self):
        pyglet.clock.unschedule(self.process_keys_in_level_editor)
        self.save_level_to_file()
        for i in self.level_buttons:
            i.destroy()
        self.editing_level = False
        self.in_menu = False
        self.level_editor_chosen_block_preview_image = object
        self.level_editor_grid_size_pointer = 0
        self.level_editor_grid_blocks_x = []
        self.level_editor_grid_blocks_y = []
        self.level_editor_batch = pyglet.graphics.Batch()
        pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
        self.gamestage = "menu"
    def create_level_editor_menu(self):
        self.level_editor_save_button = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/level_editor_gui/save_button.png")), self.width//2, self.height//2, batch=no_draw_batch, group=self.ledit_menu_order)
    def calculate_grid_lines(self):
        self.level_editor_grid_blocks_x = []
        self.level_editor_grid_blocks_y = []
        try:
            self.width//self.level_editor_grid_sizes[self.level_editor_grid_size_pointer]#check if freehanding or not
            line_index = round(self.width // self.level_editor_grid_sizes[self.level_editor_grid_size_pointer])
            index = 0
            while line_index > index:
                self.level_editor_grid_blocks_x.append(index * self.level_editor_grid_sizes[self.level_editor_grid_size_pointer])
                index += 1
            line_index = round(self.height // self.level_editor_grid_sizes[self.level_editor_grid_size_pointer])
            index = 0
            while line_index > index:
                self.level_editor_grid_blocks_y.append(index * self.level_editor_grid_sizes[self.level_editor_grid_size_pointer])
                index += 1
            index = 0
            self.level_editor_is_freehanding = False
        except ZeroDivisionError:
            self.level_editor_is_freehanding = True
    def edit_level_loader(self, the_map):
        self.level_editor_batch = pyglet.graphics.Batch()
        pyglet.gl.glClearColor(0,0,0,1)
        self.create_level_editor_menu()
        self.zero_point = pyglet.shapes.Rectangle(0,0,1,1,(0,0,0))
        self.editor_crosshair = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/level_editor_gui/crosshair.png")), self.width//2, self.height//2, batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.editor_true_pos = [self.width//2,self.height//2] #the true position of where the center of the level editor is, this will be used to place blocks in the correct place
        self.level_editor_pointer_image = pyglet.image.load("./resources/level_editor_gui/pointer.png")
        self.level_editor_pointer_image.anchor_y = self.level_editor_pointer_image.width // 2
        self.level_editor_grid_size_change_button = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/level_editor_gui/grid_size_button.png")), self.width - 32, 200, batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.second_magic_number_x = 0
        self.second_magic_number_y = 0
        self.level_editor_grid_blocks_x = []
        self.level_editor_grid_blocks_y = []
        self.level_editor_grid_sizes = [64, 32, 16, 0]
        self.level_editor_is_freehanding = False
        self.magic_number_x = self.width
        self.magic_number_y = self.height
        self.level_editor_grid_size_pointer = 0
        self.level_editor_grid_size_button_text = pyglet.text.Label(f'{self.level_editor_grid_sizes[self.level_editor_grid_size_pointer]}',
                                                font_name='Arial',
                                                font_size=12, color=(154,154,154,255),
                                                x=self.level_editor_grid_size_change_button.x, y=self.level_editor_grid_size_change_button.y,
                                                anchor_x='center', anchor_y='center', batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.calculate_grid_lines()
        self.roundedmousex = 0
        self.roundedmousey = 0
        self.block_images = []
        self.block_images_location = []
        self.level_editor_block_set_rotation = 0 #the rotation for when the block is placed
        self.level_editor_layer = 3
        self.level_editor_editing_background = False
        self.block_images_pointer = 0
        self.level_editor_set_spawn = [0,0]
        self.level_editor_chosen_block_preview_image = object
        self.level_name = ""
        self.in_menu = False
        self.editing_map = the_map
        self.level_editor_pointer = pyglet.sprite.Sprite(self.level_editor_pointer_image, self.width//2, 0, batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.block_rotation_label = pyglet.text.Label(f'Block Rotation {self.level_editor_block_set_rotation}',
                          font_name='Arial',
                          font_size=36,
                          x=5, y=self.height - 10,
                          anchor_x='left', anchor_y='top', batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.level_editor_layer_editing_on_label = pyglet.text.Label(f'Layer: 0 (below player)',
                                    font_name='Arial',
                                    font_size=36,
                                    x=self.width - 5, y=self.height - 10,
                                    anchor_x='right', anchor_y='top', batch=self.level_editor_batch, group=self.ledit_gui_order)
        self.level_editor_editing_background_label = pyglet.text.Label('Editing Background',
                                    font_name='Arial',
                                    font_size=36,
                                    x=self.width //2, y=self.height - 10,
                                    anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order)
        self.level_editor_menu_tips = [pyglet.text.Label('Use the scroll wheel to change what block you are using, use left click to place blocks, drag with right click to move around', font_name='Arial', font_size=12, color=(255,255,255,255),x=self.width//2, y=self.height,anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order)]
        self.level_editor_menu_tips.append(pyglet.text.Label('Use the Up and Down arrow to change the layer you are editing on', font_name='Arial', font_size=12, color=(255,255,255,255),x=self.width//2, y=self.level_editor_menu_tips[len(self.level_editor_menu_tips) - 1].y - 20,anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order))
        self.level_editor_menu_tips.append(pyglet.text.Label('Press c to switch to editing background and back, Press Y to set the level spawn point', font_name='Arial', font_size=12, color=(255,255,255,255),x=self.width//2, y=self.level_editor_menu_tips[len(self.level_editor_menu_tips) - 1].y - 20,anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order))
        self.level_editor_menu_tips.append(pyglet.text.Label('Use the left and right arrows to rotate the block you are placing, Press G to reset rotation', font_name='Arial', font_size=12, color=(255,255,255,255),x=self.width//2, y=self.level_editor_menu_tips[len(self.level_editor_menu_tips) - 1].y - 20,anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order))
        self.level_editor_menu_tips.append(pyglet.text.Label('Press F to delete blocks', font_name='Arial', font_size=12, color=(255,255,255,255),x=self.width//2, y=self.level_editor_menu_tips[len(self.level_editor_menu_tips) - 1].y - 20,anchor_x='center', anchor_y='top', batch=no_draw_batch, group=self.ledit_gui_order))
        self.editor_move_speed = 100
        self.editor_rotate_speed = 5
        self.load_block_images()
        self.editing_level = True
        self.level_editor_chosen_block_preview_image = Block(self.block_images_location[self.block_images_pointer], self.width//2, self.height//2,0,0, self.level_editor_block_set_rotation, False, False, self.level_editor_batch, self.layers[self.level_editor_layer])
        pyglet.clock.schedule_interval_soft(self.process_keys_in_level_editor, 1/60.00)
        with open(the_map) as file:
            data = json.load(file)
            self.level_name = data["name"]
            if not data["blocks"] == []:
                self.load_map(the_map, False)
            else:
                pass
            if not data["player_start_pos"] == []:
                self.level_editor_set_spawn = [data["player_start_pos"][0],data["player_start_pos"][1]]
    def resize_gui(self, dt):
        if not self.width == self.dwidth:
            #put functions that only need to be called when on that stage here
            match self.gamestage:
                case "game":
                    self.player.sprite.x = self.width//2
                    self.player.sync_blocks_to_position(self.blocks)
                case _:
                    pass
        try:
            self.title_label.x = self.width // 2
            self.play_button.x = self.width//2
            self.level_editor_button.x = self.play_button.x
            self.quit_button.x = self.play_button.x
        except Exception:
            pass
        try:
            self.level_selector_help_text.x += self.width - self.dwidth
            for i in self.level_buttons:
                i.level_name_text.x += self.width - self.dwidth
                i.sprite.x += self.width - self.dwidth
        except Exception:
            pass
        try:
                self.timer_text.x = self.width
                self.quit_button2.x = self.width//2
        except Exception:
            pass
        try:
                try:
                    self.level_selector_help_text.x += self.width - self.dwidth
                    for i in self.level_buttons:
                        i.level_name_text.x += self.width - self.dwidth
                        i.sprite.x += self.width - self.dwidth
                except Exception:
                    try:
                        self.level_editor_save_button.x = self.width//2
                    except Exception:
                        pass
                    for i in self.level_editor_menu_tips:
                        i.x = self.width//2
                    self.level_editor_editing_background_label.x = self.width//2
                    self.level_editor_grid_size_change_button.x = self.width - self.level_editor_grid_size_change_button.width
                    self.level_editor_grid_size_button_text.x = self.level_editor_grid_size_change_button.x
                    self.calculate_grid_lines()
                    self.level_editor_layer_editing_on_label.x = self.width - 5
                    self.level_editor_pointer.x = self.width // 2
                    self.shuffle_block_images()
                    self.arrange_block_images(True)
                    self.arrange_block_images(False)
                    
                    self.sync_blocks_to_position_for_level_editor(self.blocks)
        except Exception:
            pass
        try:
                self.backboard.x = self.width//2
                self.win_label.x = self.width//2
                self.to_menu_button.x = self.backboard.x
                self.to_menu_label.x = self.to_menu_button.x
        except Exception:
            pass
        try:
                self.splash_screen_title.x = self.width//2
                self.splash_screen_credit.x = self.width//2
                self.splash_screen_credit1.x = self.width//2
        except Exception:
            pass
        self.dwidth = self.width
        if not self.height == self.dheight:
            match self.gamestage:
                case "game":
                    self.player.sprite.y = self.height//2
                    self.player.sync_blocks_to_position(self.blocks)
                case _:
                    pass
        try:
                self.title_label.y = self.height//2 + 200
                self.play_button.y = self.height//2
                self.level_editor_button.y = self.play_button.y - 210
                self.quit_button.y = self.level_editor_button.y - 210
        except Exception:
            pass
        try:
            #level selector
                self.level_selector_help_text.y += self.height - self.dheight
                for i in self.level_buttons:
                    i.level_name_text.y += self.height - self.dheight
                    i.sprite.y += self.height - self.dheight
        except Exception:
            pass
        try:
                self.quit_button2.y = self.height//2
        except Exception:
            pass
        try:
            #level editor
                try:
                    self.level_selector_help_text.y += self.height - self.dheight
                except Exception:
                    self.level_editor_save_button.y = self.height//2
                    for i in self.level_editor_menu_tips:
                        self.level_editor_menu_tips[self.level_editor_menu_tips.index(i) - 1].y - 20
                    self.level_editor_editing_background_label.y = self.height - 10
                    self.level_editor_layer_editing_on_label.y = self.height - 10
                    self.block_rotation_label.y = self.height - 10
                    self.sync_blocks_to_position_for_level_editor(self.blocks)
        except Exception:
            pass
        try:
                self.backboard.y = self.height//2
                self.win_label.y = self.height//2 + 200
                self.to_menu_button.y = self.backboard.y - 200
                self.to_menu_label.y = self.to_menu_button.y
        except Exception:
            pass
        try:
                self.splash_screen_title.y = self.height//2 + 300
                self.splash_screen_credit.y = self.height//2 - 100
                self.splash_screen_credit1.y = self.height//2
        except Exception:
            pass
        self.dheight = self.height
    def start_splash_screen(self):
        pyglet.gl.glClearColor(0.00,0.80,0.27, 1)
        self.splash_screen_title = pyglet.text.Label('AAAAAA',
                                font_name='Arial', bold=True,
                                font_size=96,
                                x=self.width//2, y=self.height//2 + 300,
                                anchor_x='center', anchor_y='center')
        self.splash_screen_credit1 = pyglet.text.Label('Game made by Renato',
                                font_name='Arial', bold=True,
                                font_size=40,
                                x=self.width//2, y=self.height//2,
                                anchor_x='center', anchor_y='center')
        self.splash_screen_credit = pyglet.text.Label('Sounds from pixaby.com and by Pixaby',
                                font_name='Arial', bold=True,
                                font_size=24,
                                x=self.width//2, y=self.height//2 - 100,
                                anchor_x='center', anchor_y='center')
    def remove_splash_screen(self, dt):
        pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
        self.blocks = []
        self.gamestage = "menu"
    def create_new_level(self, filename, level_name):
        with open(os.path.join(os.getcwd(),f"resources/maps/{filename}"), "w") as file:
            file.write("{\n"+f'"name": "{level_name}",\n'+ '"blocks": [],\n'+'"player_start_pos": [0,0]\n}')
            self.level_buttons = []
        return
    def sync_blocks_to_position_for_level_editor(self, blocks):
        for i in blocks:
            i.sprite.x = self.width//2 + (i.true_x - self.editor_true_pos[0]) + 200
            i.sprite.y = self.height//2 + (i.true_y - self.editor_true_pos[1]) + 200
    def music_looper(self, dt):
        if self.gamestage == "menu" and not self.playing_music:
            self.music_player.play()
            self.playing_music = True
        elif not self.gamestage == "menu" and self.playing_music:
            self.music_player.pause()
            self.playing_music = False
    def check_for_dead_particles(self, dt):
        for i in self.particles_active:
            if i.dead:
                self.particles_active.remove(i)
    def initiate_variables(self):
        self.start_splash_screen()
        self.gamestage = "" #the game stages are menu , level_editor, level_select , game , endgame any other value is illegal
        self.level_create_dialog_open = False
        self.editing_level = False
        self.keys_down = []
        self.blocks = []
        self.particles_active = []
        pyglet.clock.schedule_interval_soft(self.check_for_dead_particles, 1/30.00)
        self.gravity_amount = 500
        self.player_timer = 0 #a clock for how long the player takes
        self.paused = False
        self.music_player = pyglet.media.Player()
        self.playing_music = False
        self.coin_image_index = 0
        self.load_batches()
        self.load_groups()
        self.layers = [self.g_low_background_order, self.g_medium_background_order, self.g_high_background_order, self.g_low_above_player_order, self.g_medium_above_player_order, self.g_high_above_player_order]
        self.load_sounds()
        self.music_player.queue(self.menu_loop)
        self.music_player.loop = True
        pyglet.clock.schedule_interval_soft(self.music_looper, 1/30.00)
        self.make_pause_menu()
        self.make_menu()
        pyglet.clock.schedule_once(self.remove_splash_screen, delay=3)
    def initiate_level_editor(self):
        pyglet.gl.glClearColor(0.70,0.47,0,1)
        self.make_level_selector()
    def arrange_block_images(self, right):
        if right:
            self.calc_move_distance = self.width//2 - self.block_images[self.block_images_pointer].x 
            for i in self.block_images:
                i.x += self.calc_move_distance - 10
        else:
            self.calc_move_distance = self.width//2 - self.block_images[self.block_images_pointer].x 
            for i in self.block_images:
                i.x += self.calc_move_distance + 10
    def load_batches(self):
        self.menu_batch = pyglet.graphics.Batch()
        self.game_batch = pyglet.graphics.Batch()
        self.paused_batch = pyglet.graphics.Batch()
        self.level_editor_batch = pyglet.graphics.Batch()
        self.level_select_batch = pyglet.graphics.Batch()
        self.endgame_batch = pyglet.graphics.Batch()
    def load_groups(self):
        self.m_bottom_order = pyglet.graphics.Group(order=-3)
        self.m_middle_order = pyglet.graphics.Group(order=-2)
        self.m_top_order = pyglet.graphics.Group(order=-1)
        self.g_low_background_order = pyglet.graphics.Group(order=1)
        self.g_medium_background_order = pyglet.graphics.Group(order=2)
        self.g_high_background_order = pyglet.graphics.Group(order=3)
        self.g_player_order = pyglet.graphics.Group(order=4)
        self.g_low_above_player_order = pyglet.graphics.Group(order=5)
        self.g_medium_above_player_order = pyglet.graphics.Group(order=6)
        self.g_high_above_player_order = pyglet.graphics.Group(order=7)
        self.g_particle_order = pyglet.graphics.Group(order=8)
        self.g_gui_order = pyglet.graphics.Group(order=9)
        self.ledit_bottom_order = pyglet.graphics.Group(order=10)
        self.ledit_middle_order = pyglet.graphics.Group(order=11)
        self.ledit_top_order = pyglet.graphics.Group(order=12)
        self.ledit_grid_lines_order = pyglet.graphics.Group(order=13)
        self.ledit_block_preview_order = pyglet.graphics.Group(order=14)
        self.ledit_gui_order = pyglet.graphics.Group(order=15)
        self.ledit_menu_order = pyglet.graphics.Group(order=16)
    def on_mouse_scroll(self, x,y, scroll_x, scroll_y):
        if scroll_y > 0:
            #right
            if not self.block_images_pointer > len(self.block_images) - 2:
                self.block_images_pointer += 1
            self.arrange_block_images(False)
            self.level_editor_chosen_block_preview_image = Block(self.block_images_location[self.block_images_pointer], self.level_editor_chosen_block_preview_image.sprite.x, self.level_editor_chosen_block_preview_image.sprite.y,0,0, self.level_editor_block_set_rotation, False, False, self.level_editor_batch, self.layers[self.level_editor_layer])
        else:
            #left
            if self.block_images_pointer > 0:
                self.block_images_pointer -= 1
            self.arrange_block_images(True)
            self.level_editor_chosen_block_preview_image = Block(self.block_images_location[self.block_images_pointer], self.level_editor_chosen_block_preview_image.sprite.x, self.level_editor_chosen_block_preview_image.sprite.y,0,0, self.level_editor_block_set_rotation, False, False, self.level_editor_batch, self.layers[self.level_editor_layer])

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        match self.gamestage:
            case "level_select":
                self.level_selector_help_text.x += dx
                self.level_selector_help_text.y += dy
                for i in self.level_buttons:
                    i.sprite.x += dx
                    i.sprite.y += dy
                    i.level_name_text.x += dx
                    i.level_name_text.y += dy
            case "level_editor":
                if not self.editing_level:
                    self.level_selector_help_text.x += dx
                    self.level_selector_help_text.y += dy
                    for i in self.level_buttons:
                        i.sprite.x += dx
                        i.sprite.y += dy
                        i.level_name_text.x += dx
                        i.level_name_text.y += dy
                else:
                    if button == pyglet.window.mouse.RIGHT:
                        if not self.level_editor_is_freehanding:
                            self.editor_true_pos[0] += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dx / 10)
                            self.editor_true_pos[1] += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dy / 10)
                            self.second_magic_number_x -= self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dx / 10)
                            self.second_magic_number_y -= self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dy / 10)
                            self.zero_point.x += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dx / 10)
                            self.zero_point.y += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dy / 10)
                        else:
                            self.editor_true_pos[0] += dx
                            self.editor_true_pos[1] += dy
                            self.second_magic_number_x -= dx
                            self.second_magic_number_y -= dy
                            self.zero_point.x += dx
                            self.zero_point.y += dy
                        self.level_editor_chosen_block_preview_image.sprite.x = self.roundedmousex
                        self.level_editor_chosen_block_preview_image.sprite.y = self.roundedmousey
                        self.editor_crosshair.x = self.roundedmousex
                        self.editor_crosshair.y = self.roundedmousey
                        for i in self.blocks:
                            if not self.level_editor_is_freehanding:
                                i.sprite.x += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dx / 10)
                                i.sprite.y += self.level_editor_grid_sizes[self.level_editor_grid_size_pointer] * round(dy / 10)
                            else:
                                i.sprite.x += dx
                                i.sprite.y += dy

            case _:
                pass
    def on_key_press(self, symbol, modifiers):
        self.keys_down.append(symbol)
        if modifiers == pyglet.window.key.MOD_WINDOWS:
            self.keys_down = []
        match self.gamestage:
            case "level_select":
                if symbol == pyglet.window.key.ESCAPE:
                    pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
                    self.blocks = []
                    self.level_buttons = []
                    self.gamestage = "menu"
            case "level_editor":
                if self.level_create_dialog_open:
                    match str(symbol):
                        case "65293":
                            self.level_create_dialog_open = False
                            self.create_new_level(f"{self.file_name_text_input.value}.json", f"{self.file_name_text_input.value}")
                            self.file_name_text_input.value = ""
                            self.file_name_text_input = object
                            self.make_level_selector()
                        case "65288":
                            self.file_name_text_input.value = tools.remove_at(len(self.file_name_text_input.value) - 1,self.file_name_text_input.value)
                        case _:
                            if not modifiers == pyglet.window.key.MOD_SHIFT:
                                if not symbol == 65505:
                                    self.file_name_text_input.value += chr(symbol)
                            else:
                                if not symbol == 65505:
                                    self.file_name_text_input.value += chr(symbol).upper()
                if not self.editing_level:
                    if symbol == pyglet.window.key.ESCAPE:
                        pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
                        self.blocks = []
                        self.level_buttons = []
                        self.gamestage = "menu"
                    if symbol == pyglet.window.key.TAB and not self.level_create_dialog_open:
                        self.level_create_dialog_open = True
                        self.file_name_text_input = LevelCreateDialog("", self.width//2, self.height//2, 200, batch=self.level_editor_batch, group=self.ledit_middle_order)
                    elif symbol == pyglet.window.key.TAB:
                        self.level_create_dialog_open = False
                        self.file_name_text_input.value = ""
                        self.file_name_text_input = object
                else:
                    if symbol == pyglet.window.key.Y:
                        self.level_editor_set_spawn = [((self.level_editor_chosen_block_preview_image.sprite.x - self.width//2) + self.editor_true_pos[0]), ((self.level_editor_chosen_block_preview_image.sprite.y - self.height//2) + self.editor_true_pos[1])] #bookmark
                    if symbol == pyglet.window.key.UP:
                        if self.level_editor_layer < len(self.layers) - 1:
                            self.level_editor_layer += 1
                            if self.level_editor_layer >= 3:
                                self.level_editor_layer_editing_on_label.text = f"Layer: {self.level_editor_layer} (above player)"
                            elif self.level_editor_layer < 3:
                                self.level_editor_layer_editing_on_label.text = f"Layer: {self.level_editor_layer} (below player)"
                    if symbol == pyglet.window.key.RIGHT:
                        self.level_editor_block_set_rotation += self.editor_rotate_speed
                        self.level_editor_chosen_block_preview_image.sprite.rotation = self.level_editor_block_set_rotation
                    if symbol == pyglet.window.key.LEFT:
                        self.level_editor_block_set_rotation -= self.editor_rotate_speed
                        self.level_editor_chosen_block_preview_image.sprite.rotation = self.level_editor_block_set_rotation
                    if self.level_editor_block_set_rotation >= 360 or self.level_editor_block_set_rotation <= -360:
                        self.level_editor_block_set_rotation = 0
                        self.level_editor_chosen_block_preview_image.sprite.rotation = 0
                    if symbol == pyglet.window.key.DOWN:
                        if self.level_editor_layer > 0:
                            self.level_editor_layer -= 1
                            if self.level_editor_layer >= 3:
                                self.level_editor_layer_editing_on_label.text = f"Layer: {self.level_editor_layer} (above player)"
                            elif self.level_editor_layer < 3:
                                self.level_editor_layer_editing_on_label.text = f"Layer: {self.level_editor_layer} (below player)"
                    if symbol == pyglet.window.key.C:
                        if not self.level_editor_editing_background:
                            self.level_editor_editing_background = True
                            self.level_editor_editing_background_label.batch = self.level_editor_batch
                        else:
                            self.level_editor_editing_background = False
                            self.level_editor_editing_background_label.batch = no_draw_batch
                    if symbol == pyglet.window.key.ESCAPE:
                        if not self.in_menu:
                            self.in_menu = True
                            self.level_editor_save_button.batch = self.level_editor_batch
                            self.level_editor_layer_editing_on_label.batch = no_draw_batch
                            self.block_rotation_label.batch = no_draw_batch
                            self.level_editor_pointer_image.batch = no_draw_batch
                            self.level_editor_grid_size_change_button.batch = no_draw_batch
                            self.level_editor_grid_size_button_text.batch = no_draw_batch
                            for i in self.block_images:
                                i.batch = no_draw_batch
                            for i in self.level_editor_menu_tips:
                                i.batch = self.level_editor_batch
                        else:
                            self.in_menu = False
                            self.level_editor_layer_editing_on_label.batch = self.level_editor_batch
                            self.block_rotation_label.batch = self.level_editor_batch
                            self.level_editor_pointer_image.batch = self.level_editor_batch
                            self.level_editor_grid_size_change_button.batch = self.level_editor_batch
                            self.level_editor_grid_size_button_text.batch = self.level_editor_batch
                            for i in self.block_images:
                                i.batch = self.level_editor_batch
                            for i in self.level_editor_menu_tips:
                                i.batch = no_draw_batch
                            self.level_editor_save_button.batch = no_draw_batch
                    if symbol == pyglet.window.key.F:
                        for i in self.blocks:
                            if tools.separating_axis_theorem(tools.getRect(self.editor_crosshair), tools.getRect(i.sprite)):
                                self.blocks.remove(i)
                    if symbol == pyglet.window.key.E:
                        if not self.block_images_pointer > len(self.block_images) - 2:
                            self.block_images_pointer += 1
                        self.arrange_block_images(False)
                        self.level_editor_chosen_block_preview_image = Block(self.block_images_location[self.block_images_pointer], self.level_editor_chosen_block_preview_image.sprite.x, self.level_editor_chosen_block_preview_image.sprite.y,0,0, self.level_editor_block_set_rotation, False, False, self.level_editor_batch, self.layers[self.level_editor_layer])
                    if symbol == pyglet.window.key.Q:
                        if self.block_images_pointer > 0:
                            self.block_images_pointer -= 1
                        self.arrange_block_images(True)
                        self.level_editor_chosen_block_preview_image = Block(self.block_images_location[self.block_images_pointer], self.level_editor_chosen_block_preview_image.sprite.x, self.level_editor_chosen_block_preview_image.sprite.y,0,0, self.level_editor_block_set_rotation, False, False, self.level_editor_batch, self.layers[self.level_editor_layer])
                    if symbol == pyglet.window.key.G:
                        self.level_editor_block_set_rotation = 0
            case "game":
                if symbol == pyglet.window.key.ESCAPE:
                    if not self.paused:
                        self.quit_button2.x = self.width//2
                        self.quit_button2.y = self.height//2
                        self.paused = True
                    else:
                        self.paused = False
            case _:
                pass
    def on_resize(self, width, height):
        self.resize_gui(1)
        if self.editing_level and self.gamestage == "level_editor":
            self.edit_level_loader(self.editing_map) #bookmark1
        print(self.blocks)
        pyglet.gl.glViewport(0, 0, *self.get_framebuffer_size())
        self.projection = pyglet.math.Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
    def on_key_release(self, symbol, modifier):
        self.keys_down.remove(symbol)
    def on_mouse_motion(self, x, y, dx, dy):
        match self.gamestage:
            case "game":
                if self.paused:
                    return
                target_rotation = math.degrees(math.atan2(x - self.player.sprite.x, y - self.player.sprite.y)) + 180
                if target_rotation < 360 - self.player.max_angle and target_rotation > 180:
                    self.player.sprite.rotation = 360 - self.player.max_angle
                elif target_rotation > self.player.max_angle and target_rotation < 180:
                    self.player.sprite.rotation = self.player.max_angle
                else:
                    self.player.sprite.rotation = target_rotation
            case "level_editor":
                if not self.editing_level:
                    pass
                else:
                    if not self.level_editor_is_freehanding:
                        index = 0
                        try:
                            for i in self.level_editor_grid_blocks_x:
                                if x  > i and x  > self.level_editor_grid_blocks_x[index + 1]:
                                    self.roundedmousex = i
                                index += 1
                        except IndexError:
                            self.roundedmousex = self.level_editor_grid_blocks_x[len(self.level_editor_grid_blocks_x) - 1]
                        index = 0
                        try:
                            for i in self.level_editor_grid_blocks_y:
                                if y > i and y  > self.level_editor_grid_blocks_y[index + 1]:
                                    self.roundedmousey = i
                                index += 1
                        except IndexError:
                            self.roundedmousey = self.level_editor_grid_blocks_y[len(self.level_editor_grid_blocks_y) - 1]
                        index = 0
                    else: 
                        self.roundedmousex = x
                        self.roundedmousey = y
                    self.editor_crosshair.x = self.roundedmousex
                    self.editor_crosshair.y = self.roundedmousey
                    self.level_editor_chosen_block_preview_image.sprite.x = self.roundedmousex
                    self.level_editor_chosen_block_preview_image.sprite.y = self.roundedmousey
            case _:
                pass
    def on_mouse_press(self, x, y, button, modifiers):
        match self.gamestage:
            case "menu":
                if tools.separating_axis_theorem(tools.getRect(self.play_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                    self.gamestage = "level_select" #change the game stage to a level selector then initiate the level selector
                    self.make_level_selector()
                if tools.separating_axis_theorem(tools.getRect(self.level_editor_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                    self.gamestage = "level_editor"
                    self.initiate_level_editor()
                    #make level editor open here
                if tools.separating_axis_theorem(tools.getRect(self.quit_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                    self.close()
            case "level_select":
                for i in self.level_buttons:
                    if tools.separating_axis_theorem(tools.getRect(i.sprite), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                        self.load_map(i.level_location)
            case "level_editor":
                if not self.editing_level:
                    if not self.level_create_dialog_open:
                        for i in self.level_buttons:
                            if tools.separating_axis_theorem(tools.getRect(i.sprite), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                                self.level_buttons = []
                                self.level_selector_help_text = object
                                self.edit_level_loader(i.level_location)
                    else:
                        if tools.CheckAABBCollision(self.file_name_text_input, pyglet.shapes.Rectangle(x - 2, y - 2, 5,5, (0,0,0))):
                            self.file_name_text_input.value = ""
                else:
                    if self.in_menu:
                        if button == pyglet.window.mouse.LEFT and tools.separating_axis_theorem(tools.getRect(self.level_editor_save_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                            self.save_level_and_quit_to_menu()
                            return
                    if button == pyglet.window.mouse.LEFT and tools.separating_axis_theorem(tools.getRect(self.level_editor_grid_size_change_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                        if not self.level_editor_grid_size_pointer >= len(self.level_editor_grid_sizes) - 1:
                            self.level_editor_grid_size_pointer += 1
                            self.calculate_grid_lines()
                            self.level_editor_grid_size_button_text.text = f"{self.level_editor_grid_sizes[self.level_editor_grid_size_pointer]}"
                            return
                        else:
                            self.level_editor_grid_size_pointer = 0
                            self.calculate_grid_lines()
                            self.level_editor_grid_size_button_text.text = f"{self.level_editor_grid_sizes[self.level_editor_grid_size_pointer]}"
                            return
                    if button == pyglet.window.mouse.LEFT:
                        #if self.block_images_pointer == self.coin_image_index: 
                         #   self.blocks.append(Block(self.block_images_location[self.block_images_pointer], (((self.roundedmousex - self.width //2) + self.editor_true_pos[0]) + (self.width - self.magic_number_x)//2) - self.second_magic_number_x, (((self.roundedmousey - self.height//2) + self.editor_true_pos[1]) + (self.height - self.magic_number_y)//2) - self.second_magic_number_y, self.level_editor_block_set_rotation, self.level_editor_editing_background, True, self.level_editor_batch, self.layers[self.level_editor_layer], self.level_editor_layer))
                        #else:
                        #    self.blocks.append(Block(self.block_images_location[self.block_images_pointer], (((self.roundedmousex - self.width //2) + self.editor_true_pos[0]) + (self.width - self.magic_number_x)//2) - self.second_magic_number_x, (((self.roundedmousey - self.height//2) + self.editor_true_pos[1]) + (self.height - self.magic_number_y)//2) - self.second_magic_number_y, self.level_editor_block_set_rotation, self.level_editor_editing_background, False, self.level_editor_batch, self.layers[self.level_editor_layer], self.level_editor_layer))
                        if self.block_images_pointer == self.coin_image_index: 
                            self.blocks.append(Block(self.block_images_location[self.block_images_pointer], (self.editor_true_pos[0] + (self.editor_crosshair.x - self.width//2)) + self.second_magic_number_x, (self.editor_true_pos[1] + (self.editor_crosshair.y - self.height//2)) + self.second_magic_number_y, 0, 0, self.level_editor_block_set_rotation, self.level_editor_editing_background, True, self.level_editor_batch, self.layers[self.level_editor_layer], self.level_editor_layer))
                        else:
                            self.blocks.append(Block(self.block_images_location[self.block_images_pointer], (self.editor_true_pos[0] + (self.editor_crosshair.x - self.width//2)) + self.second_magic_number_x, (self.editor_true_pos[1] + (self.editor_crosshair.y - self.height//2)) + self.second_magic_number_y, 0, 0, self.level_editor_block_set_rotation, self.level_editor_editing_background, False, self.level_editor_batch, self.layers[self.level_editor_layer], self.level_editor_layer))
                        
                        self.blocks[len(self.blocks) - 1].true_x = self.blocks[len(self.blocks) - 1].sprite.x - self.zero_point.x
                        self.blocks[len(self.blocks) - 1].true_y = self.blocks[len(self.blocks) - 1].sprite.y - self.zero_point.y
            case "game":
                if self.paused:
                    if tools.separating_axis_theorem(tools.getRect(self.quit_button2), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                        self.unschedule_game_functions()
                        self.player_timer = 0
                        self.coins_collected = 0
                        self.paused = False
                        self.blocks = []
                        self.level_buttons = []
                        pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
                        self.gamestage = "menu"
                    return
                if button == pyglet.window.mouse.LEFT:
                    self.player.gravity_enabled = False
                    self.player.y_velocity = 0
                    self.player.x_velocity = 0
                    bullet_move_x = self.player.jump_power * math.cos( math.radians(-self.player.sprite.rotation + 90))
                    bullet_move_y = self.player.jump_power * math.sin( math.radians(-self.player.sprite.rotation + 90))
                    self.player.sprite.y += bullet_move_y
                    self.player.sprite.x += bullet_move_x
                    for i in range(0, 20, 1):
                        self.particles_active.append(Particle(self.player.sprite.x, self.player.sprite.y, random.randrange(round(self.player.sprite.rotation - 15), round(self.player.sprite.rotation + 15)), self.game_batch, self.g_particle_order, self.particles_active))
                    self.jump_sound.play()
                    self.player.gravity_enabled = True
            case "endgame":
                if tools.separating_axis_theorem(tools.getRect(self.to_menu_button), tools.getRect(tools.center_image(pyglet.shapes.Rectangle(x,y, 5, 5, (0,0,0))))):
                    pyglet.gl.glClearColor(0.240, 0.683, 1.00,1)
                    self.blocks = []
                    self.level_buttons = []
                    self.gamestage = "menu"
            case _:
                pass
    def on_draw(self):
        self.clear()
        match self.gamestage:
            case "menu":
                self.menu_batch.draw()
            case "level_select":
                self.level_select_batch.draw()
            case "game":
                self.game_batch.draw()
                if self.paused:
                    self.paused_batch.draw()
            case "level_editor":
                self.level_editor_batch.draw()
            case "endgame":
                self.game_batch.draw()
                self.endgame_batch.draw()
            case _:
                self.splash_screen_title.draw()
                self.splash_screen_credit1.draw()
                self.splash_screen_credit.draw()
class LevelCreateDialog(pyglet.gui.TextEntry):
    def __init__(self, text, x, y, width, color=(255,255,255,255), text_color=(0,0,0,255), caret_color=(255,255,255,255), batch=None, group=None):
        super(LevelCreateDialog, self).__init__("Type file name here", x - width//2,y,width, color, text_color, caret_color, batch, group)
class LevelButton(object):
    def __init__(self, x,y, level_name, level_location, batch):
        self.sprite = tools.center_image(pyglet.shapes.Rectangle(x,y,len(level_name) * 42, 80, (255,255,255,255)))
        self.level_location = level_location
        self.level_name_text =  pyglet.text.Label(f'{level_name}',
                                font_name='Arial',
                                font_size= 70,
                                x=self.sprite.x, y=self.sprite.y,
                                anchor_x='center', anchor_y='center', batch=batch)
    def destroy(self):
        self.sprite.batch = None
        self.sprite.group = None
        self.sprite = None
        self.level_name_text.batch = None
        self.level_name_text = None
        self.level_location = None
        self = None
class Player(object):
    def __init__(self, truex, truey,window_width, window_height, map_blocks, batch, group):
        self.sprite = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load("./resources/ufo/ufo_sprite.png")), window_width // 2, window_height // 2, batch=batch, group=group)
        self.true_x = truex #the true x position
        self.true_y = truey#the true y position
        self.map_blocks = map_blocks
        self.gravity_enabled = True
        self.max_angle = 50
        self.jump_power = 25
        self.x_velocity = 0
        self.y_velocity = 0
        self.sync_blocks_to_position(map_blocks)
    def respawn(self, windowwidth, windowheight):
        self.gravity_enabled = False
        self.x_velocity = 0
        self.y_velocity = 0
        self.sprite.x = windowwidth // 2
        self.sprite.y = windowheight // 2
        self.sync_blocks_to_position(self.map_blocks)
        self.gravity_enabled = True
    def sync_blocks_to_position(self, blocks):
        for i in blocks:
            i.sprite.x = self.sprite.x + (i.true_x - self.true_x) + 200
            i.sprite.y = self.sprite.y + (i.true_y - self.true_y) + 200
class Particle(object):
    def __init__(self, x,y,rotation,batch,group,particle_list, explosion=False):
        """inverts the rotation automatically"""
        if explosion:
            self.sprite = tools.center_image(pyglet.shapes.Rectangle(x,y, 5,5, (random.randrange(230,255), random.randrange(76,110), random.randrange(0,48)), batch, group))
        else:
            self.sprite = tools.center_image(pyglet.shapes.Rectangle(x,y, 5,5, (random.randrange(245,255), random.randrange(245,255), random.randrange(245,255)), batch, group))
        self.speed = 15
        self.dead = False
        self.rotation = rotation
        self.particle_list = particle_list
        pyglet.clock.schedule_interval_soft(self.move_particle, 1/60.00)
        pyglet.clock.schedule_once(self.destroy_object, delay=1)
    def destroy_object(self,dt):
        pyglet.clock.unschedule(self.move_particle)
        self.sprite.batch = None
        self.dead = True
    def move_particle(self,dt):
        self.sprite.x -= self.speed * math.cos( math.radians(-self.rotation + 90))
        self.sprite.y -= self.speed * math.sin( math.radians(-self.rotation + 90))
class Block(object):
    def __init__(self,image,x,y, truex, truey, rotation, isBackground, isCoin, batch, group, layernumber=0):

        try:
            self.sprite = pyglet.sprite.Sprite(tools.center_image(pyglet.image.load(image)), x,y, batch=batch, group=group)
        except TypeError:
            self.sprite = pyglet.sprite.Sprite(tools.center_image(image), x,y, batch=batch, group=group)
        self.image_location = f"{image}"
        self.layer = layernumber
        self.iscoin = isCoin
        self.true_x = truex
        self.true_y = truey
        self.sprite.rotation = rotation
        self.background_object = isBackground
    def destroy(self):
        self.sprite.batch = None
        self.sprite.group = None
        self.sprite = None
        self.image_location = None
        self = None
Main_Window(1000,700, "Funny")

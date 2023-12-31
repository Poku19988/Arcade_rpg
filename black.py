"""
Platformer Game

python -m arcade.examples.platform_tutorial.11_animate_character
"""
import os

import arcade
import time
#music
background_music = arcade.Sound("Music.mp3")
background_music.play(loop = True,volume=0.1)
#Time
start_time = time.time()
# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Platformerr"
TIME_LEFT = 30  # 30 seconds
# Constants used to scale our sprites from their original size
TILE_SCALING = 3
CHARACTER_SCALING = 1
COIN_SCALING = TILE_SCALING
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 0

PLAYER_START_X = SCREEN_HEIGHT//2
PLAYER_START_Y =SCREEN_WIDTH//2

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


LAYER_NAME_PLATFORMS = "walls"
LAYER_NAME_COINS = "coins"
LAYER_NAME_BACKGROUND = "background"
LAYER_NAME_PLAYER = "player"
LAYER_NAME_PASSABLES = "passables"
LAYER_NAME_BACKGROUND2 = "bg2"


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""
    
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        
        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "male_person/"

        # Load textures for idle standing
        
        self.idle_texture_pair = load_texture_pair(f"{main_path}tile000.png")
        # Load textures for standing
        self.idle_textures = []
        self.walk_textures = []
        for i in range(1,13):
            if i<10 :
                texture = load_texture_pair(f"{main_path}tile00{i}.png")
            else :
                texture = load_texture_pair(f"{main_path}tile0{i}.png")
            self.idle_textures.append(texture) #idle
        for i in range(14,20) :
            texture = load_texture_pair(f'{main_path}tile0{i}.png')
            self.walk_textures.append(texture)    #walking
        # Set the initial texture
        self.texture = self.idle_texture_pair[0]
        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.idle_textures[self.cur_texture][
            self.character_face_direction
        ]

        self.cur_texture = 0
        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer for the game
        """
        self.Time = 0
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our 'physics' engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.end_of_map = 0

        # Keep track of the score
        self.time_left = TIME_LEFT
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("coin1.wav")
        self.game_over = arcade.load_sound("gameover1.wav")
        #Time
        self.start_time = time.time()
    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Map name
        map_name = "bg.json"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
        
            
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND : {
                 "use_spatial_hash": True
            },
            LAYER_NAME_PASSABLES :{
                "use_spatial_hash": True
            },
            LAYER_NAME_BACKGROUND2 : {
                "use_spatial_hash": True
            }
        }

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map[LAYER_NAME_BACKGROUND].color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            
            walls=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

        arcade.draw_text(f"Time left: {int(self.time_left)}", SCREEN_WIDTH //2, 0 ,
                         arcade.color.WHITE, font_size=18, anchor_x="center")

        # Draw hit boxes.
        # for wall in self.wall_list:
        #     wall.draw_hit_box(arcade.color.BLACK, 3)
        #
        # self.player_sprite.draw_hit_box(arcade.color.RED, 3)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
       

        # Process up/down when on a ladder and no movement
        if self.up_pressed and not self.down_pressed :
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif  self.down_pressed and  not self.up_pressed :
            self.player_sprite.change_y =-PLAYER_MOVEMENT_SPEED
        else :
            self.player_sprite.change_y = 0
        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        
        else :
            self.player_sprite.change_x = 0
        if self.score ==1 :
            end_text = "You win"
            self.clear()
            
            arcade.draw_text(
            end_text,
            SCREEN_HEIGHT//2,
            SCREEN_WIDTH//2,
            arcade.csscolor.WHITE,
            30,
            )
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key==arcade.key.UP or key == arcade.key.W :
            self.up_pressed = False
       
        if key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered, 0.2)
    
    def on_update(self, delta_time):
        """Movement and game logic"""
        self.process_keychange()
        # Move the player with the physics engine
        self.physics_engine.update()
        
        # Update animations
        self.Time += delta_time
        self.player_sprite.update_animation(delta_time)

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, LAYER_NAME_PLAYER]
        )

        # Update walls, used with moving platforms
    
        self.center_camera_to_player()
        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:

            # Figure out how many points this coin is worth
            
            
            self.score += 1

            # Remove the coin
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
        self.time_left -= delta_time

        # Position the camera
        self.center_camera_to_player()
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 30  :
            self.close()
        




def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()
    

if __name__ == "__main__" :
    main()
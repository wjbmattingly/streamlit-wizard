import streamlit as st
import random
import time

custom_css = """
<style>
    @font-face {
        font-family: 'Endor';
        src: url('https://raw.githubusercontent.com/wjbmattingly/streamlit-wizard/main/ENDOR___.ttf') format('truetype');
    }

    h1, h2, h3, h4, h5, h6, p, .stMarkdown h1, .stMarkdown p {
    font-family: 'Endor', serif;
    color: #3e2723;
}
    table {
        border-collapse: collapse;
        width: 100%;
        border: 4px solid #3e2723;
        background-color: rgba(255, 250, 230, 0.5);
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    td {
        border: 2px solid #3e2723;
        padding: 10px;
        text-align: center;
        font-size: 20px;
        background-color: rgba(255, 250, 230, 0.8);
    }
    .stMarkdown h1, .stMarkdown p {
        color: #3e2723;
    }
</style>
"""


# Injecting the custom CSS into the app
st.markdown(custom_css, unsafe_allow_html=True)

# Constants
SIZE = 10
WIZARD = '🧙'
MONSTER = '👹'
OBSTACLE = '🌲'
POTION = '⚗️'

EMPTY = '☐'
WIZARD_HP = 100
MONSTER_HP = 50

# Initialize the game state
def initialize_game():
    grid = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    wizard_pos = (SIZE // 2, SIZE // 2)
    grid[wizard_pos[0]][wizard_pos[1]] = WIZARD

    # Place random obstacles
    for _ in range(random.randint(5, 15)):
        x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        while grid[x][y] in (WIZARD, MONSTER):
            x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        grid[x][y] = OBSTACLE

    monsters = {}
    for _ in range(random.randint(3, 5)):
        x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        while (x, y) in monsters or grid[x][y] in (WIZARD, OBSTACLE, POTION):
            x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        monsters[(x, y)] = MONSTER_HP
        grid[x][y] = MONSTER
        # Place random potions
    for _ in range(random.randint(1, 3)):
        x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        while grid[x][y] in (WIZARD, MONSTER, OBSTACLE):
            x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        grid[x][y] = POTION
    return grid, wizard_pos, WIZARD_HP, monsters  # Return monsters instead of {MONSTER: MONSTER_HP}

def render_grid(grid):
    table_html = '<table style="border-spacing: 0px;">'
    for row in grid:
        table_html += '<tr>'
        for cell in row:
            table_html += f'<td style="width: 30px; height: 30px; text-align: center; border: 1px solid black;">{cell}</td>'
        table_html += '</tr>'
    table_html += '</table>'
    st.markdown(table_html, unsafe_allow_html=True)

def attack(attacker_hp, defender_hp):
    damage = random.randint(5, 15)
    defender_hp -= damage
    return attacker_hp, max(0, defender_hp)

def move_monsters(grid, monsters):
    directions = ['Up', 'Down', 'Left', 'Right']
    new_monsters = {} # To store the new positions of the monsters

    for (x, y), hp in monsters.items():
        direction = random.choice(directions)
        grid[x][y] = EMPTY

        # Determine new position
        if direction == 'Up' and x > 0: x -= 1
        elif direction == 'Down' and x < SIZE - 1: x += 1
        elif direction == 'Left' and y > 0: y -= 1
        elif direction == 'Right' and y < SIZE - 1: y += 1

        # Check for collisions with obstacles
        if grid[x][y] == OBSTACLE:
            x, y = x, y # Stay in the same position if obstacle

        new_monsters[(x, y)] = hp
        grid[x][y] = MONSTER

    return new_monsters


def move_wizard(grid, wizard_pos, direction, wizard_hp, monsters):
    x, y = wizard_pos
    grid[x][y] = EMPTY

    # Determine new position
    if direction == 'Up' and x > 0: x -= 1
    elif direction == 'Down' and x < SIZE - 1: x += 1
    elif direction == 'Left' and y > 0: y -= 1
    elif direction == 'Right' and y < SIZE - 1: y += 1

    # Check for collisions with monsters
    if grid[x][y] == MONSTER:
        monster_hp = monsters[(x, y)]
        # Wizard attacks monster
        wizard_hp, monster_hp = attack(wizard_hp, monster_hp)
        # Monster attacks wizard
        monster_hp, wizard_hp = attack(monster_hp, wizard_hp)

        # Check if monster is defeated
        if monster_hp <= 0:
            st.success("Monster defeated!")
            grid[x][y] = EMPTY
            del monsters[(x, y)]
        else:
            st.warning(f"Monster attacked! Wizard HP: {wizard_hp}, Monster HP: {monster_hp}")
            monsters[(x, y)] = monster_hp
            x, y = wizard_pos

    elif grid[x][y] == OBSTACLE:
        st.warning("Collision with an obstacle!")
        x, y = wizard_pos
        # Check for collisions with potions
    elif grid[x][y] == POTION:
        heal_amount = random.randint(10, 30)
        wizard_hp = min(WIZARD_HP, wizard_hp + heal_amount)
        st.success(f"Found a potion! Restored {heal_amount} HP!")
        grid[x][y] = EMPTY
    grid[x][y] = WIZARD
    return (x, y), wizard_hp, monsters

# Main game loop
st.title("Wizard World")

if 'grid' not in st.session_state or 'wizard_pos' not in st.session_state or 'wizard_hp' not in st.session_state or 'monsters' not in st.session_state:
    st.session_state.grid, wizard_pos, st.session_state.wizard_hp, st.session_state.monsters = initialize_game()
    st.session_state.wizard_pos = wizard_pos  # Store as a tuple


# Render the grid
st.write(f"Wizard HP: {st.session_state.wizard_hp}")
render_grid(st.session_state.grid)

# Handle movements
directions = ['Up', 'Down', 'Left', 'Right']
# Handle movements
# with st.form(key='movement_form'):
col1, col2, col3 = st.columns(3)

st.write("")  # Just to align the buttons

col2.write("Up")
up_button = col2.button("↑")

st.write("")  # Just to align the buttons

col1, col2, col3 = st.columns(3)

col1.write("Left")
left_button = col1.button("←")

col2.write("Down")
down_button = col2.button("↓")

col3.write("Right")
right_button = col3.button("→")
direction = None

if up_button:
    direction = 'Up'
elif down_button:
    direction = 'Down'
elif left_button:
    direction = 'Left'
elif right_button:
    direction = 'Right'

st.session_state.wizard_pos, st.session_state.wizard_hp, st.session_state.monsters = move_wizard(st.session_state.grid, st.session_state.wizard_pos, direction, st.session_state.wizard_hp, st.session_state.monsters)
 # Force re-run
if up_button or down_button or left_button or right_button:
    # st.session_state.wizard_pos, st.session_state.wizard_hp, st.session_state.monsters = move_wizard(st.session_state.grid, st.session_state.wizard_pos, direction, st.session_state.wizard_hp, st.session_state.monsters)
    # # Move monsters after the wizard moves
    # st.session_state.monsters = move_monsters(st.session_state.grid, st.session_state.monsters)
    time.sleep(.5) 
    st.experimental_rerun()
# Check Wizard's HP after movement
if st.session_state.wizard_hp <= 0:
    st.error("You Died!") # Flash "You Died" message
    time.sleep(2) # Delay to allow the message to be displayed
    # Reset the game
    st.session_state.grid, st.session_state.wizard_pos, st.session_state.wizard_hp, st.session_state.monsters = initialize_game()
    st.experimental_rerun() # Rerun the script to refresh the game

# Check if all monsters are gone
if not st.session_state.monsters:
    st.balloons() # Trigger balloons
    st.success("Congratulations! You have defeated all the monsters!")

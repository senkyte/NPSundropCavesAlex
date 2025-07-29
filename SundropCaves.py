from random import randint
import pygame # im a dramatic guy, i want music.
from random import randint
import time
pygame.mixer.init()
def playmusic(musicfile): # sfx
    pygame.mixer.Channel(0).play(pygame.mixer.Sound(musicfile))
def playmusic2(musicfile): # ost
    pygame.mixer.Channel(1).play(pygame.mixer.Sound(musicfile))

player = {}
original_map = []
global encounteredRuin
global bossBeat
game_map = []
fog = []
winner_list = []
encounteredRuin = False
bossBeat = False

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500
MAX_LOAD = 10

minerals = ['copper', 'silver', 'gold'] # Mineral is tied with pickaxe progression. Each new ore requires the next level of pickaxe. 
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}


prices = {} # prices of each ore
prices['copper'] = (1, 3) 
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)
prices['pickaxe'] = ([50,'silver'],[150,'gold'])

pieces = {} # number of pieces per ore
pieces['copper'] = (1,5)
pieces['silver'] = (1,3)
pieces['gold'] = (1,2)

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(filename, map_struct): # 'For all future references, just treat map_struct as game_map' -alex
    try:  # Validation check of filename.
        map_file = open(filename, 'r')
        map_list = map_file.readlines()
        if not any("T" in line for line in map_list): # Ensures town location is in map
            raise ValueError(f"Your town location (T) is not found on {filename} ! Invalid level map!")
    except FileNotFoundError: 
        print(f"Something went wrong! We can't find {filename}!")
    else:
        global MAP_WIDTH
        global MAP_HEIGHT      
        map_struct.clear()
        
        for i in range(len(map_list)):
            map_struct.append(list(map_list[i].strip("\n")))
        
        MAP_WIDTH = len(map_struct[0])
        MAP_HEIGHT = len(map_struct)

        original_map = map_struct # saves a copy of the game_map before any nodes are gone

        map_file.close()






# This function clears the fog of war at a designated size x size square around the player
def clear_fog(fog, player,size): # Limitation: size MUST be an odd number. I will add an assert that is only meant for potential developers who want to modify my work and not the player -alex 
    assert size % 2 != 0
    player_x = player['x']
    player_y = player['y']
    sizediff = (size - 1)/2 # The range to check, left and right.
    for y in range(player_y - sizediff, player_y + sizediff + 1): # Iterates through every coordinate.
        for x in range(player_x - 1, player_x + 2): 
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT: # Checks if the x pr y coordinate is within 1 of the player
                    fog[y][x] = " "

           

def initialize_game(game_map, fog, player):
    # initialize map
    load_map("level1.txt", game_map)

    # TODO: initialize fog
    fog.clear()
    for i in range(MAP_HEIGHT): # Creates columns
        fog.append(list("?"*MAP_WIDTH)) # Creates rows of fog.
    
    # Looks for the starting coordinate, the town.
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if game_map[y][x] == "T":
                player['x'] = x
                player['y'] = y
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY
    player['load'] = 0
    player['picklevel'] = 0
    player['totalsteps'] = 0
    player['health'] = 100
    player['damage'] = (50,200)
    player['fogclear'] = 3

    clear_fog(fog, player,player['fogclear'])

# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):
    print("+------------------------------+") # Upper border
    for i in range(MAP_HEIGHT): # Iterate through each row and column to fill in the cleared fog with the actual map
        for j in range(MAP_WIDTH): 
            if fog[i][j] == " ":
                fog[i][j] = game_map[i][j]
    fog[player['y']][player['x']] = 'M'
    for i in range(MAP_HEIGHT): # Prints the map.
        print(f"|{"".join(fog[i])}|")
    print("+------------------------------+") # Closing border
    fog[player['y']][player['x']] = ' '

#This function draws the 3x3 viewport
def draw_view(game_map, player):
    print("+---+") # Upper border
    view = [['#' for _ in range(3)] for _ in range(3)]
    view[1][1] = 'M'
    player_x = player['x']
    player_y = player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            x = player_x + dx
            y = player_y + dy
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                if dx == 0 and dy == 0:
                    continue  # Leave the 'M' in the center
                view[dy + 1][dx + 1] = game_map[y][x]
    for row in view:
        print(f"|{''.join(row)}|")
    print("+---+") # Lower border.
        
    
# This function shows the information for the player
def show_information():
    print("----- Player Information -----") # Will deal with later once other features are implemented.
    print(f"Name: {player['name']}")
    print(f"Portal position: ({player['x']},{player['y']})")
    print(f"Pickaxe level: {player['picklevel']} ({minerals[player['picklevel'] - 1]})")
    print("------------------------------")
    print(f"Load: {player['load']} / {MAX_LOAD}")
    print("------------------------------")
    print(f"GP: {player["GP"]}")
    print(f"Steps taken: {player['steps']}")
    print("------------------------------")


# This function saves the game
saved_map = []
saved_fog = []
saved_player = {}
def save_game(game_map, fog, player):
    saved_map = game_map
    saved_fog = fog # save fog
    saved_player = player # save player
    print("Game saved.")
    show_town_menu()
        
# This function loads the game
def load_game(game_map, fog, player):
    game_map = saved_map
    fog = saved_fog
    player = saved_player
    print("Game loaded.")
    show_town_menu()

def show_main_menu():
    playmusic2("introtheme.mp3")
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")
    while True: # Validation check.
        choice = input("Your choice? ")
        if choice.upper() == "N":
            player['name'] = input("Greetings, miner! What is your name? ")
            print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!")
            initialize_game(game_map,fog,player)
            show_town_menu()
            break
        elif choice.upper() == "L":
            load_game(game_map,fog,player)
            break
        elif choice.upper() == "Q":
            print("Goodbye!")
            break
        elif choice.upper() == 'H':
            show_winner()
        else:
            print("Invalid choice! Please enter a valid choice!")

def sell_ores():
    player['day'] += 1
    for i in minerals: # iterates though all minerals
        totalgp = 0
        for j in range(player[i]): # iterates though the number of pieces 
            money = prices[i] # Fetches the rate
            totalgp += randint(money[0],money[1]) # Adds the rate.
        if totalgp != 0:
            print(f"You sell {player[i]} {i} ores for {totalgp} GP.")
            player['GP'] += totalgp
            player[i] = 0
    player['load'] = 0 
    print(f"You now have {player['GP']} GP!")


def win():
    print(
        f'''-------------------------------------------------------------
Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!
You now have enough to retire and play video games every day.
And it only took you {player['day']} days and {player['totalsteps']} steps! You win!
-------------------------------------------------------------'''
    )
    # opens the winner_list
    winnerfile = open("winnerlist.txt","r")
    winner_list = winnerfile.readlines()
    for i in range(len(winner_list)):
        winner_list[i].strip("\n").split(",")
        gp = int(winner_list[-1])
        steps = int(winner_list[-2])
        day = int(winner_list[-3])
        if len(winner_list[i]) > 4: # assuming player tries to be funny and add , in their username
            winner_list[i] = [''.join(winner_list[:-4]),day,steps,gp] # combines the funny username
        

    winner_list.append([player['name'],player['day'],player['totalsteps'],player['GP']]) # add the latest score
    winnerfile.close()

def show_winner(): # Extremely simple show winner code. Horrifically ugly and inefficient, but I cannot use lambda, neither do I know lambda. - alex
    winnerfile = open("winnerlist.txt",'w')
    if len(winner_list) != 0:  
        print("Top Scores:")
        for i in range(len(winner_list)):
            highest_player = ["",9999,9999,0]
            for j in range(len(winner_list)):
                if winner_list[j][1] == highest_player[1]:
                    if winner_list[j][2] == highest_player[2]:
                        if winner_list[j][3] == highest_player[3]:
                            highest_player = winner_list[j]
                        elif winner_list[j][3] > highest_player[3]:
                            highest_player = winner_list[j]
                    elif winner_list[j][2] < highest_player[2]:
                        highest_player = winner_list[j]
                        
                elif winner_list[j][1] < highest_player[1]:
                    highest_player = winner_list[j]
            print(f"{i + 1}. {highest_player[0]}")
            winnerfile.write(f'{highest_player}\n') # adds the player back into the text file.
            winner_list.remove(highest_player)
    else:
        print("There are no winners right now.")
    winnerfile.close()
    
    


def show_town_menu():
    playmusic2("oddlyoptimistictowntheme.mp3")
    player['steps'] = 0
    if player['GP'] >= WIN_GP:
        win()
    else:
        # Display
        print()
        # TODO: Show Day
        print(f"DAY {player['day']}")
        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        print("------------------------")
        while True: # Validation check.
            choice = input('Action? ')
            if choice.upper() == "B":
                show_shop_menu(MAX_LOAD)
                break
            elif choice.upper() == "I":
                show_information()
            elif choice.upper() == "M":
                draw_map(game_map,fog,player)
            elif choice.upper() == "E":
                replenish_node(original_map,game_map)
                playmusic2("miningtheme.mp3")
                show_mine_menu()
                break
            elif choice.upper() == "V":
                save_game(game_map,fog,player)
                break
            elif choice.upper() == "Q":
                show_main_menu()
                break
            else:
                print("Invalid choice! Please enter a valid choice!")


def show_shop_menu(MAX_LOAD):
    print(
        f'''----------------------- Shop Menu -------------------------

Blacksmith: "Ah, welcome adventurer!"
                
(P)ickaxe upgrade to Level {player['picklevel'] + 1} to mine {prices["pickaxe"][player['picklevel']][1]} ore for {prices["pickaxe"][player['picklevel']][0]} GP
(B)ackpack upgrade to carry {MAX_LOAD + 2} items for {MAX_LOAD * 2} GP
(T)orch that that increases the size of the viewport to 5x5 for 50 GP
(C)hat
(L)eave shop
-----------------------------------------------------------
GP: {player["GP"]}
-----------------------------------------------------------
'''  )
    while True:
        choice = input("Your choice? ")
        if choice.upper() == "P":
            if player["GP"] >= prices["pickaxe"][player['picklevel']][0]:
                print(f"Congratulations! You can now mine {prices["pickaxe"][player['picklevel']][1]}!")
                player['GP'] -= prices["pickaxe"][player['picklevel']][0]
                player["picklevel"] += 1
                break
            else:
                print("You don't have enough GP!")
        elif choice.upper() == "B":
            if player['GP'] >= MAX_LOAD * 2:
                MAX_LOAD += 2
                player["GP"] -= MAX_LOAD * 2
                print(f'Congratulations! You can now carry {MAX_LOAD} items!')
                break
            else:
                print("You don't have enough GP!")
        elif choice.upper() == "T": # 10 mark! 10 mark! 10 maark!
            if player['GP'] >= 50:
                print("Congrats! You now own a magic torch that that increases the size of the viewport to 5x5!")
                player["fogclear"] = 5
                player['GP'] -= 50
            else:
                print("You don't have enough money!")
        elif choice.upper() == "C": # just some fun lore dialogue -alex
            print("Blacksmith: 'Well! What would you like to talk about?'")
            print("(1) About the town")
            print("(2) About the blacksmith")
            print("(3) The creator")
            print("(L)eave")
            if encounteredRuin == True:
                print("(?) The ruin?")
            choice = input("Talk? ")
            if choice == "1":
                print("Blacksmith: Ah, a nice peaceful town with a oddly abundant mine that somehow magically replenishes! I hope you enjoy your stay.")
            elif choice == "2":
                print("Blacksmith: Me? Nothing to talk about. I've spent my life helping people like you create stronger pickaxes to help you mine better ores. It's a shame... I was trained to forge weapons in the past...")
            elif choice == "3":
                print("Blacksmith: Ah, you speak of the town's religion. Legend has it that this entire town is nothing but a simulation, created by a god. Once the god has had its fun, we shall all cease to be. How nihilistic!")
            elif choice == "?" and encounteredRuin == True:
                print("Blacksmith: ...so you've encountered the Ruin. It is best you stay far away from that ruin, lest it consume you like it has to other adventurers.")
                time.sleep(2)
                print("Blacksmith: ...Adventurer. Are you willing to venture into the depths? (Y/N)")
                choice2 = input("Your decision. ")
                if choice2 == "Y":
                    print("Blacksmith: Very well. I have an odd feeling about you... Perhaps you will be the one to defeat him.")
                    print("Blacksmith: I will provide you with a weapon... the 10Mark blade. My greatest creation. I will sell it to you for 200 GP.")
                    buyBlade = input("Would you like to buy the 10Mark?(Y/N) ")
                    if buyBlade.upper() == "Y" and player["GP"] >= 200:
                        print("You equiped the 10Mark. It increases your damage!")
                        player["damage"] = (100,300)
                        player['GP'] -= 200
                    elif buyBlade.upper() == "Y" and player["GP"] < 200:
                        print("Blacksmith: Hm? You're broke! Go fetch more GP if you really want this weapon!")
                    else:
                        print("Blacksmith: Hesitating? Talk to me again once you have made your mind.")
                else:
                    print("Best not to dig into it then...")
            else:
                print("Blacksmith: Speak up, adventurer! You're wasting my time!")
        elif choice.upper() == "L":
            break
        else:
            print("Invalid choice! Please enter a valid choice!")
    show_town_menu()



def show_mine_menu():
    game_map[player['y']][player['x']] = " "
    if player['steps'] == TURNS_PER_DAY:
        print("You are exhausted.\nYou place your portal stone here and zap back to town.")
        sell_ores()
        show_town_menu()
    else:
        print('---------------------------------------------------')
        print(f"{'DAY ' + str(player['day']):^50}") 
        print('---------------------------------------------------')
        print(f'DAY {player['day']}')
        draw_view(game_map,player)
        print(f'Turns left:  Load: {player['load']} / {MAX_LOAD}  Steps: {player['steps']}') 
        print("(WASD) to move")
        print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")
        while True: # Validation check.
            choice = input('Action? ')
            if choice.upper() in "WASD":
                move(choice.upper())
                break
            elif choice.upper() == "M":
                draw_map(game_map,fog,player)
            elif choice.upper() == "I":
                show_information()
            elif choice.upper() == "P":
                sell_ores()
                game_map[player['y']][player['x']] = "P"
                show_town_menu()
                break
            elif choice.upper() == "Q":
                show_main_menu()
                break
            else:
                print("Invalid choice! Please enter a valid choice!")

def mine_ore(ore, number,player):
    pieces = randint(number[0],number[1])
    print(f"You mined {pieces} piece(s) of {ore}.")
    if pieces + player['load'] > MAX_LOAD:
        print(f'...but you can only carry {MAX_LOAD - player['load']} more pieces!')
        player[ore] += MAX_LOAD - player['load']
        player['load'] = MAX_LOAD
    else:
        player[ore] += pieces
        player['load'] += pieces
    game_map[player['y']][player['x']] = " "    

def replenish_node(original_map,game_map): # 10 mark! 10 mark! 10 mark! 
    for y in range(len(original_map)):
        for x in range(len(original_map[0])):
            if original_map[y][x] in mineral_names.keys() and game_map[y][x] not in mineral_names.keys():
                chance = randint(1,5)
                if chance == 1: # 20% chance.
                    game_map[y][x] = original_map[y][x] # replenishes node

def move(action): # Validation will be done during choice input. Deals with moving, and also deals with the ores.
    global encounteredRuin
    global bossBeat
    old_x = player['x']
    old_y = player['y']
    if action == 'W': # Dealing with the movement.
        if player['y'] > 0:
            player['y'] -= 1  # Move UP
        else:
            print("Invalid move!")
    elif action == 'S':
        if 0 <= player["y"] < MAP_HEIGHT:
            player['y'] += 1  # Move DOWN
        else:
            print("Invalid move!")
    elif action == 'D':
        if 0 <= player['x'] < MAP_WIDTH:
            player['x'] += 1  # Move RIGHT
        else:
            print("Invalid move!")
    elif action == 'A':
        if player['x'] > 0:
            player['x'] -= 1  # Move LEFT
        else:
            print("Invalid move!")

    if game_map[player['y']][player['x']] in mineral_names.keys(): 
        if player['load'] == MAX_LOAD:
            print("You can't carry any more, so you can't go that way.")
            player['x'] = old_x
            player['y'] = old_y
        else:
            mineral_name = mineral_names[game_map[player['y']][player['x']]] 
            if player['picklevel'] >= minerals.index(mineral_name):
                mine_ore(mineral_name,pieces[mineral_name],player)
            else:
                print("Your pickaxe is too WEAK!")
                player['x'] = old_x
                player['y'] = old_y
    
    if game_map[player['y']][player['x']]  == "Q":
        choice = input("... You see an entrance to a dark cavern...enter? (THIS IS A SIDE QUEST. YOU WILL RETURN BACK TO THE TOWN IF VICTORIOUS.)(Y/N) ")
        if choice.upper() == "Y" and bossBeat == False:
            print("... you jump into the dark cavern.")
            bossFight()
        elif choice.upper() == 'Y' and bossBeat == True:
            print("...there's no point in coming back. The knight is slain.")
            player['x'] = old_x
            player['y'] = old_y
        else:
            print("...you decide to leave it alone.")
            encounteredRuin = True
            player['x'] = old_x
            player['y'] = old_y

    clear_fog(fog,player,player['fogclear']) # Clears the fog around the player
    player['steps'] += 1
    player['totalsteps'] += 1
    show_mine_menu()



# extra bonus alex content: a boss fight!!!! the Q node gives a warning. If the player chooses to proceed, they will encounter the Roaring Knight.

RoaringKnight = {}
RoaringKnight['health'] = 2000
RoaringKnight['damage'] = (5,10)
def playerFight():
    playmusic("slash.mp3")
    damage = randint(player['damage'][0],player['damage'][1])
    RoaringKnight["health"] -= damage
    print(f"You dealt {damage} damage!")
    if damage >= 150:
        print("It's a crit!")

def knightAttack():
    damage = randint(RoaringKnight["damage"][0],RoaringKnight["damage"][1])
    dodge = randint(1,10)
    if dodge != 1:
        print(f"The roaring knight deals {damage} damage.")
        player['health'] -= damage
    else:
        print("... you somehow dodged his attack!")



def playerItem():
    print("You held on to your hopes and dreams...")
    time.sleep(2)
    playmusic("heal.mp3")
    chance = randint(1,4)
    if chance == 1:
        print("...You regained 10 health!")
        player["health"] += 10
    elif chance == 2:
        print("Your determination surged! You regained 15 health!")
        player["health"] += 15
    else:
        print("...you barely regained 5 health.")
        player["health"] += 5


def bossFight():
    playmusic2('crickets.mp3')
    print(
    '''-------------------------------------------------------------
                            A Cold Place
       -------------------------------------------------------------'''
    )
    time.sleep(1)
    print("You have entered a location where you shouldn't have.")
    time.sleep(2)
    print("...")
    time.sleep(2)
    print("Something lurks here.")
    time.sleep(2)
    print(f"{player['name']}: ...?")
    time.sleep(2)
    print("... the roaring knight from deltarune appeared????")
    time.sleep(2)
    print("... here we go!")
    playmusic2("BlackKnife.mp3")
    time.sleep(2)
    print("The Roaring Knight appears.")
    while True:
        if player["health"] <= 0:
            print("... the Knight strikes you down. Your journey... is at an end.")
            break
        print(f'''Player Health: {player['health']} 
                  Knight Health: {RoaringKnight['health']}''')
        print("(A)ttack        (I)tem      (R)un")
        choice = input('What will you do? ')
        if choice.upper() == "A":
            playerFight()
        elif choice.upper() == "I":
            playerItem()
        elif choice.upper() == "R":
            print('You tried to run... but your legs are stuck in fear!')
        else:
            print("You hesitate, your fear overwhelming your decisions...")
        if RoaringKnight["health"] <= 0:
            print("The knight stumbles... he drops a Shadow Crystal. You win! You earned 2000 GP!")
            player['GP'] += 2000
            global bossBeat
            bossBeat = True
            break
        time.sleep(2)
        knightAttack()
    show_town_menu()



#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print(f"How quickly can you get the {WIN_GP} GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")
show_main_menu()    
    

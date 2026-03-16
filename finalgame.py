#Student Name-Maria Rani Mathew
#Student ID-S4111583
#Course Name-Programming Fundamentals(2450)

import csv
import random
import sys
from datetime import datetime

# This is where I defined a custom exception for invalid movements in the game.
# If a player tries to move in a direction that doesn't have a connected location, this exception gets triggered.
class InvalidDirectionException(Exception):
    pass

# I created another exception for handling situations where the input file doesn't match the expected format.
# This makes sure my game doesn't crash when reading bad data from the CSV files.
class InvalidInputFileFormat(Exception):
    pass

# The Item class is for everything you can pick up or interact with in the game.
class Item:
    def __init__(self, name, description, pickable, consumable):# Here, I initialized the details of each item.
        self.name = name # The name of the item
        self.description = description # A short description of the item, just to make it interesting.
        # I made sure that the "pickable" and "consumable" attributes are stored as True/False for easier checks later.
        self.pickable = pickable.lower() == 'yes' 
        self.consumable = consumable.lower() == 'yes' 

    def __str__(self):  
        return self.name # I added this to make items print nicely. For example, if I print an item, it’ll just show its name.

# Next, I created the Location class to represent all the places in the game.
class Location:
    def __init__(self, name, description):
        self.name = name # The name of the location
        self.description = description # A short description for immersion
        # Every location has doors leading in four directions (west, north, east, south).
        # I initially set these doors to None, meaning they don’t connect to any other location yet.
        self.doors = {"west": None, "north": None, "east": None, "south": None}
        self.creatures = [] # I made this list to store creatures present at this location.
        self.items = [] # This list holds all the items available at this location.

    def connect(self, direction, other_location):
        if direction in self.doors:
            self.doors[direction] = other_location # I set the specified door to point to the other location
            # Here, I figured out the opposite direction to make the connection bidirectional.
            opposite = {"west": "east", "north": "south", "east": "west", "south": "north"}[direction]
            other_location.doors[opposite] = self

    def add_creature(self, creature):
        self.creatures.append(creature) # I simply added the creature to the location's list of creatures.

    def add_item(self, item):
        self.items.append(item) # Just added the item to the location's list of items.

# The Creature class is the foundation for all entities like Pymons or other animals in the game.
class Creature:
    def __init__(self, nickname, description, adoptable):
        self.nickname = nickname # Every creature has a nickname, which is basically its identity.
        self.description = description # I added a description to make creatures more engaging and descriptive for the players.
        self.adoptable = adoptable.lower() == "yes" # This adoptable flag determines if the creature can be taken into the player's team.


# The Pymon class represents the main character in the game that the player controls.
class Pymon:
    def __init__(self, nickname="Kimimon", description="I am white and yellow with a square face.", energy=3):# I set a default nickname and description for the Pymon to ensure it's always initialized with some personality.
        self.nickname = nickname# The Pymon's name
        self.description = description # A brief, playful description of the Pymon
        self.adoptable = "yes" # All Pymons are adoptable by default
        self._energy = energy # Energy is the lifeline for the Pymon; it starts with a default of 3
        self._current_location = None # I used this to track where the Pymon currently is
        self.inventory = [] # The inventory holds all the items the Pymon collects
        self.immunity = False # This keeps track of whether the Pymon is immune for a battle
        self.move_count = 0 # I added this to monitor when the Pymon needs an energy check after two moves
        self.battle_stats = [] # This list stores the history of all battles fought by the Pymon

    # I used getter and setter methods (via properties) to control access and enforce constraints on key attributes.
    # I used a property for energy so that I could enforce limits and prevent values outside 0–3.
    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._energy = max(0, min(value, 3))# I made sure that the energy stays between 0 and 3.

    # The current location keeps track of where the Pymon is in the game world.
    @property
    def current_location(self):
        return self._current_location

    @current_location.setter
    def current_location(self, location):
    # When the Pymon moves to a new location, I made sure to remove it from the previous one.
        if self._current_location and self in self._current_location.creatures:
            self._current_location.creatures.remove(self)
        self._current_location = location # Updating to the new location
        location.add_creature(self)  # I added the Pymon to the new location's creature list

    # The spawn method places the Pymon in an initial location at the start of the game.
    def spawn(self, location):
        self.current_location = location

    # The move method handles the Pymon's movement and energy management.
    def move(self, direction):
        # I first check if the direction is valid and there's a door in that direction.
        if self.current_location and direction in self.current_location.doors:
            new_location = self.current_location.doors[direction]
            if new_location:
                self.current_location = new_location# Update the Pymon's location
                self.move_count += 1 # Track the number of consecutive moves
                # After every two moves, the Pymon loses one energy point.
                if self.move_count == 2:
                    self.energy -= 1
                    self.move_count = 0
                    # If energy drops to 0, the Pymon escapes to a random location.
                    if self.energy == 0:
                        print("Your Pymon has run out of energy and escapes into the wild!")
                        self.current_location = random.choice(list(self.current_location.doors.values()))
                        if self.current_location:
                            print(f"Pymon has moved to a random location: {self.current_location.name}")
                        else:
                            print("Game over. No Pymon left to continue.")
                            exit()
                print(f"You traveled {direction} and arrived at {new_location.name}.")
            else:
                raise InvalidDirectionException(f"There is no door to the {direction}.")
        else:
            raise InvalidDirectionException(f"Invalid direction: {direction}.")

        
    # The inspect method allows the player to check the Pymon's details, including energy.
    def inspect(self):
        return f"Hi Player, my name is {self.nickname}, I am {self.description} with energy {self.energy}/3."

    # The pick_item method lets the Pymon collect items from its current location.
    def pick_item(self, item_name):
        # I search for an item with a matching name and ensure it is pickable.
        item = next((item for item in self.current_location.items if item.name.lower() == item_name.lower() and item.pickable), None)
        if item:
            self.inventory.append(item)  # Added the item to the Pymon's inventory
            self.current_location.items.remove(item)# Removed it from the location
            print(f"You picked up a {item_name} from the ground.")
        else:
            print(f"{item_name.capitalize()} cannot be picked up.")


    # This method lets the player view all items currently in the inventory.
    def view_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
            return
        print("Your inventory contains:")
        for index, item in enumerate(self.inventory, start=1):
            print(f"{index}) {item.name}")
            
    # The use_item method allows the Pymon to consume or use items from its inventory.
    def use_item(self, item_name):  # I looked for the specified item in the inventory.
        item = next((item for item in self.inventory if item.name.lower() == item_name.lower()), None)
        if not item:
            print(f"{item_name.capitalize()} is not in your inventory.")
            return
        # Depending on the type of item, different actions are taken.
        if item.consumable and item.name.lower() == "apple":             
            if self.energy < 3:# Apples restore energy but only if energy isn’t already full.
                self.energy += 1
                self.inventory.remove(item)
                print("You ate the apple and gained 1 energy.")
            else:
                print("Your energy is already full.")
        elif item.name.lower() == "potion": # Potions provide temporary immunity for battles.
            self.immunity = True
            self.inventory.remove(item)
            print("You used the potion. You have temporary immunity for the next battle.")
        elif item.name.lower() == "binocular": # Binoculars allow players to scout surrounding areas.
            self.use_binocular()
        else:
            print(f"{item_name.capitalize()} cannot be used.")
            
    # The use_binocular method allows the player to see what’s in nearby locations.
    def use_binocular(self):
        direction = input("Use binocular to view (current, west, north, east, south): ").strip().lower()
        if direction == "current":
            self.describe_location(self.current_location)
        elif direction in self.current_location.doors:
            connected_location = self.current_location.doors[direction]
            if connected_location:
                self.describe_location(connected_location)
            else:
                print(f"This direction leads nowhere.")
        else:
            print("Invalid direction.")
            
    # This method describes the contents of a specific location.
    def describe_location(self, location):  # It lists creatures and items present at the location.
        creatures = ', '.join([creature.nickname for creature in location.creatures]) or "no creatures"
        items = ', '.join([item.name for item in location.items]) or "no items"
        print(f"In {location.name}: Creatures - {creatures}, Items - {items}")
        
    # The battle_outcome method determines the result of each encounter in a rock-paper-scissors game.
    def battle_outcome(self, player_choice, opponent_choice):
    # I created a dictionary to map winning and losing combinations.
        outcomes = {("r", "s"): "win", ("p", "r"): "win", ("s", "p"): "win", ("r", "p"): "lose", ("p", "s"): "lose", ("s", "r"): "lose"}
        if player_choice == opponent_choice:# If both choices are the same, the result is a draw.
            print(f"{player_choice} vs {opponent_choice}: Draw.")
            return "draw"
        result = outcomes.get((player_choice, opponent_choice))# Display whether the player wins or loses based on the choices.
        print(f"{player_choice} vs {opponent_choice}: {'Win' if result == 'win' else 'Lose'}.")
        return result
    
    # The challenge method initiates a battle between the player's Pymon and an opponent.
    def challenge(self, opponent):
        print(f"{opponent.nickname} gladly accepted your challenge! Ready for battle!")
        encounters_won = 0  # Tracks the number of encounters the player wins
        encounters_lost = 0 # Tracks the number of encounters the player loses
        encounters_draw = 0 # Tracks the number of draws
        total_rounds = 0 # I used this to limit the battle to three rounds

        while total_rounds < 3 and self.energy > 0: # The player inputs their choice, and the opponent randomly selects one.
            player_choice = input("Your turn (r)ock, (p)aper, or (s)cissor?: ").lower()
            opponent_choice = random.choice(['r', 'p', 's'])
            outcome = self.battle_outcome(player_choice, opponent_choice)

            if outcome == "win":
                encounters_won += 1 # Increment wins for the player
                print(f"You won 1 encounter.")
            elif outcome == "lose":
                encounters_lost += 1 # Increment losses and reduce the Pymon's energy
                self.energy -= 1
                print(f"You lost 1 encounter and 1 energy.")
            else:
                encounters_draw += 1 # Increment draws
                print("It’s a draw, no points awarded.")
                
            total_rounds += 1
        # At the end of the battle, the result is recorded for future stats.
        battle_record = {
            "timestamp": datetime.now(), # I added a timestamp for each battle for reference.
            "opponent": opponent.nickname, # Records the opponent's nickname.
            "wins": encounters_won,
            "draws": encounters_draw,
            "losses": encounters_lost
        }
        self.battle_stats.append(battle_record) # Append the battle result to the stats list
        # Decide the outcome of the entire battle based on wins and losses.
        if encounters_won > encounters_lost:
            print(f"Congrats! You have won the battle and adopted a new Pymon called {opponent.nickname}!")
        elif encounters_lost > encounters_won:
            print(f"You lost the battle against {opponent.nickname}.")
        else:
            print("The battle ended in a draw. Try again to find a winner!")
            
    # The generate_stats method displays an overview of the Pymon's performance and battle history.
    def generate_stats(self):
    # I included details about the Pymon's current status, like energy and inventory.
        print(f"{self.nickname} Stats:")
        print(f"Energy Level: {self.energy}")
        print(f"Inventory Items: {[item.name for item in self.inventory]}")
        print(f"Current Location: {self.current_location.name}")
        print(f"Immunity Status: {'Active' if self.immunity else 'Inactive'}")

    # If no battles have been fought yet, let the player know.
        if not self.battle_stats:
            print("\nNo battles have been recorded yet.")
        else:
            print("\nBattle History:")
            total_wins, total_draws, total_losses = 0, 0, 0
            # Loop through each battle record and summarize the results.
            for idx, battle in enumerate(self.battle_stats, start=1):
                wins = battle["wins"]
                draws = battle["draws"]
                losses = battle["losses"]
                total_wins += wins # Accumulate wins
                total_draws += draws # Accumulate draws
                total_losses += losses # Accumulate losses
                timestamp = battle["timestamp"].strftime("%d/%m/%Y %I:%M%p") # Format the battle timestamp
                print(f"Battle {idx}, {timestamp} Opponent: {battle['opponent']}, W: {wins} D: {draws} L: {losses}")
            # I ensured the total stats are displayed at the end for an overview.            
            print(f"Total: W: {total_wins} D: {total_draws} L: {total_losses}")

# Record class to handle loading from CSV files
class Record:
    def __init__(self): # I decided to store all locations and creatures in dictionaries for quick access.
        self.locations = {} # Stores all locations with their names as keys.
        self.creatures = {} # Stores all creatures with their nicknames as keys.

    # This method helped to load locations from a CSV file and establishes their connections.
    def load_locations(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                expected_headers = {"name", "description", "west", "north", "east", "south"}# To ensure the file format is correct, I validated the headers.
                if not expected_headers.issubset(set(reader.fieldnames)):
                    raise InvalidInputFileFormat("Invalid location file format. Headers do not match.")
                # First pass: I created Location objects for every entry in the file.
                for row in reader:
                    location = Location(row["name"].strip(), row["description"].strip())
                    self.locations[location.name] = location
                # Second pass: After creating all locations, I connected them based on directions.
                file.seek(0)# To reset the file pointer to the beginning.
                next(reader)# Skip the headers.
                for row in reader:
                    location = self.locations.get(row["name"].strip()) # Retrieve the current location.
                    if location:
                        for direction in ["west", "north", "east", "south"]:# For each direction, I checked if there’s a valid connected location.
                            if row[direction] != "None" and row[direction].strip() in self.locations:
                                location.connect(direction, self.locations[row[direction].strip()])
        except Exception as e:
        # If there’s any issue, I catch the exception and raise a custom error for clarity.
            print(f"Error loading locations: {e}")
            raise InvalidInputFileFormat("An error occurred while loading locations.")

    # This method loads all creatures from a CSV file into the creatures dictionary.
    def load_creatures(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                # For each row, I created a Creature object and stored it by nickname.
                for row in reader:
                    creature = Creature(row["name"].strip(), row["description"].strip(), row["adoptable"].strip())
                    self.creatures[creature.nickname] = creature
        except Exception as e:
        # I ensured that any issue while reading creatures is reported with a custom error.
            print(f"Error loading creatures: {e}")
            raise InvalidInputFileFormat("An error occurred while loading creatures.")

    # This method loads items from a CSV file and places them randomly in existing locations.
    def load_items(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                # For every item in the file, I created an Item object and placed it in a random location.
                for row in reader:
                    item = Item(row["name"].strip(), row["description"].strip(), row["pickable"].strip(), row["consumable"].strip())
                    random_location = random.choice(list(self.locations.values()))
                    random_location.add_item(item) # Added the item to that location.
        except Exception as e:  # If there’s any problem, I raised a custom error with details for easier debugging.
            print(f"Error loading items: {e}")
            raise InvalidInputFileFormat("An error occurred while loading items.")

# Operation class to manage game flow
class Operation:
    def __init__(self): # I created an Operation class to handle the overall game flow and interactions.
        self.record = Record() # Keeps track of all locations, creatures, and items.
        self.pymon = Pymon() # Represents the player's main character in the game.
        self.bench = [] # It stores additional Pymons that the player can swap to.
    # This method sets up the game by loading data from CSV files and initializing the game world.
    def setup_game(self, location_file="locations.csv", creature_file="creatures.csv", item_file="items.csv"):
        """Setup game with custom files for locations, creatures, and items."""
        self.record.load_locations(location_file) # I loaded all locations from the specified file.
        self.record.load_creatures(creature_file) # I loaded all creatures into the game.
        self.record.load_items(item_file) # I randomly placed items across different locations.

        # I added adoptable creatures to the bench, excluding the player's current Pymon.
        for creature in self.record.creatures.values():
            if creature.adoptable and creature.nickname != self.pymon.nickname:
                self.bench.append(creature)
        # I assigned a random starting location for the player's Pymon.
        starting_location = random.choice(list(self.record.locations.values()))
        self.pymon.spawn(starting_location) # I used the spawn method to place the Pymon in the location.

        print("Welcome to Pymon World!") # A friendly welcome message.
        print(f"You started at {self.pymon.current_location.name}.") # Letting the player know their starting point.
    # This method starts the main game loop where the player can interact with the game.
    def start_game(self):
        """Main game loop with command actions."""  # I mapped commands to corresponding methods for modularity and simplicity.
        command_actions = {
            "1": self.inspect_pymon_menu, # Inspect the current Pymon or swap Pymons.
            "2": self.inspect_location,  # Inspect the details of a location.
            "3": self.move_pymon, # Move the Pymon in a specified direction.
            "4": self.pick_item, # Pick up an item from the current location.
            "5": self.view_inventory, # View or use items in the inventory.
            "6": self.challenge_creature,  # Challenge a creature to a battle.
            "7": self.pymon.generate_stats, # Display the player's stats and battle history.
            "8": self.save_game, # Save the current game state.
            "9": self.load_game, # Load a saved game state.
            "10": self.admin_menu, # Access admin features like adding locations or creatures.
            "11": self.exit_game # Exit the game.
        }

        # I created an infinite loop to keep the game running until the player decides to exit.
        while True:
            self.show_menu()  # Display the available commands.
            command = input("Your command: ").strip() # Get the player's input.
            action = command_actions.get(command) # It looks up the corresponding action.
            if action:
                action() # Executing the action if the command is valid.
            else:
                print("Invalid command. Please try again.") # Inform the player about invalid input.

    # This method displays the main menu of commands for the player.
    def show_menu(self):
        """Display game options."""
        print("\nPlease issue a command to your Pymon:") # Encouraging the player to make a choice.
        print("1) Inspect Pymon") # Viewing details of the current Pymon or swap Pymons.
        print("2) Inspect current location") # Learning about the current location.
        print("3) Move") # Moving to an adjacent location.
        print("4) Pick an item") # Picking up an item in the current location.
        print("5) View inventory") # Checking or using items in the inventory.
        print("6) Challenge a creature") # Engaging in a battle with a creature.
        print("7) Generate stats")# Viewing stats and battle history.
        print("8) Save game") # Saving progress to a file.
        print("9) Load game") # Loading progress from a file.
        print("10) Admin Menu") # Access to administrative features.
        print("11) Exit the program") # Exiting the game.

    # This method lets the player inspect their Pymon or swap it with another from the bench.
    def inspect_pymon_menu(self):
        """Menu to inspect or swap Pymons."""
        print("1) Inspect current Pymon")  # Option to view the details of the current Pymon.
        print("2) Swap with a benched Pymon") # Option to swap the current Pymon with another.
        sub_command = input("Choose an option (1 or 2): ").strip()
        if sub_command == "1":
            print(self.pymon.inspect())  # Showing details of the current Pymon.
        elif sub_command == "2" and self.bench:
            self.swap_pymon() # Swaping the current Pymon with another.
    # This method handles the swapping of Pymons from the bench.
    def swap_pymon(self):
        """Swap current Pymon with one from the bench."""
        print("Available Pymons in bench:") # Showing all Pymons available in the bench.
        for idx, pymon in enumerate(self.bench, 1):
            print(f"{idx}) {pymon.nickname} - {pymon.description}") # Displaying each Pymon's details.
        try:
            choice = int(input("Select a Pymon to swap with (enter number): ").strip()) - 1
            if 0 <= choice < len(self.bench): # Validating the player's choice.
                selected_creature = self.bench.pop(choice) # Removing the chosen Pymon from the bench.
                new_pymon = Pymon(nickname=selected_creature.nickname, description=selected_creature.description)
                self.bench.append(self.pymon) # Adding the current Pymon to the bench.
                self.pymon = new_pymon # Replacing the current Pymon with the new one.
                self.pymon.spawn(self.record.locations["School"]) # Spawn the new Pymon in a default location.
                print(f"You have swapped to {self.pymon.nickname}!")  # Notifying the player about the swap.
            else:
                print("Invalid selection.")  # Inform the player about an invalid choice.
        except ValueError:
            print("Please enter a valid number.")  # Handle non-integer inputs gracefully.
    # This method lets the player inspect available locations.
    def inspect_location(self):
        """Inspect available locations."""
        print("Available locations to inspect:") # Let the player know they can choose a location.
        available_locations = list(self.record.locations.keys()) # Retrieving all location names.
        for idx, location_name in enumerate(available_locations, 1):
            print(f"{idx}) {location_name}") # Displaying each location name with a number.

        while True: # I used a loop to ensure valid input is received.
            try:
                choice = int(input("Choose a location to inspect by number: ").strip()) - 1
                if 0 <= choice < len(available_locations): # Validating the choice.
                    location = self.record.locations[available_locations[choice]]
                    break # Exiting the loop once a valid location is chosen.
                else:
                    print("Invalid choice. Please select a valid location number.")
            except ValueError:
                print("Invalid input. Please enter a number corresponding to the location.")

        print(f"You are at {location.name}, {location.description}") # Showing the details of the chosen location.

    # This method allows the player to move their Pymon to a new location.
    def move_pymon(self):
        """Move the Pymon in a specified direction."""
        direction = input("Moving to which direction?: ").strip().lower() # It gets the desired direction.
        try:
            self.pymon.move(direction)  # Using the Pymon’s move method to navigate.
        except InvalidDirectionException as e:
            print(e) # Displaying an error message if the direction is invalid.
    # This method lets the player pick up an item in their current location.
    def pick_item(self):
        """Pick an item at the current location."""
        item_name = input("Picking what: ").strip() # Asks the player for the item's name.
        self.pymon.pick_item(item_name) # Adding the item to the inventory if possible.

    # This method manages the player's inventory, allowing them to view or use items.
    def view_inventory(self):
        """View and use items in the inventory."""
        print("1) View items") # Option to view the current inventory.
        print("2) Use an item")  # Option to use an item from the inventory.
        sub_command = input("Choose an option (1 or 2): ").strip()  # It gets the player's choice.
        if sub_command == "1":
            self.pymon.view_inventory() # Show the items in the inventory.
        elif sub_command == "2":
            item_name = input("Which item would you like to use?: ").strip() # Asks the player which item to use.
            self.pymon.use_item(item_name) # Attempt to use the specified item.
    # This method allows the player to challenge a creature in the current location to a battle.
    def challenge_creature(self):
        """Challenge a creature in the current location."""
        creature_name = input("Challenge who: ").strip() # Asks for the creature's name.
        if creature_name in self.record.creatures: # Checking if the creature exists.
            opponent = self.record.creatures[creature_name] # Retrieving the opponent.
            self.pymon.challenge(opponent) # Initiating the battle with the chosen creature.
        else:
            print(f"{creature_name} is not in this location to challenge.") # Informing the player if the creature isn’t there.
    # This method saves the current game state to a file so the player can resume later.
    def save_game(self, filename="save2024.csv"):
        """Saves the current game state to a CSV file."""
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                # Saving Pymon's details including name, energy, and current location.
                writer.writerow(["Pymon", self.pymon.nickname, self.pymon.energy, self.pymon.current_location.name])
                writer.writerow(["Inventory"] + [item.name for item in self.pymon.inventory])# Saving the items in the inventory.
                writer.writerow(["Battle History"]) # Saving battle history.
                for battle in self.pymon.battle_stats:
                    # Timestamp of the battle, Opponent’s name,Number of wins in the battle,Number of draws in the battle,Number of losses in the battle.
                    writer.writerow([battle["timestamp"].strftime("%d/%m/%Y %I:%M%p"), battle["opponent"], battle["wins"], battle["draws"], battle["losses"]])
                print("Game saved successfully!") # Notifying the player that the game has been saved.
        except Exception as e:
            print(f"Error saving game: {e}") # Handling errors during the save process


    # I created this method to reload the saved game state from a file. This ensures that players can 
    # continue their progress from where they left off, making the game more user-friendly and engaging.
    def load_game(self, filename="save2024.csv"):
        """Loads the game state from a CSV file."""
        try:
            with open(filename, 'r') as file: # Opening the specified file for reading game state data.
                reader = csv.reader(file) # Using CSV reader to parse the file line by line.
                for row in reader:
                    if row[0] == "Pymon": # If the row contains Pymon's data, update Pymon's attributes.
                        self.pymon.nickname = row[1] # Updating Pymon's nickname.
                        self.pymon.energy = int(row[2]) # Updating Pymon's energy level.
                        self.pymon.current_location = self.record.locations.get(row[3], None)   # Setting Pymon's current location by finding it in the record.
                    elif row[0] == "Inventory": # If the row contains inventory data, populate Pymon's inventory.
                        self.pymon.inventory = [        # Creating items from the row data and add them to Pymon's inventory.
                            Item(name=item, description="", pickable="yes", consumable="no") for item in row[1:]
                        ]
                    elif row[0] == "Battle History":  # If the row contains battle history data, recreate the battle stats.
                        self.pymon.battle_stats = [] # Clearing any existing battle stats.
                        for battle_row in reader: # Processing each battle entry.
                            # Here I parsed the timestamp, opponent, and battle outcomes.
                            timestamp = datetime.strptime(battle_row[0], "%d/%m/%Y %I:%M%p")
                            opponent = battle_row[1]
                            wins, draws, losses = int(battle_row[2]), int(battle_row[3]), int(battle_row[4])
                            # Appending the parsed battle record to Pymon's stats.
                            self.pymon.battle_stats.append({
                                "timestamp": timestamp,
                                "opponent": opponent,
                                "wins": wins,
                                "draws": draws,
                                "losses": losses
                            })
                print("Game loaded successfully!")  # Notifying the player that the game state was successfully loaded.

        except FileNotFoundError:
            print("Save file not found.") # Handling the case where the save file doesn't exist.
        except Exception as e:
            print(f"Error loading game: {e}")# Handling any other exceptions during the loading process.

    # This method provides an admin menu for advanced options like adding locations, creatures, or randomizing connections.
    def admin_menu(self):
        """Displays the admin menu for adding custom locations, creatures, and randomizing connections."""
        print("1) Add a custom location") # Option to add a new location.
        print("2) Add a custom creature") # Option to add a new creature.
        print("3) Randomize connections between locations") # Option to shuffle location connections.

        choice = input("Choose an option (1, 2, or 3): ").strip() # Asking the admin for their choice.
        if choice == "1":
            self.add_custom_location() # Calling the method to add a new location.
        elif choice == "2":
            self.add_custom_creature() # Calling the method to add a new creature.
        elif choice == "3":
            self.randomize_connections() # Randomizing connections between locations.

    # This method allows the admin to add a new location and save it to the locations file.
    def add_custom_location(self):
        """Adds a new custom location to the game and saves it to 'locations.csv'."""
        name = input("Enter location name: ").strip() # It gets the name of the new location.
        description = input("Enter description: ").strip() # It gets the description of the new location.
        new_location = Location(name, description) # Creating a new Location object.
        self.record.locations[name] = new_location # Adding the location to the game’s records.
        try:
            with open("locations.csv", "a", newline='') as file:
                writer = csv.writer(file)
                # Writing the new location to the file with default "None" connections.
                writer.writerow([name, description, "None", "None", "None", "None"])
            print("New location added successfully.")  # Informing the admin that the location was added.
        except PermissionError:
            print("Error: Unable to write to 'locations.csv'. Please ensure it is closed and you have write permissions.")

    # This method lets the admin add a new creature and save it to the creatures file.
    def add_custom_creature(self):
        """Adds a new custom creature to the game and saves it to 'creatures.csv'."""
        nickname = input("Enter creature name: ").strip() # It gets the creature's name.
        description = input("Enter description: ").strip() # It gets the creature's description.
        adoptable = input("Is adoptable (yes/no): ").strip().lower() # Checking if the creature can be adopted.
        new_creature = Creature(nickname, description, adoptable) # Creating a new Creature object.
        self.record.creatures[nickname] = new_creature # Adding the creature to the game’s records.
        try:
            with open("creatures.csv", "a", newline='') as file:
                writer = csv.writer(file)
                # Writing the new creature to the file.
                writer.writerow([nickname, description, adoptable])
            print("New creature added successfully.")  # Informing the admin that the creature was added.
        except PermissionError:
            print("Error: Unable to write to 'creatures.csv'. Please ensure it is closed and you have write permissions.")  # Handling file errors.

    # This method randomizes the connections between locations to add unpredictability to the game.
    def randomize_connections(self):
        """Randomizes the connections between all locations."""
        locations = list(self.record.locations.values()) # It gets a list of all locations.
        directions = ["west", "north", "east", "south"] # These are the possible connection directions.

        for location in locations:
            # Clearing existing connections for the location.
            for direction in directions:
                location.doors[direction] = None

            # Randomly assigning new connections to the location.
            connected_locations = random.sample(locations, k=len(directions))
            for direction, connected_location in zip(directions, connected_locations):
                if connected_location != location:  # Avoiding connecting a location to itself
                    location.connect(direction, connected_location)

        print("Connections between locations have been randomized.") # Notifying the admin.

    # This method ends the game session.
    def exit_game(self):
        """Exit the game."""
        print("Exiting the game.") # A simple farewell message given.
        exit() # Terminating the program.

# This is the entry point of the program. I used this block to allow flexibility in how the game files are provided.
# By using command-line arguments, players or admins can specify custom CSV files for locations, creatures, and items.
# If no arguments are provided, it defaults to "locations.csv", "creatures.csv", and "items.csv".
if __name__ == "__main__":
    location_file = "locations.csv" 
    creature_file = "creatures.csv"
    item_file = "items.csv"
# I added this to check if any custom file names are passed via command-line arguments.
    args = sys.argv[1:]
    if len(args) >= 1:   # If at least one argument is provided, use it for the location file
        location_file = args[0]
    if len(args) >= 2:  # If a second argument is provided, use it for the creature file
        creature_file = args[1]
    if len(args) >= 3:  # If a third argument is provided, use it for the item file
        item_file = args[2]
    # I instantiate the Operation class to set up and manage the game.
    game = Operation()
    # This initializes the game with the specified or default files for locations, creatures, and items.
    game.setup_game(location_file, creature_file, item_file)
    # Finally, I start the game, enabling players to interact with the Pymon world.
    game.start_game()

# References
#https://rmit.instructure.com/courses/124829/pages/8-dot-0-week-overview-designing-object-oriented-programs-part-2?module_item_id=6500918
#https://rmit.instructure.com/courses/124829/pages/8-dot-2-1-introducing-constructors?module_item_id=6500924
#https://rmit.instructure.com/courses/124829/pages/9-dot-1-3-making-use-of-inheritance?module_item_id=6500937
#https://rmit.instructure.com/courses/124829/pages/10-dot-1-3-modifying-file-input-output-and-exception-handling?module_item_id=6500957
#https://rmit.instructure.com/courses/124829/pages/10-dot-1-4-adapting-the-financemanagerui-class?module_item_id=6500958


# Assessment of Development
# I aimed to create an interactive and engaging game system by focusing on essential components like locations, creatures, and items.
# Challenges included managing dynamic game elements like randomizing connections, battle mechanics, and state persistence.
# I overcame these challenges by adopting a modular design, which allowed for clean separation of responsibilities across classes.
# Robust exception handling ensured the game could gracefully handle invalid inputs or file errors, providing a seamless player experience.
# Regular testing and iterative refinement allowed me to identify and resolve issues early in development.
# My approach prioritized flexibility and scalability, enabling future extensions such as new game mechanics, customizations, and additional features.


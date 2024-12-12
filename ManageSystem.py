import os  # Import os module for fetching the environment variables.
import shlex  # Import shlex to safely quote user input
import InquirerPy  # Import InquirerPy module for cross-platform and provide a better menus
import datetime  # Import datetime module to get the current date/time of the machine
import prompt_toolkit  # Import prompt_toolkit module mainly to clear the terminal screen.
import sys  # Import sys to exit properly
import colorama  # Import colorama to print colored output
import socket  # Import socket to get IP Address
import netmiko  # Import netmiko to connect to remote machines using SSH
import requests  # Import requests to make web requests


class ManageSystem:
    def __init__(self):
        colorama.init(autoreset=True)  # Initialize colorama for color output

        self.program_running: bool = True  # Initialize program_running to True
        self.day_date: str = ""  # Initialize day_date to empty string
        self.current_time: str = ""  # Initialize current_time to empty string

        self.RED: str = colorama.Fore.RED  # Red Color
        self.CYAN: str = colorama.Fore.CYAN  # Cyan Color
        self.LIGHT_GREEN: str = colorama.Fore.LIGHTGREEN_EX  # Light Green Color
        self.RESET: str = colorama.Fore.RESET  # Reset Color

        self.success: str = f"{self.LIGHT_GREEN}[+]{self.RESET}"  # Append the "[+]" prefix, for successful outputs.
        self.error: str = f"{self.RED}[-]{self.RESET}"  # Append the "[-]" prefix, for unsuccessful outputs.

        self.option_descriptions: dict = {  # The user is supposed to choose an option from the list of 6 elements.
            "1": "Show date and time (local computer)",  # Local date and time on the local computer.
            "2": "Show IP address (local computer)",  # Print the IP address of the local computer.
            "3": "Show Remote home directory listing",  # Print out the listing of the "Home" directory on a remote computer.
            "4": "Backup remote file",  # Create a backup (.old) file in the same directory as the original one.
            "5": "Save web page",  # Access a URL and back up the webpage locally.
            "Q": "Quit",  # Quit the program
        }

        self.actions: dict = {  # Dict to store actions corresponded to the user input
            "1": self.current_date_time,  # 1 -> Execute current_date_time() function
            "2": self.get_local_ipaddress,  # 2 -> Execute get_local_ipaddress() function
            "3": self.list_remote_home_directory,  # 3 -> Execute list_remote_home_directory() function
            "4": self.backup_remote_file,  # 4 -> Execute backup_remote_file() function
            "5": self.save_web_page,  # 5 -> Execute save_web_page() function
            "Q": self.quit_program,  # Q -> Execute quit_program() function
        }
        self.choosable_options: list = [f"{key} - {desc}" for key, desc in self.option_descriptions.items()]  # Use the descriptions to populate the menu shown to the user, use Inline for loop

        self.user_input: InquirerPy.utils.InquirerPySessionResult = ({})  # The user input populated by InquirerPy in the menu() function.

        password: str = self.fetch_environment_variable(
            "PASSWORD"
        )  # Use the fetch_environment_variable function to extract the PASSWORD variable
        username: str = "shashwat"  # hardcoded username
        port: str = "22"  # hardcoded port
        self.ip_address: str = "172.16.29.130"  # hardcoded IP Address

        self.remote_machine: dict = {  # A dict that stores all necessary information to connect to a remote device.
            "device_type": "linux",  # device_type element is set to "linux"
            "host": self.ip_address,  # host element is the FQDN or IP Address of a remote machine
            "port": port,  # port element is the port on which SSH service is listening to.
            "username": username,  # username element to authenticate against the remote machine
            "password": password,  # password element to authenticate against the remote machine
        }
        self.net_connect: any = None  # Initialize & Assign it to None, the type is assigned in establish_ssh_connection function

    @staticmethod
    def format_output(output) -> str:
        """
        Static function to format the output, It should split the command at '%', then remove all unnecessary null bytes and strips line breaks. Should work on default terminals
        """
        return output.split("%")[0].replace("\x00", "").strip()

    def fetch_environment_variable(self, variable: str) -> str:
        """
        Function to fetch information from environment variables.
        """
        try:
            data: str = os.environ.get(variable)  # Read the data from Environment Variables.
            if len(data) == 0:  # If the variable is empty
                print(f"{self.error} Environment Variable {variable} is empty!")  # Print error
                self.quit_program()  # Quit the program
            return data  # return data
        except TypeError:
            print(f"{self.error} Environment Variable doesn't exists!")  # Print error
            self.quit_program()  # Quit the program

    def current_date_time(self) -> None:

        """
        Using the datetime module with various format codes:  https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
            %A: Used to get the weekday (fullname).
            %d: Used to get the day of the month (zero-padded decimal number).
            %B: Used to get the full name of the month.
            %Y: Used to get current Year.
            %X: Used to get current time in 24-hour format (00:00:00).
        """

        self.day_date: str = f"{self.CYAN}{datetime.datetime.now():%A, %d %B %Y}"  # Get the current day and date. (Monday, 01 January 2024) (Color is CYAN)
        self.current_time: str = f"{self.CYAN}{datetime.datetime.now():%X}"  # Get the current time. (24-hour format) (Color is CYAN)

        final_response: str = (f"{self.success} Today is {self.day_date}\n"  # An f-string, used to print current date and day.
            f"{self.success} Current time is {self.current_time}")  # The continuation, appends current time to it.

        print(final_response)  # Print the final_response which is the f-string

    def get_local_ipaddress(self) -> None:

        """
        Using socket module, we create a UDP connection, connect to an external server, and read the local IP Address.
        """

        s: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP using AF_INET (IPv4 Protocol) and SOCK_DGRAM (UDP protocol)
        try:  # Try/Finally block to avoid exceptions and finally close the connection
            s.connect(("8.8.8.8", 80))  # Connect to an external server. The DNS of Google has been used, but no real connection is established.
            ip_address: str = s.getsockname()[0]  # use the function to retrieve the first element which is the IP address used for the connection
        except OSError:  # Check for OSError, indicating issues in internet connectivity.
            print(f"{self.error} Cannot create socket, check internet connection!")  # print the error message
            return  # return nothing
        finally:  # the "finally" block to close the socket
            s.close()  # Close the connection

        final_return: str = f"{self.success} Local IP Address: {self.CYAN}{ip_address}"  # Create an f-string with the IP Address.

        print(final_return)  # return the f-string containing the IP Address

    def establish_ssh_connection(self) -> None:

        """
        Function is used to establish an SSH connection to a remote computer. If the connection is already established, it won't create a new one. Handles three exceptions.
        """

        try:  # try/except block to handle connections and exceptions
            if not self.net_connect:  # If not connected
                self.net_connect: netmiko.BaseConnection = netmiko.ConnectHandler(**self.remote_machine)  # pass remote_machine as dict and open the SSH connection
                self.net_connect.set_base_prompt(pri_prompt_terminator="")
                print(f"{self.success} Successfully Connect to {self.ip_address}.")  # print the output
        except netmiko.exceptions.NetmikoAuthenticationException:  # Authentication Exception, if the credentials passed are incorrect.
            print(f"{self.error} Authentication Failed. Make sure credentials are correct.")  # print the error message
        except netmiko.exceptions.ReadTimeout:  # Read Time Out if the default terminal doesn't match the default terminal configuration. ($ or #)
            print(f"{self.error} Read Timed Out. Make sure the system has the default terminal.")  # print the error message
        except netmiko.exceptions.NetmikoTimeoutException:  # Connection Time Out, if the machine is offline or dropping our requests or listens on different port.
            print(f"{self.error} Timed Out. Make sure the address & port is correct.")  # print the error message

    def execute_command(self, command) -> str:

        """
        Function is used to send command to remote machine using an established connection. The return value is the formatted and stripped output.
        """

        if self.net_connect is not None:  # Check if connection is established
            try:  # try/except block to handle response and exceptions
                output: any = self.format_output(self.net_connect.send_command(command))  # send_command to send the command, capture the output and format it
                return output  # return the formatted and stripped output.
            except netmiko.exceptions.NetmikoAuthenticationException:  # Authentication Exception, if the credentials passed are incorrect.
                print(f"{self.error} Authentication Failed. Make sure credentials are correct.")  # print the error message
            except netmiko.exceptions.ReadTimeout:  # Read Time Out if the default terminal doesn't match the default terminal configuration. ($ or #)
                print(f"{self.error} Read Timed Out. Make sure the system has the default terminal.")  # print the error message
            except netmiko.exceptions.NetmikoTimeoutException:  # Connection Time Out, if the machine is offline or dropping our requests or listens on different port.
                print(f"{self.error} Timed Out. Make sure the address & port is correct.")  # print the error message

    def list_remote_home_directory(self) -> None:

        """
        Function to list home directory on a remote linux machine. Checks if there is already an SSH connection, if not create one.
        """

        command: str = "ls /home/shashwat"  # Command to list home directory
        self.establish_ssh_connection()  # connect to the remote server
        output: any = self.execute_command(command)  # execute the command using execute_function; the return value is output which is formatted.
        if output is not None:  # check if the output is not None
            print(f"{self.success} Remote Server Output:\n{output}")  # Print out the server response

    def backup_remote_file(self) -> None:

        """
        Function to make a backup of a file on a remote device. Has a user input to get the full path of the file. Should print any errors if it occurs.
        """

        file_name: str = input(f"{self.success} Full Enter full path of the file: ")  # User Input to ask for the full path of the file.
        sanitized_file_name: str = shlex.quote(file_name)  # Sanitize the user input to prevent any unintended/malicious Remote Code Execution Vulnerability onto the server
        command: str = f"cp {sanitized_file_name} {sanitized_file_name}.old"  # Command to list home directory
        self.establish_ssh_connection()  # connect to the remote server
        output: any = self.execute_command(command)  # execute the command using execute_function; the return value is output that is formatted.
        if output is not None:  # if the output is not None
            if len(output) == 0:  # check if the length is equal to 0.
                print(f"{self.success} Command executed!")  # Print command executed properly.
            else:  # else if the length of output greater than 0, it usually indicates an error.
                print(f"{self.error} Command execute but following error/output: {output}")  # Print out the error/response

    def save_web_page(self) -> None:

        """
        Function to make an HTTP request and make a copy of response. The url must start with either 'http://' or 'https://'. The HTTP response status is ignored, and only text is stored; binary data is not supported.
        """

        url: str = input(f"{self.success} Enter URL to save the web page: ")  # User input for URL

        if not url.startswith(("http://", "https://")):  # check if the url starts with 'http://' or 'https://'
            print(f"{self.error} Invalid URL. i.e https://example.com'.")  # if it doesn't print the error

        else:  # if the url is proper, then make the request
            if not os.path.exists(
                "Webpages_Backup"
            ):  # Check if the "Webpages_Backup" directory exists
                os.mkdir("Webpages_Backup")  # if it doesn't exist, make one
            try:
                response: requests.Response = requests.get(url)  # Make an HTTP GET request to the url
            except requests.exceptions.ConnectionError:  # Check if there's a Connection Error, indicating the site doesn't exist.
                print(f"{self.error} Cannot connect to the given URL '{url}'.")  # print the error message
                return  # return None
            except Exception as e:  # If any other Exception
                print(f"{self.error} An error occurred while saving the web page: {e}")  # print the error
                return  # return None

            filename: str = url.replace(".", "_")  # replace the '.' with '_' for filename
            filename: str = filename.split("/")[2]  # split at '/' and access the 3rd element, which is the site name
            with open(f"Webpages_Backup/{filename}.html", "w", encoding="utf-8") as file:  # Ignoring the HTTP Status and saving the response to an HTML file inside the WebPages_Backup Directory.
                file.write(response.text)  # Should only work with text, no binary data
            print(f"{self.success} HTML data saved: Webpages_Backup/{filename}.html")  # print out success message

    def quit_program(self) -> None:

        """
        Function to exit/quit the python program, sets the program_running to False before quiting. And then use "sys.exit()" to safely exit the program.
        """

        print(f"{self.success} Quiting...")
        self.program_running: bool = False  # Sets up the program_running to False
        sys.exit(0)  # exit the program safely with error code 0

    def parse_execute_user_input(self) -> None:

        """
        Function that parses user input and executes its corresponding action.
        """

        selected_key: str = self.user_input["selected_option"][0]  # Select the first character of the selected option.

        action: any = self.actions.get(selected_key)  # fetch the action using the selected key

        if action:  # If there is any action associated with the selected key
            action()  # call the function associated with the selected option
        else:  # Else the action is not associated with any selected key
            print(f"{self.error} Invalid option.")  # print error: "Invalid option"

    def menu(self) -> None:

        """
        Using the InquirerPy module to create a choosable_menu that displays six options. User is supposed to choose anyone.
        """

        choosable_menu: list = [  # Define the choosable_menu configuration as a list of dictionaries
            {
                "type": "list",  # The type of input is a list where users can select one option.
                "message": "Please Select an Option To Continue:",  # The message to display above the choosable_menu options.
                "choices": self.choosable_options,  # Use the generated choosable_options list for choices
                "name": "selected_option",  # A unique identifier for this prompt to reference the selected option
            }
        ]
        self.user_input = InquirerPy.prompt(choosable_menu)  # Parse the user input and store it in `user_input`

    def main(self) -> None:

        """
        The main function to combine all features and function.
        """

        try:  # Try/Except block for error/interprets handling
            while self.program_running:  # Loop until user select Quit option
                self.menu()  # Display the menu
                self.parse_execute_user_input()  # parse and execute user selected option

                input(f"{self.RED}[!]{self.RESET} Press any key to continue...")  # The input function to allow user to select another functionality
                prompt_toolkit.shortcuts.clear()  # Clear the screen for the user

        except KeyboardInterrupt:  # Detect "CTRL + C" and safely quit the program.
            print(f"{self.RED}[!]{self.RESET} KeyboardInterrupt detected!")  # Print the detection.


if __name__ == "__main__":
    manage_system = ManageSystem()  # Initialize the ManageSystem class
    manage_system.main()  # Execute the main function of ManageSystem class.

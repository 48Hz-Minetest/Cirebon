import pico
import sys

registers = {
    'A': 0, 'B': 0, 'C': 0, 'D': 0
}
constants = {}
stack = []
channels = {}
current_channel = None

flags = {
    'EQUAL': False
}

def tokenize(code):
    tokens = []
    lines = code.strip().split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith(';'):
            tokens.append(stripped_line.split())
    return tokens

def find_labels(tokens):
    labels = {}
    for i, line_tokens in enumerate(tokens):
        if line_tokens[0].endswith(':'):
            label_name = line_tokens[0][:-1]
            labels[label_name] = i
    return labels

def execute(tokens, labels):
    global registers, constants, stack, channels, current_channel, flags
    
    ip = 0
    while ip < len(tokens):
        line_tokens = tokens[ip]
        command = line_tokens[0].lower()

        try:
            if command.endswith(':'):
                ip += 1
                continue

            elif command == 'mov':
                target_reg = line_tokens[1].upper()
                source = line_tokens[2]
                
                if source.isdigit() or (source.startswith('-') and source[1:].isdigit()):
                    registers[target_reg] = int(source)
                elif source.upper() in registers:
                    registers[target_reg] = registers[source.upper()]
                elif source in constants:
                    registers[target_reg] = constants[source]
                else:
                    print(f"Error: Unknown source '{source}'")
                    break

            elif command == 'add':
                target_reg = line_tokens[1].upper()
                source_reg = line_tokens[2].upper()
                registers[target_reg] += registers[source_reg]

            elif command == 'sub':
                target_reg = line_tokens[1].upper()
                source_reg = line_tokens[2].upper()
                registers[target_reg] -= registers[source_reg]

            elif command == 'mul':
                target_reg = line_tokens[1].upper()
                source_reg = line_tokens[2].upper()
                registers[target_reg] *= registers[source_reg]

            elif command == 'div':
                target_reg = line_tokens[1].upper()
                source_reg = line_tokens[2].upper()
                if registers[source_reg] == 0:
                    print("Error: Division by zero.")
                    break
                registers[target_reg] //= registers[source_reg]

            elif command == 'const':
                const_name = line_tokens[1]
                # Check if the value is a string (starts with " and ends with ")
                if line_tokens[2].startswith('"') and line_tokens[-1].endswith('"'):
                    value = ' '.join(line_tokens[2:]).strip('"')
                    constants[const_name] = value
                else:
                    value = int(line_tokens[2])
                    constants[const_name] = value

            elif command == 'push':
                source = line_tokens[1]
                if source.upper() in registers:
                    stack.append(registers[source.upper()])
                else:
                    stack.append(int(source))

            elif command == 'pop':
                target_reg = line_tokens[1].upper()
                if not stack:
                    print("Error: Stack is empty.")
                    break
                registers[target_reg] = stack.pop()
            
            elif command == 'chadd':
                channel_name = line_tokens[1]
                if channel_name not in channels:
                    channels[channel_name] = []
                else:
                    print(f"Warning: Channel '{channel_name}' already exists.")

            elif command == 'chdel':
                channel_name = line_tokens[1]
                if channel_name in channels:
                    del channels[channel_name]
                    if current_channel == channel_name:
                        current_channel = None
                else:
                    print(f"Error: Channel '{channel_name}' does not exist.")
                    break

            elif command == 'chswitch':
                channel_name = line_tokens[1]
                if channel_name in channels:
                    current_channel = channel_name
                else:
                    print(f"Error: Channel '{channel_name}' does not exist.")
                    break

            elif command == 'chin':
                if current_channel is None:
                    print("Error: No active channel.")
                    break
                source = line_tokens[1]
                if source.upper() in registers:
                    channels[current_channel].append(registers[source.upper()])
                elif source in constants:
                    channels[current_channel].append(constants[source])
                else:
                    print(f"Error: Unknown source '{source}'.")
                    break

            elif command == 'chout':
                if current_channel is None:
                    print("Error: No active channel.")
                    break
                if not channels[current_channel]:
                    print(f"Error: Channel '{current_channel}' is empty.")
                    break
                value = channels[current_channel].pop(0)
                print(f"--> Output from channel '{current_channel}': {value}")

            elif command == 'chmov':
                if current_channel is None:
                    print("Error: No active channel.")
                    break
                if not channels[current_channel]:
                    print(f"Error: Channel '{current_channel}' is empty.")
                    break
                target_reg = line_tokens[1].upper()
                value = channels[current_channel].pop(0)
                registers[target_reg] = value
            
            elif command == 'prt_reg':
                reg_name = line_tokens[1].upper()
                if reg_name in registers:
                    print(f"--> Register '{reg_name}': {registers[reg_name]}")
                else:
                    print(f"Error: Unknown register '{reg_name}'.")
                    break
            
            elif command == 'prt_str':
                const_name = line_tokens[1]
                if const_name in constants and isinstance(constants[const_name], str):
                    print(f"--> String output: {constants[const_name]}")
                else:
                    print(f"Error: Constant '{const_name}' is not a string.")

            elif command == 'cmp':
                reg1 = line_tokens[1].upper()
                reg2 = line_tokens[2].upper()
                flags['EQUAL'] = (registers[reg1] == registers[reg2])
                
            elif command == 'jmp':
                label = line_tokens[1]
                if label in labels:
                    ip = labels[label]
                else:
                    print(f"Error: Unknown label '{label}'.")
                    break
            
            elif command == 'je':
                label = line_tokens[1]
                if flags['EQUAL']:
                    if label in labels:
                        ip = labels[label]
                    else:
                        print(f"Error: Unknown label '{label}'.")
                        break
            
            elif command == 'jne':
                label = line_tokens[1]
                if not flags['EQUAL']:
                    if label in labels:
                        ip = labels[label]
                    else:
                        print(f"Error: Unknown label '{label}'.")
                        break
            
            else:
                print(f"Error: Unknown command '{command}'")
                break

            ip += 1

        except IndexError:
            print(f"Error: Incomplete command '{command}'")
            break
        except KeyError as e:
            print(f"Error: Unknown register, constant, or channel: {e}")
            break
        except Exception as e:
            print(f"An execution error occurred: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        while True:
            terminput = input("Cirebon >>> ")
            if terminput == "q" or terminput == "quit" or terminput == "exit":
                break
            elif terminput == "echo":
                echoinput = input("echo >>> ")
                print(f"--> String output: {echoinput}")
            elif terminput == "pico":
                pico.mode()
            elif terminput == "help" or terminput == "helpme" or terminput == "h":
                print("**********************************")
                print("Help:")
                print("q/quit/exit     exit cirebon shell")
                print("help/helpme/h   display this menu")
                print("echo            put string")
                print("pico            install Pico")
                print("**********************************")
                print("Cirebon 1.2                 Stable")
                print("MIT License")
                print("Copyright (c) 2025 48Hz")
                print("**********************************")
                print("Say Hi!                         :D")
            else:
                print("Error: Invalid command.\nUse 'help', 'helpme' or 'h' to get help.")
    else:
        file_path = sys.argv[1]
        if not file_path.endswith('.cire'):
            print("Error: Invalid file extension. Expected '.cire'.")
            sys.exit(1)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
                tokens = tokenize(code)
                labels = find_labels(tokens)
                execute(tokens, labels)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred while reading or executing: {e}")

import re
import sqlite3

# File names
input_filename = 'mysql_dump.sql'  # replace with your file name
output_filename = 'sqlite.db'  # replace with desired SQLite DB name

# Open MySQL dump file and SQLite3 DB
with open(input_filename, 'r') as f_input, sqlite3.connect(output_filename) as conn:
    cursor = conn.cursor()

    # A buffer for multi-line SQL commands
    command_buffer = ''

    # Loop through each line in the SQL file
    for line in f_input:
        # Skip comments, SET, LOCK and UNLOCK commands
        if re.match(r'(--.*)|(\/\*.*)|(SET.*)|(LOCK TABLES.*)|(UNLOCK TABLES.*)|(ALTER TABLE.*)', line):
            continue

        # Append line to the buffer
        command_buffer += line

        # If the line ends with a semicolon, it's the end of the command
        if re.search(r';\s*$', line):
            command_buffer = command_buffer.replace('),(', '),\n(')

            # MySQL to SQLite replacements
            command_buffer = re.sub(r'`', '', command_buffer)  # replace ` with nothing
            command_buffer = re.sub(r' AUTO_INCREMENT', '', command_buffer)  # remove AUTO_INCREMENT
            command_buffer = re.sub(r' unsigned', '', command_buffer)  # remove unsigned
            command_buffer = re.sub(r' int\([0-9]+\)', ' INTEGER', command_buffer)  # replace all int(X) with INTEGER
            command_buffer = re.sub(r' ENGINE=.*', '', command_buffer)  # remove all after ENGINE=
            command_buffer = re.sub(r',\s+UNIQUE KEY .* \((.*)\)', r', UNIQUE(\1)',
                                    command_buffer)  # replace UNIQUE KEY with comma before
            command_buffer = re.sub(r' UNIQUE KEY .* \((.*)\)', r' UNIQUE(\1)',
                                    command_buffer)  # replace UNIQUE KEY without comma before

            # Convert MySQL specific commands to SQLite
            command_buffer = re.sub(r'IF NOT EXISTS', '', command_buffer)
            command_buffer = re.sub(r'DEFAULT CHARSET=latin1', '', command_buffer)

            # Handle backslash escaping for SQLite
            command_buffer = command_buffer.replace("\\'", "''")
            command_buffer = command_buffer.replace('\\"', '""')

            # Fix :/ and /!\
            command_buffer = command_buffer.replace(":\\''", ":\\'")
            command_buffer = command_buffer.replace("/!\\''", "/:\\'")

            # Execute each command (continue on error)
            try:
                cursor.execute(command_buffer)
            except sqlite3.Error as e:
                print(f'Error message: {e.args[0]}')
                for i, line in enumerate(command_buffer.split('\n'), start=1):
                    print(f'Line {i}: {line}')

            # Clear the command buffer
            command_buffer = ''

    # Commit changes and close
    conn.commit()

print('MySQL to SQLite conversion complete!')

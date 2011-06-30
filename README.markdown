Simplici7y 
==========

> "Welcome to the Marathon" -Leela

Getting Started
---------------

+ Change directory into Simplici7y
+ Create a database ( "Simplici7y" is the default )
+ Rename config/example_database.yml to config/database.yml
+ Configure your local database settings in new database.yml file
+ Initialize database: rake db:schema:load
+ Add required gems: rake gems:install
+ Start the web server: script/server (run with --help for options)
+ Go to http://localhost:3000/ and get a simple Simplici7y homepage.

If you had any problems, please let me know so I can add it here.

For hourly, daily and monthly download rankings, add the following line to cron, substituting your own installation paths.

    7 * * * * /usr/bin/env ruby /var/www/Simplici7y/script/runner /var/www/Simplici7y/app/hourly.rb

Pushing Live
------------

When you push the project live, be sure to protect these files:

+ /tmp/
+ /config/
+ /public/version/
+ /public/screenshot/

and ignore these files:

+ /log/

Then restart the application: touch Simplici7y/tmp/restart.txt
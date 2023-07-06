Simplici7y 
==========

Simplici7y is a file sharing web application for the Aleph One community. Originally written in with Ruby on Rails 1.0 and hosted alongside The Pfhorums, Simplici7y is now a Django 4 Application deployed to Heroku from Github.

The project is named after a 7-polygon mapping challenge, which focuses on doing more with less.

When Fileball suffered downtime in early 2007, Jon Irons saw the need to fill the gap as soon as possible. He came to me with his idea for a new project. Jon's support was fundamental to the development and successful launch of Simplici7y, and I consider this project his as much as it is mine.

Simplici7y came online on the second anniversary of The Pfhorums. After Fileball was destroyed in a fire, S7 became the de facto place to publish. In the 16 years it has been online, there have been over 12 million downloads, 600 items and 1,400 reviews.

## Contributing

Contributions are welcome. Please open an issue or pull request. If you have any questions, [contact me on the Discord](https://discord.gg/VpwMyeFd).

### Minimum `.env` file:

```
DEBUG=True
DJANGO_SECRET_KEY='secret'
```

### Scripts:

- `./scripts/bootstrap.sh`: Set up local dev environment
- `./scripts/server.sh`: Run server
- `./scripts/format.sh`: Format code
- `./scripts/migrate.sh`: Create and run migrations

# Arceus, the Discord bot for PTU

Arceus is a bot for Discord servers that provides several features for playing the PTU (Pokemon Tabletop United) RPG.

Use the following link to add the bot to your server:
https://discord.com/api/oauth2/authorize?client_id=836726415016984586&permissions=109632&scope=bot

## Features
* Displays the sprite for any pokemon, retrieved from the Poke API (https://pokeapi.co/). Includes shinies and megas.
* Connects to each player's automated character sheet on Google Sheets, which can be found at (https://pokemontabletop.com/downloads-and-resources/)
* Displays stats for trainers and pokemon from their character sheets
* Rolls skill checks for trainers and pokemon
* Rolls move accuracy and damage for trainers and pokemon

## How to use
* To add a spreadsheet, a player must first share the spreadsheet in Google Drive with ptu-spreadsheet-bot@arceusbot-312120.iam.gserviceaccount.com
* Then link the sheet with your discord account by calling this command in your server: "*link [spreadsheet name]" where the spreadsheet name is the name of your document in
Google Drive
* Note that the worksheet name for each pokemon should be the same as their chosen name

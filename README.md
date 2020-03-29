## Table of contents
* [General Info](#recipe-costing-app)
* [Motivation](#motivation)
* [Demo](#demo)
* [Built with](#built-with)
* [Features](#features)
* [Installation](#installation)
* [Setup](#setup)

# Recipe Costing App

A web app which takes user's input and generates recipe costing sheets in Google Sheets. The app renders selected information from the Google Sheets (e.g ingredients, recipe groups, units). This repository has a ready-to-copy-paste google sheet template that you need in order to run the application. 
Currenlty the app is compatible only with Google Chrome. 

# Motivation 

# Demo 
Demo
Download demo ![here](https://imgflip.com/gif/3uitbi)

Screnshots availabe here
# Built with
  - Python
  - JavaScript
  - Flask
  - gspread
  - HTML
  - CSS
  - Bootstrap
  
# Features
This application makes it easy to:
  - Efficently cost recipes
  - Generate Google Sheets with the provided templates and create more organized and consistent database for your costing needs 
  - Select ingredients directly from the database in Google Sheets
  - Add new ingredients & recipe groups (sheets) directly from the web portal
  - Restrict access to specific users with the authentication feauture
  
  
# Installation & Usage 
 **To Install**

```$ git clone https://github.com/skarmen/recipe-costing-app/```

**To Run**
```
$ cd recipe-costing-app
$ python3 wsgi.py
```


# Setup

**I. Set up your Google Sheet**

   1. Get the Google Sheet template [here](https://docs.google.com/spreadsheets/d/1MuhTdjDZ0N3soA6olJ68aufQbpo5-fZzQgc5v-M-K6s/edit?usp=sharing)
   2. Make a copy of the template and add it you Google Drive
   3. Rename your new file as you wish & start adding ingredients and categories to it
   4. Go to the ***spreadsheet.py*** file, find the variable ***SHEET_NAME*** and assigned it your new spreadsheet name (e.g     ***SHEET_NAME = “My Recipe Costing App”***). You will need to repeat this step every time the spreadsheet name is changed. 
   5. Changes to the Google Sheet 
      - **Important Dependencies**
          - Column *PRICE* at *CATEGORY* row, in *INGREDIENT COST* sheet in should be empty at all times
          - Submitted ingredients will be added as an ingredient after the last *empty line* in *INGREDIENT COST* sheet. Reccomend creating a category at the end of the sheet named "Recipes from the portal" 
          - If you need to rename the pre-existing sheet names (e.g *INGREDIENT COST*, *recipe-template*) they must be changed throughout ***spreadsheet.py***.
          - **Any other changes to the pre-existing sheet templates will cause the app to break**     

 
**II. Google Sheet Authenitcation** 

Once you have set up the recipe template sheet you need to configure your Google Sheet Authentication. 
To programatically access your spreadsheet, you will need to create a service account and credentials from the [Google APIs console](https://console.developers.google.com/apis/).

   1. Go to the [Google APIs console](https://console.developers.google.com/apis/)
   2. Create a new project 
   3. Click ***Enable APIs and Services*** , search for and enable Google Drive API 
   4. Go to ***Credentials > Create Credentials > Help Me choose*** 
   5. Select the following: (credentials for a ***Web Server*** to access ***Application Data***) 
       - ***Google Drive API*** 
       - ***Web Server (e.g node.js, Tomcat)***
       - ***Application Data***
       - ***No, I’m not using them*** 
  6. Crate a name for the service account and grant it a ***Project*** Role of ***Editor***
  7. Download the JSON file 
  8. Rename the file to *client_secret.json* and copy it to your code directory 
  9. Find the *client_email* inside the *client_secret.json* and copy the email 
  10. Go to your spreadsheet and click the ***Share*** button and paste the client email & send. This will give the app edit rights for that sheet.
 
With all credentials in place, there is one last step to set up your google sheet with the app. 

**III. HTTP Authentication** 

You can grant access to the web application by updating the username and password in the ***.env** file. This is only basic HTTP auth with Flask. 
  1. From the repository open ***.env** 
  2. Update the username and password credentials 
  ```
  RECIPE_USER=username
  RECIPE_PASSWORD=password
  ```

With all the credentials in place, you can now run the application. 




# MealPlan - A Meal Planning Website
#### Video Demo: https://youtu.be/2SXgrkl9fME
#### Project description:
This website allows user to create recipes and add them to meal plans. The meal plans automatically create the necessary grocery list given the list of recipes and ingredients for them.

To begin create an account and log in.

On the home page you see the overview of his meal plans and recipes. To create a new recipe or plan click a corresponding "Create" button. To see the full list of plans or recipes click "See all" and the respected section.

To view the recipe clcik on the card. In the opened page you can see the ingredient list and method as well as edit or delete this recipe.

To view the meal plan click on the corresponding card. In the opened page you can see the grocery list as well as selected recipes and information about the meal plan. You can also edit or delete the meal plan on this page.

#### Contained files:
**app.py** is the main apploication code
**helper.py** contains additional functions used in the main code
**recipes.db** is the database used by the website which contains recipes and meal plans of all users.
**static** contains css styles for the website. Note that the website also uses a number of Bootstrap styles.
**templates** contains templates for all pages in the project. Note that **layout.html** and **layout_recipe.html** contain the wrapper html for the rest of the pages, including menu and footer bars, headers and javascript functions.

#### Development details:
I have background in design, so I first develpped the UX design for this project. You can find the desired look on https://bogdanova.de/copy-of-animal-hospital-1
Unfortunately my knowledge of front end development was not emough to fully implement the design, but I managed to closely mimic it with BootStrap and additional css styles. Creating beautiful web pages proved to be the most difficult part of the project and some design ideas were never implemented.
In terms of the back-end development I went through various iterations of the database so that it could contain all the necessary information. It was also an interesting challenge to create unique webpages for each recipe/plan.
One of the more difficult parts to implement was the list of ingredients on "Create Recipe" page. The list is implemented adaptably through JS and allows adding and removing of rows. When the recipe is created all ingredients are fetched together and as every row has the same id it requires special implementation. Additional difficulties are posed on the "Edit recipe" page where the same ingredients should be displayed and edited. Once the recipe is edited all the ingredients in the database are replaced with possible new values.
The images for recipes are currently only stored as links so as to not store them on the server, but that would be a good further development for this project.
I also would like to add an option of importing recipes from the web, but that feature proved to be much more difficult to implement, then desired as there is no easy API to bring them in. I think it would be possible through the integration with OpenAI, but this task is beyond the scope of this course.

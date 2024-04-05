
Project Design Document

This project is a flask web application using Python, HTML, SQLite, CSS, and Javascript.
Each section will discuss the primary features and design choice implemented in each language.


Python:
The main functionality of the web application is implemented in the app.py python file. In it, all the routes which can be accessed by a user are defined and associated with functions that return a rendered template with varied additional parameters. User input from the POST method is primarily gotten using the request.form.get("") function, however, due to the nature of the webapp requiring users to upload images, whether through posts or profile photos, request.files[""] was additionally utilized along with the <input type="file"> tag in HTML. Cs50's SQL import was also used to allow the webapp to communicate with an SQLite database and have more permanent storage.


HTML:
Every HTML file in the project stems from the same layout.html. layout.html defines the two main sections
of the website: The vertical navbar and the main content. The vertical navbar uses the <nav> tag and the
bootstrap navbar and navbar-light css styling classes. Each choice on the navbar is an <a> tag to another page on this webapp. The other section is the main content section which is filled in by the jinja block template allowing other HTML files to extend it. This design allows the vertical navbar to stay static and the main content to exists next to the vertical navbar for every extending HTML file.

Every other HTML file is an existing page of the website. Login and Register are ported over from the Finance project, however all others are most unique. All user input utilizes the <form> tag with some additions. In addfriends.html, form groups are generated using a jinja for loop with a button as well as a <form type="hidden"> with an value of the userid of a possible friend the current user could add. This allows hidden data to sent using POST and allowing app.py to determine the userID of the friend should the user click the "Add friend" button.

Another topic of note is the user of dynamic <img src> in index.html and profile.html. The src attributes are determined by either a user.id or a post.id depending on the context and are set to /userpfp/{{user.id}} or
/images/{{ post.id }} respectively. These do not correlate to webpages, but instead are handeled by the app.py and return the proper image file for the front end.

Jinja was used extensively to allow the webpages to be dynamic and user dependent.

SQLite:
There are 3 tables in the keystroke.db database: users, posts, and friends. The users table contains the columns: id, username, hash, and profilephoto, with datatypes: INTEGER, TEXT, TEXT, and BLOB, respectively. BLOB (Binary Large Object) was used to store photos as binary objects as sqlite does not have a IMAGE datatype. User ids were added to allow for multiple users to have the same username without causing errors. Hash stores the password hash instead of the direct password for security.

A table named posts stores all of the posts on the website. It contains the columns id, title, bodytext, imageBinary, date_created, username, language, userid, and comments with datatypes: INTEGER, TEXT, TEXT, BLOB, TEXT, TEXT, TEXT, INTEGER, and TEXT. Again the image binary is stored as a BLOB.

Lastly the friends table has just two columns userID and friendID. This is just a simple relation between one user id and another. This system allows one user to be friends with another user, but not the other way around analogous to following on instagram or another social media platform.

CSS:
The only css file present in the project is the styles.css file. In it defines styles for all the HTML elements in the html. The var() function along with an argument of a variable name was used to simplify arbitrary color choices into simple variable names like background-color. This css was not incredibly complicated and it mainly serves as simple styling for the webapp.

Javascript:
Javascript was used once in the layout.html file to include a button that scrolled to the top of the page when the user was at the bottom. If I had more time, I would try to add more functionality with asyncronous functions that add more posts as the user scrolls down.



# Fair Price Jobs
#### Video Demo:  https://www.youtube.com/watch?v=vg5jIKvffYA
#### Description:

This project was developed to address a real life headache faced by anyone who wants to renovate a property in the South of France (where I live).
Finding a reasonably priced tradesman to lay tiles, do the electrics, check the roof etc. is very difficult.

The idea is to build a platform where friends can share information on jobs that they have had done:
- contact details of the tradesman, pricing, rating, job description etc.

Anyone can register and create a group or search for an existing group. Groups are associated with postcodes.
To join an existing group will require approval from that groups owner.

Once joined the user can see the different members and the tradesmen who have been entered along with the jobs they have done.


### Design choices

I worked outside the cs50.dev environment for this project
I used flask, html with bootstrap and sqlite3
In addition to files below I wrote some sql scripts to reset the database and enter dummy data
The social group aspect was more complex than I originally anticipated


#### File Descriptions:

- `app.py`: Main application file that runs the server and handles requests.
- `helpers.py`: helper functions, alerts, login required etc.
- `static/`: Directory for static files like CSS and JavaScript. Not much used so far
- `templates/`: Directory for HTML templates used for rendering the web pages.
  - `index.html`: Homepage of the application.
  - `layout.html`: Base layout template for the application.
  - `register.html`: User registration page.
  - `login.html`: User login page.  
  - `welcome.html`: Welcome page displayed after user login.
  - `create_group.html`: Interface for creating a new user group.
  - `group_members.html`: Displays the members of a specific group.
  - `add_tradesman.html`: Form for adding a new tradesman.
  - `add_job.html`: Form for adding a new job entry.
  - `view_job.html`: Detailed view of a specific job entry.
  - `application.db`: sqlite database tables below
        users:         Stores user information including credentials and personal details.
        groups:        Contains group information with names and postcodes.
        user_groups:   Junction table linking users to groups with their respective statuses.
        tradesmen:     Holds details about tradesmen including their contact information and trade type.
        group_tradesmen: Junction table linking groups to tradesmen.
        jobs:          Records job details including user, tradesman, and financial information.

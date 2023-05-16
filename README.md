# My Habit Tracker Server
I'm building a web application to help me keep track of my workouts. It could be helpful for you as well. 
### Server Installation
- Fork or clone this repo
- You need to create [supabase](https://app.supabase.com) project where you will get the URL and KEY
- Run the following commands in the `/client` folder
    ```
        py -3 -m venv .venv
        .venv\scripts\activate
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install python-dotenv
    ```
- Update the `.flaskenv.example` file to read `.env.local` and add the correct URL for `SUPABASE_URL` and `SUPABASE_KEY`
- To deploy I used [heroku](https://dashboard.heroku.com/), I'm workin on correct pipelines to auto deploy, for now I use the following commands
    ```
    heroku git:remote -a <project-name>
    git push heroku <branch-name>
    ```
# DBT Streamlit Monitoring

This app is for DBT **Cloud users** who want to be able to share information on how
their jobs are performing, but without granting admin access to DBT Cloud directly.

Kudos to the wizards at [Cazoo](https://www.cazoo.co.uk/) for creating it! You can read their blog post [here](https://blog.streamlit.io/dbt-cloud-jobs-with-streamlit/).

The app allows people to see which jobs:
 - have been completed successfully
 - have failed
 - lets you see the specific steps where a job is falling over

![image](https://user-images.githubusercontent.com/27242399/140054479-fa548407-336c-4019-89fd-efb277712c5c.png)

You'll need to add some secrets specific to your environment, but other than that you
should be up and running right out of the box.

## Features

- Supports multiple projects on the same DBT Account
- RAG Status of jobs
- Show failed steps, with links to the specific file in your repo
- Get a view of recent job runs to see if there's an ongoing issue with your job


## Installation

Install and run locally with pipenv (you will need to configure your [secrets.toml file](#secrets.toml) to actually be able to use the app)

```bash
>> pipenv install
>> pipenv run app
```

For Mac users, watchdog is included as a dev dependency, so you can include watchdog with

```bash
>> pipenv install -d
```

## Configuration

### secrets.toml

The app in its current form assumes the presence of a few things which will be custom to
each DBT account, and so we put these in secrets.toml inside of .streamlit.

Running streamlit locally will use these secrets (accessible both as environment variables
and from streamlit.secrets) and if you decide to deploy onto Streamlit for Teams then you
can use the same format to add your secrets directly into the web interface.

You can see an example file in `.streamlit/example_secrets.toml`. You will need to copy this file/rename it to `.streamlit/secrets.toml` if you want to use it

 - `ACCOUNT_ID` - your DBT account id

 - `API_TOKEN` - your DBT API key (for very obvious reasons we don't commit this to version control).

 - `DASHBOARD_USER` / `DASHBOARD_PASS` - username/password for the authorisation. If you are always using the app locally, you likely will not require this, but can be useful if you want to host the app on an internal/external web page.  (NOTE: We **do not** recommend using this for securing an app long term, and you should use a proper SSO backed auth like okta, google, jumpcloud etc which would be much more robust)

 - `PROJECT_MAPPING` - This is mapping that links specific DBT project ids to a plain English name for displaying in the app. The project mapping is used to drive the select boxes that allow you pick specific projects to drill down to (if you have multiple projects of course).

 - `PROJECT_REPO_URL_MAPPING` - This is a mapping that maps the dbt adapter you are using (ie, `redshift`) to the git repository where the code is stored, so you can view the queries of tables/tests that have failed in the browser

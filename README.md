
# DBT Streamlit Monitoring

This project is for DBT Cloud users who want to be able to share information on how
their jobs are performing, but without granting Admin access to DBT Cloud directly.

The app builds a nice interactive dashboard using Streamlit, which allows people to see
which jobs are completing successfully (or failing) and lets you see the specific steps
where a job is falling over.

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

Unless you're a massive fan of Cazoo (I mean, who isn't!) you might want to swap out the
logo for your own.

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


It's possible that this might be a bit Cazoo specific, but I hope it finds some use elsewhere. This comes from two main pieces;
* When we have job failures, our analysts asked for a link directly to the repo for that file.
* We currently have two main repos for DBT, one for all Big Query jobs and one for Redshift, so having the ability to add multiple adapters is very useful for us

These URLs are the 'base' url for our repos that link to the repo, branch, and the folder within.

So as an example;

https://github.com/MyCompany/MyRepo/tree/main/my_folder/

This is a repo hosted on git, the repo is called MyRepo, has `main` as the primary repo branch and within the repo all the dbt work is in a folder called `my_folder`. This logic should work with other major git providers (gitlab, bitbucket etc), but please let us know if you have difficulties!

### Contributing

Contributions of new features or bugfixes are (very) welcome. Please, if you would like to contribute, install our pre-commit hooks to ensure the code matches our formatting standards.

```bash
>> pre-commit install --hook-type pre-commit
>> pre-commit install --hook-type pre-push
# if you want to run the commit hooks after install you can run the below (note that you do not need to do this before evey commit, it will happen automatically)
>> pre-commit run --all-files
```

If you have any queries, questions or want to talk through a possible new feature, please raise a [issue](https://github.com/Cazoo-uk/dbt-streamlit/issues) and we will get back to you as soon as possible

import streamlit as st
from src.pages.dbt_dashboard import render_page as render_page_dbt_dashboard
from src.shared.environment import Auth
from PIL import Image

st.set_page_config(page_icon="⚙️", page_title="DBT Dashboard")

image = Image.open("./images/logo.png")
st.image(image, width=75)


def main():
    set_up_app()
    set_up_auth()
    render_page_dbt_dashboard()


def set_up_app():
    st.title("DBT Dashboard")
    with st.expander("How to use this app"):
        st.text("")
        st.markdown(
            """

            This app is for DBT **Cloud users** who want to be able to share information on how
            their jobs are performing, but without granting admin access to DBT Cloud directly.

            Kudos to the wizards at [Cazoo](https://www.cazoo.co.uk/) for creating it! You can read their blog post [here](https://blog.streamlit.io/dbt-cloud-jobs-with-streamlit/).

            The app allows people to see which jobs:
            - have been completed successfully
            - have failed
            - lets you see the specific steps where a job is falling over

            """
        )

        st.text("")
        image = Image.open("./images/dbt_screenshot.png")
        st.image(image, width=600)
        st.text("")
        st.markdown(
            """
            
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
            and from streamlit.secrets) and if you decide to deploy onto Streamlit Cloud then you
            can use the same format to add your secrets directly into the web interface.

            You can see an example file in `.streamlit/example_secrets.toml`. You will need to copy this file/rename it to `.streamlit/secrets.toml` if you want to use it

            - `DASHBOARD_USER` / `DASHBOARD_PASS` - username/password for the authorisation. If you are always using the app locally, you likely will not require this, but can be useful if you want to host the app on an internal/external web page.  (NOTE: We **do not** recommend using this for securing an app long term, and you should use a proper SSO backed auth like okta, google, jumpcloud etc which would be much more robust)

            - `ACCOUNT_ID` - your DBT account id

            - `API_TOKEN` - your DBT API key (for very obvious reasons we don't commit this to version control).

            - `PROJECT_MAPPING` - This is mapping that links specific DBT project ids to a plain English name for displaying in the app. The project mapping is used to drive the select boxes that allow you pick specific projects to drill down to (if you have multiple projects of course).

            - `PROJECT_REPO_URL_MAPPING` - This is a mapping that maps the dbt adapter you are using (ie, `redshift`) to the git repository where the code is stored, so you can view the queries of tables/tests that have failed in the browser


            """
        )

def set_up_auth():

    auth = Auth(
        user=st.secrets["DASHBOARD_USER"], password=st.secrets["DASHBOARD_PASS"]
    )

    if not auth.is_auth():
        st.warning("Please, introduce the correct username and password in your secrets.")
        st.stop()

    return auth


if __name__ == "__main__":
    main()

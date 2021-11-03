import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd


from src.pages.dbt_dashboard import render_page as render_page_dbt_dashboard
from src.shared.environment import Auth


def main():
    # st.set_page_config(layout="wide")
    set_up_app()
    set_up_auth()
    render_page_dbt_dashboard()


# np.random.seed(24)
# df = pd.DataFrame({"A": np.linspace(1, 5, 5)})
# df = pd.concat([df, pd.DataFrame(np.random.randn(5, 4), columns=list("BCDE"))], axis=1)
# df.iloc[0, 2] = np.nan
# 
# # Unstyled
# st.table(df)
# 
# # Custom formatting
# st.table(df.style.format({"E": "{:.2f}"}))


###############


def set_up_app():
    # Set a title and add a sidebar title
    st.title("DBT Dashboard")

    # add an image to the sidebar
    image = Image.open("./images/logo.png")
    st.sidebar.image(image, use_column_width=True)

    st.sidebar.title("Login")


def set_up_auth():

    input_user = st.sidebar.text_input("Username")
    input_pass = st.sidebar.text_input("Password", type="password")

    if not input_user or not input_pass:
        st.warning("Please input your user / pass.")
        st.stop()
    auth = Auth(user=input_user, password=input_pass)

    if not auth.is_auth():
        st.warning("Please, introduce the correct user/pass.")
        st.stop()

    return auth


if __name__ == "__main__":
    main()

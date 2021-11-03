from typing import Tuple
import os
import requests
import streamlit as st

from src.dbt_dashboard import (
    find_failed_results,
    get_all_jobs,
    get_all_runs,
    historical_runs,
    only_latest_runs,
    unique_jobs,
    fetch_run_artifacts,
    highlight,
)
from src.classes import DbtCloud

PROJECT_MAPPING = st.secrets["PROJECT_MAPPING"]
ACCOUNT_ID = int(os.environ["ACCOUNT_ID"])
PROJECT_REPO_URL_MAPPING = st.secrets["PROJECT_REPO_URL_MAPPING"]


CHOSEN_DF_MAPPING = {"all": get_all_runs}
REQUIRED_COLUMNS_RUNS = [
    "id",
    "project_name",
    "project_id",
    "status_humanized",
    "finished_at",
    "run_duration",
    "is_success",
    "is_complete",
    "job_id",
]
REQUIRED_COLUMNS_JOBS = ["name", "next_run"]


class UnknownAdapterException(Exception):
    pass


def render_page():  # NOQA: CFQ001
    """This renders the dbt dashboard, it fetches the latest runs and the
    corresponding details for the given job in the run
    """
    st.sidebar.title("Configuration")

    chosen = st.sidebar.selectbox(
        "Failed or Successful runs", ["all", "failed", "successful"]
    )

    st.sidebar.subheader("Filter by project")
    project_dict = {
        project_id: st.sidebar.checkbox(project, value=True)
        for project_id, project in PROJECT_MAPPING.items()
    }

    filter_list = [int(key) for key, value in project_dict.items() if value]

    dbt = DbtCloud(account_id=ACCOUNT_ID)
    all_runs, all_jobs = fetch_dbt_data(dbt)
    failed_runs_df, successful_runs_df, all_runs_df = merge_runs_jobs_to_df(
        all_runs, all_jobs, filter_list
    )

    st.text(
        f"""
        The below data frame contains info on {chosen} runs
        This is merged with data on the relevant jobs based on job id
        """
    )
    select_text = "Select a run to view last run artifacts: "
    chosen_mapping = {
        "all": all_runs_df,
        "successful": successful_runs_df,
        "failed": failed_runs_df,
    }

    chosen_df = chosen_mapping[chosen]
    # styling has to be applied only to the shown df instance and not the one used for later iteration
    st.dataframe(
        chosen_df.sort_values("finished_at", ascending=False, axis=0)
        .style.apply(highlight, axis=1)
        .set_properties(**{"color": "#FFF"})
    )
    run_name = st.selectbox(
        select_text,
        list(
            zip(
                chosen_df.sort_values("finished_at", ascending=False, axis=0)["name"],
                chosen_df.sort_values("finished_at", ascending=False, axis=0)[
                    "project_name"
                ],
            )
        ),
    )

    job_id = chosen_df.loc[
        (chosen_df["name"] == run_name[0]) & (chosen_df["project_name"] == run_name[1])
    ]["job_id"].item()
    if (
        chosen_df.loc[
            (chosen_df["name"] == run_name[0])
            & (chosen_df["project_name"] == run_name[1])
        ].status_humanized.item()
        != "Cancelled"
    ):
        run_results = fetch_run_artifacts(dbt, chosen_df, run_name)
        manifest = dbt.get_run_manifest(
            run_results["metadata"]["env"]["DBT_CLOUD_RUN_ID"]
        )
        adapter = manifest["metadata"]["adapter_type"]
        base_url = PROJECT_REPO_URL_MAPPING.get(adapter)
        if base_url is None:
            raise UnknownAdapterException(
                f"The adapter type {adapter} was not found in the PROJECT_REPO_URL_MAPPING"
            )

        failed_steps = find_failed_results(run_results)

        st.text(
            """
            Press the button below to view json results from the latest run of the selected job
            """
        )
        if st.button("Show latest run results"):
            list_failed(failed_steps, run_results, manifest, base_url)

    else:
        st.text("Run was cancelled, no run artifacts available")

    if job_id:
        st.title("Historical runs")
        st.text(
            f"""
        Previous runs for job: {run_name}
        """
        )
        historical_df = historical_runs(all_runs, job_id).head(10)
        st.table(historical_df[["finished_at", "is_success", "is_error"]])
        select_run = st.selectbox(
            "Select historical run to inspect", list(historical_df.index)
        )
        try:
            run_result = dbt.get_run_artifacts(select_run)
        except requests.HTTPError:
            st.text("No run artifacts available")
            run_result = None
        if run_result and st.button("Show historic run results"):
            failed_steps = find_failed_results(run_result)
            list_failed(failed_steps, run_result, manifest, base_url)


@st.cache(ttl=10 * 60)
def fetch_dbt_data(dbt: DbtCloud) -> Tuple[dict, dict]:
    """call dbt api for all latest runs and jobs

    Args:
        dbt (DbtCloud): dbt cloud api instance

    Returns:
        Tuple[dict, dict]: dict of both runs and jobs
    """
    all_runs = get_all_runs(dbt)
    all_jobs = get_all_jobs(dbt)

    return all_runs, all_jobs


def merge_runs_jobs_to_df(all_runs, all_jobs, filter_list):

    df_latest_runs = only_latest_runs(all_runs)
    df_unique_jobs = unique_jobs(all_jobs)

    df_latest_runs["project_name"] = (
        df_latest_runs["project_id"].astype(str).map(PROJECT_MAPPING)
    )

    df_latest_runs = df_latest_runs[REQUIRED_COLUMNS_RUNS]
    df_unique_jobs = df_unique_jobs[REQUIRED_COLUMNS_JOBS]

    merged_df = df_unique_jobs.merge(df_latest_runs, left_index=True, right_index=True)
    merged_df = merged_df.loc[
        (merged_df.is_complete == True)  # NOQA: E712
        & (merged_df["project_id"].isin(filter_list))
    ]
    failed_runs_df = merged_df.loc[merged_df.is_success == False]  # NOQA: E712
    successful_runs_df = merged_df.loc[merged_df.is_success == True]  # NOQA: E712

    return failed_runs_df, successful_runs_df, merged_df


def list_failed(failed_steps, run_results, manifest, base_url):
    """output failed results with details from run results and manifest as expandable

    Args:
        failed_steps ([type]): [description]
        run_results ([type]): [description]
        manifest ([type]): [description]
        base_url ([type]): [description]
    """
    if len(failed_steps):
        st.text("Failed steps")
        for failed in failed_steps:
            unique_id = failed[0]
            path = manifest["nodes"][unique_id]["original_file_path"]

            with st.beta_expander(f"{failed[1]}   : {failed[0]}"):
                link = f"[{path}]({base_url}{path})"
                st.markdown(link, unsafe_allow_html=True)
                info_json = create_info_json(manifest, failed, run_results)
                st.json(info_json)
    else:
        st.text("No failed steps found")


def create_info_json(manifest: dict, failed: tuple, run_results: dict) -> dict:

    """Create json blob containing useful info pulled from manifest and run results
    Order here is for sake of presentation within streamlit app

    Returns:
        dict: contains relevant details for run from manifest and run results based on run ids from failed
    """

    info_blob = {}
    info_blob["Type"] = manifest["nodes"][failed[0]]["resource_type"]
    info_blob["Status"] = run_results["results"][failed[1]]["status"]
    info_blob["Message"] = run_results["results"][failed[1]]["message"]
    info_blob["Raw SQL"] = manifest["nodes"][failed[0]]["raw_sql"]
    info_blob["Timing"] = run_results["results"][failed[1]]["timing"]
    info_blob["Depends On"] = manifest["nodes"][failed[0]]["depends_on"]

    return info_blob

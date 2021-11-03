import pandas as pd
from src.classes import DbtCloud


def only_latest_runs(all_runs: dict) -> pd.DataFrame:
    """from all runs return only latest finished per job

    Args:
        all_runs (dict): all runs as response from DBT api class

    Returns:
        pd.DataFrame: dataframe of latest runs for each job
    """
    runs = {}
    for run in all_runs["data"]:
        new_time = run["started_at"]
        existing_time = runs.get(run["job_id"], {}).get("started_at")
        if existing_time:
            if new_time and new_time > existing_time:
                runs[run["job_id"]] = run
            else:
                continue
        else:
            runs[run["job_id"]] = run

    return pd.DataFrame.from_dict(runs, orient="index")


def unique_jobs(all_jobs: dict) -> pd.DataFrame:
    """from all jobs create dataframe with only distinct jobs

    Args:
        all_jobs (dict): api response for jobs call

    Returns:
        pd.DataFrame: dataframe of unique jobs
    """
    jobs = {}
    for job in all_jobs["data"]:
        if not jobs.get(job["id"]):
            jobs[job["id"]] = job
    return pd.DataFrame.from_dict(jobs, orient="index")


def get_all_runs(dbt: DbtCloud) -> dict:
    """get last 500 dbt runs

    Args:
        dbt (DbtCloud): dbt class instance for calling api

    Returns:
        dict: 500 latest runs
    """
    all_runs = dbt.list_runs(params={"order_by": "-finished_at", "limit": 500}).response
    return all_runs


def get_all_jobs(dbt: DbtCloud) -> dict:
    """returns 200 jobs

    Args:
        dbt (DbtCloud): dbt class instance for calling api

    Returns:
        dict: list of all created jobs
    """
    all_jobs = dbt.list_jobs(params={"order_by": "-created_at", "limit": 200}).response
    return all_jobs


def historical_runs(all_runs: dict, job_id: int) -> pd.DataFrame:
    """for job type find all historical runs in get_all_runs response

    Args:
        all_runs (dict): from the list of all runs find any that matche the same job id
        job_id (int): chosen job id

    Returns:
        pd.DataFrame: dataframe of historical runs fo given job id
    """
    historical_runs = {}
    for run in all_runs["data"]:
        if run["job_id"] == job_id:
            historical_runs[run["id"]] = run
    return pd.DataFrame.from_dict(historical_runs, orient="index")


def fetch_run_artifacts(
    dbt: DbtCloud, chosen_df: pd.DataFrame, run_name: tuple
) -> dict:
    """find run id in response dataframe and fetch run artifacts
    with the given run id

    Args:
        dbt (DbtCloud): dbt class for calling api
        chosen_df (pd.DataFrame): dataframe of combined run and job data
        run_name (tuple): job name and related project name

    Returns:
        dict: dbt api run artifact json response
    """
    run_row = chosen_df.loc[
        (chosen_df["name"] == run_name[0]) & (chosen_df["project_name"] == run_name[1])
    ]
    return dbt.get_run_artifacts(run_row["id"].item())


def find_failed_results(run_artifacts: dict) -> list:
    """find the index and ID for which elements failed in run

    Args:
        run_artifacts (dict): dbt api run artifact json response

    Returns:
        list: list of tuples with unique id, index
    """
    failed_steps = []

    for index, result in enumerate(run_artifacts["results"]):
        if result["status"] not in ["success", "pass"]:
            failed_steps.append((result["unique_id"], index))
    return failed_steps


def highlight(series: pd.Series) -> list:
    """return list same width as row to apply styling

    Args:
        series (pd.Series): one row of data from chosen datafram

    Returns:
        list: list same size as series with styling to apply
    """
    if series.is_success >= 1:
        return ["background-color: #3e9456"] * (len(series))
    else:
        return ["background-color: #a62100"] * (len(series))

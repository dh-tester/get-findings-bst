#!/usr/bin/env python

"""
This script requests all finding data for a specific company and writes it to a csv file.

This is primarily useful when there are over 9,000 findings and the export option on the web page is disabled.

The documentation for the api endpoint being used can be found at this link:
https://help.bitsighttech.com/hc/en-us/articles/360022913734-GET-Finding-Details
"""

import os.path
import requests
import pandas as pd

findings_list = []


def request_user_input():
    company_guid = input("Please enter company guid: ")
    bst_admin_token = input("Please enter api token: ")
    limit = input("Please enter a limit (5000 recommended): ")
    unsampled = input("Unsampled (true/false): ")
    retrieve_findings_data(company_guid, bst_admin_token, limit, unsampled)


def retrieve_findings_data(company_guid, bst_admin_token, limit, unsampled):
    api_url = "https://api.bitsighttech.com/ratings/v1/companies/" + company_guid + "/findings?limit=" + limit + "&unsampled=" + unsampled
    auth_values = (bst_admin_token, 'blank_password')

    while api_url:
        print("Requesting: ", api_url)
        response_data = requests.get(url=api_url, auth=auth_values)
        response_data.raise_for_status()

        json_data = response_data.json()

        findings_list.extend(json_data['results'])

        api_url = json_data['links']['next']

        print("http status: ", response_data)


def reshape_finding_data():
    findings_dataframe = pd.DataFrame(findings_list)

    exploded_details_column = findings_dataframe.details.apply(pd.Series)

    final_findings_dataframe = pd.concat([findings_dataframe, exploded_details_column['grade']], axis=1)

    final_findings_dataframe = final_findings_dataframe.drop(
        columns=['temporary_id', 'assets', 'details', 'related_findings', 'rolledup_observation_id', 'tags',
                 'remediation_history', 'duration', 'comments'])

    final_findings_dataframe.to_csv("export_file.csv", index=False)

    print("Process complete. ", "File location: ", os.getcwd() + "/export_file.csv")


if __name__ == '__main__':
    request_user_input()
    reshape_finding_data()

__author__ = "dh_tester"
__status__ = "production"
__version__ = "2.0"

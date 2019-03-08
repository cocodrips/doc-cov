import argparse
import http.client
import json
import logging
import os

logger = logging.getLogger(__name__)
markdown_header = "## document coverage"


def csv_to_table(filepath):
    """
    Convert report to markdown table.
    Args:
        filepath: report file.

    Returns:
        str
    """
    with open(filepath, 'r') as f:
        output = f"""{markdown_header}
|  | Coverage|
|----|----:|
"""
        for line in f:
            name, type_, true, all_, coverage = line.strip().split(',')
            if name != 'coverage':
                continue
            output += f"|{type_}|{coverage:>8} ({true:^3} / {all_:^3})|\n"
        return output


def comment_pr(args):
    conn = http.client.HTTPSConnection("api.github.com")
    payload = ""

    token = args.token
    if not token:
        token = os.environ.get('GITHUB_TOKEN')

    if not token:
        raise ("No github token.")

    headers = {
        'Authorization': f"token {token}",
        'User-Agent': "doccov-app",
    }

    user = os.environ.get('PROJECT_USERNAME')
    repo = os.environ.get('PROJECT_REPONAME')
    issue_num = os.environ.get('PR_NUMBER')

    if os.environ.get('CIRCLECI') == 'true':
        user = os.environ.get('CIRCLE_PROJECT_USERNAME')
        repo = os.environ.get('CIRCLE_PROJECT_REPONAME')
        issue_num = os.environ.get('CIRCLE_PR_NUMBER')

    if not any([user, repo, issue_num]):
        logger.error("Failed to get repository info.")

    # -----------------------------------
    # Delete old doc-coverage comment
    # -----------------------------------

    conn.request("GET", f"/repos/{user}/{repo}/issues/{issue_num}/comments", payload, headers)

    data = conn.getresponse().read()
    comments = json.loads(data.decode("utf-8"))
    for comment in comments:
        if comment['body'].startswith(markdown_header):
            comment_id = comment['id']
            logger.info(f'delete {comment_id}')
            conn.request("DELETE", f"/repos/{user}/{repo}/issues/comments/{comment_id}",
                         payload, headers)
            conn.getresponse()

    # -----------------------------------
    # Add doc-coverage comment
    # -----------------------------------
    payload = {
        "body": csv_to_table(args.report)
    }
    conn.request("POST", f"/repos/{user}/{repo}/issues/{issue_num}/comments",
                 json.dumps(payload), headers)
    res = conn.getresponse()


def entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=str, help="doccov output file(csv)")
    parser.add_argument("--token", dest='token', default='', type=str,
                        help="Github token. Or set environment `GITHUB_TOKEN`")
    args = parser.parse_args()
    comment_pr(args)


if __name__ == '__main__':
    entry_point()

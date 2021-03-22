import click
import datetime
import os
from github import Github

boilerplate_issue_body=("Use the issue description to describe the goals of the epic and "
        "what it's about. Use the comments to update the current status."
        "\n\n"
        "# Description/Goals\n\n"
        "TODO")

def do_create(r, title, epic_tracking_label):
    if epic_tracking_label not in [label.name for label in r.get_labels()]:
        r.create_label(epic_tracking_label, "fff")
    r.create_issue(title=title, body=boilerplate_issue_body, labels=[r.get_label(epic_tracking_label)])

def remove_status_header(status):
    new_status = ""
    for line in status.split("\n"):
        if "# Current Status" in line:
            continue
        new_status += line + "\n"
    return new_status.strip()

def do_status(r, epic_tracking_label):
    if epic_tracking_label not in [label.name for label in r.get_labels()]:
        return []
    issues = r.get_issues(labels=[r.get_label(epic_tracking_label)])
    statuses = []
    for issue in issues:
        comments = [comment.body for comment in issue.get_comments()]
        latest_comment = comments[-1] if len(comments) else "No Status"
        statuses.append({"title": issue.title, "status": latest_comment, "url": issue.url})
    for status in statuses:
        status["status"] = remove_status_header(status["status"])
    return statuses

@click.command()
@click.option('--repo', type=str, help='Repo to use (username/repo).', required=True)
@click.option('--create', type=str, help='Create a new epic with the given title.')
@click.option('--status', is_flag=True, help='Dump epic statuses.')
@click.option('--project-name', type=str, default="Current", help='Dump epic statuses.')
@click.option('--epic-tracking-label', type=str, default="epic-tracking", help='Dump epic statuses.')
def epic(repo, create, status, project_name, epic_tracking_label):
    github_access_token = os.environ.get('GITHUB_ACCESS_TOKEN')
    g = Github(github_access_token)
    r = g.get_repo(repo)

    if create:
        do_create(r, create, epic_tracking_label)
    elif status:
        print("# %s %s Status\n" % (
            datetime.date.strftime(datetime.date.today(), "%m/%d/%Y"),
            project_name))
        print("https://github.com/%s/labels/%s\n" % (project_name, epic_tracking_label))
        for status in do_status(r, epic_tracking_label):
            print("## %s\n" % status["title"])
            print("%s\n" % status["status"])
    else:
        click.echo("One of --status or --create is required")

if __name__ == '__main__':
    epic()

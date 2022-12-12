import threading
import time

import requests

from util import configUtils
from util.MyThread import MyThread
from util.dateUtils import get_diff_day


def get_worklogs(issues, type, diff, fromDate, toDate):
    worklogs = []
    thread_list = []
    for issue in issues:
        t = MyThread(get_worklog, (issue, type, diff, fromDate, toDate))
        while threading.active_count() > 20:
            time.sleep(0.4)
        t.start()
        thread_list.append(t)
    for i in thread_list:
        worklogs.extend(i.get_result())
    return worklogs


def get_worklog(issue, type, diff, fromDate, toDate):
    wl = []
    if type == '个人':
        try:
            project = issue.fields.customfield_11907.value
        except:
            project = ''
        wl.append({"key": issue.key, '创建时间': issue.fields.created[0:10], "工作事项": issue.fields.summary, "项目支持": project})
        return wl
    logs = configUtils.jira_client().worklogs(issue)
    for w in logs:
        d = get_diff_day(w.started[0:10])
        if type == '项目' or type == '产品':
            f = get_diff_day(str(fromDate.date().getDate())[1:-1].replace(' ', '').replace(',', '-'))
            t = get_diff_day(str(toDate.date().getDate())[1:-1].replace(' ', '').replace(',', '-'))
            if f <= d <= t:
                if type == '项目':
                    try:
                        prod = issue.fields.customfield_12000.value
                    except:
                        prod = ''
                    wl.append({"姓名": w.author.displayName, "部门": issue.fields.project.name,
                               "项目": issue.fields.customfield_11907.value, "工作事项": issue.fields.summary,
                               "产品": prod,
                               "start": w.started[0:10], "用时": w.timeSpentSeconds / 3600})
                elif type == '产品':
                    try:
                        prod = issue.fields.customfield_12000.value
                    except:
                        prod = ''
                    wl.append({"姓名": w.author.displayName, "部门": issue.fields.project.name,
                               "工作事项": issue.fields.summary,
                               "产品": prod,
                               "start": w.started[0:10], "用时": w.timeSpentSeconds / 3600})
        else:
            if d >= diff:
                wl.append({"姓名": w.author.displayName, "工作事项": issue.fields.summary,
                           "start": w.started[0:10], "用时": w.timeSpentSeconds / 3600})
    return wl


def get_sprints(project):
    url = configUtils.host
    cookies = configUtils.jira_cookie()
    board_url = url + "/rest/agile/1.0/board?projectKeyOrId=" + project
    response = requests.get(board_url, cookies=cookies, headers={"Accept": "application/json"})
    sprints = []
    for item in response.json()['values']:
        sprint_url = url + "/rest/agile/1.0/board/" + str(item['id']) + "/sprint?state=future,active"
        response = requests.get(sprint_url, cookies=cookies, headers={"Accept": "application/json"})
        sprint_json = response.json()
        if 'values' in sprint_json:
            sprint_list = sprint_json['values']
            for sprint in sprint_list:
                element = {'id': sprint['id'], 'name': sprint['name']}
                if element not in sprints:
                    sprints.append(element)
    return sorted(sprints, key=lambda x: x['id'], reverse=True)


if __name__ == '__main__':
    from datetime import datetime, date
    d = datetime.strptime('2020-01-01', '%Y-%m-%d')
    d2 = datetime.now()
    diff = (d - d2).days
    print(diff)
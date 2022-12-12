import math
import re
import threading
import time
from datetime import datetime

import bs4
import markdown
from jira.exceptions import JIRAError

from reportError import ReportError
from util import configUtils
from util.MyThread import MyThread

temp = []


def create_work(sprint, summary, day, username, project, issuetype='任务', timeSpend='0h'):
    jira = configUtils.jira_client()
    log = 'summer:{0} | day:{1} | spend:{2}'.format(summary, day, timeSpend)
    if temp.count(log) > 0:
        return summary + ' : 已提交过，点击清理提交缓存即可重新提交'

    # 检查产品
    reg_prod = re.findall(re.compile(r'[【](.*?)[】]', re.S), summary)[0]
    hasProd = [i['value'] for i in configUtils.get_prods()].__contains__(reg_prod)

    prod_name = '无' if not hasProd else reg_prod

    # 检查项目支持
    reg_names = re.findall(re.compile(r'[[](.*?)[]]', re.S), summary)
    pname = ''
    if len(reg_names) > 0:
        pname = reg_names[0]
    try:
        # , 'timeestimate': '0h', 'timeoriginalestimate': '0h'
        field_dict = {'project': project, 'summary': summary, 'description': '无', 'issuetype': issuetype, 'assignee': {'name': username}}
        # 普通卡片
        if pname.__contains__("-"):
            wi = jira.issue(pname)
            if not summary.endswith("]"):
                pi = wi
                field_dict['timetracking'] = {"remainingEstimate": "0", "originalEstimate": 0}
                field_dict['parent'] = {'key': pi.key}
                field_dict['project'] = pi.fields.project.id
                field_dict['summary'] = summary.split(pname)[1].replace(']', '')
                field_dict['issuetype'] = '子任务'
                if pname.startswith('APITEAM'):
                    field_dict['components'] = [{"name": "其它"}]
                else:
                    field_dict['components'] = [{"name": "无"}]
                wi = jira.create_issue(fields=field_dict)
        else:
            if sprint:
                field_dict['customfield_10100'] = sprint
            if prod_name:
                if prod_name != '无':
                    field_dict['customfield_12000'] = {"value": prod_name}
            if pname:
                field_dict['customfield_11907'] = {"value": pname}
            wi = jira.create_issue(fields=field_dict)

    except JIRAError as e:
        if "customfield_11907" in e.response.text:
            return '项目名称不存在:{0} \n'.format(pname)
        if "问题不存在" in e.response.text:
            return '卡片不存在:{0}'.format(pname)
        else:
            return e.response.text
    if wi is not None:
        create_tempo(wi, timeSpend, day)
    temp.append(log)


def create_tempo(issue, timeSpend, day):
    jira = configUtils.jira_client()
    try:
        jira.transition_issue(issue, '11')
        jira.transition_issue(issue, '21')
    except:
        pass
    # 创建worklog
    try:
        jira.add_worklog(issue=issue.key, timeSpent=timeSpend, started=day)
    except JIRAError as e:
        return e.response.text


def read_data(soup):
    """ 解析周报内容
    :param soup:
    :param preview:
    :return:
    """
    works = []
    l = 0
    if soup.ol is None:
        raise ReportError("第1行错误: eg: 1. 图平台")
    for i in soup.ol.contents:
        l += 1
        title = '【' + i.next + '】 '
        if type(i) != bs4.element.Tag or i.ul is None: continue
        for a in i.ul.contents:
            l += 1
            second = a.next.replace('<p>', '').replace('</p>', '')
            if type(a) != bs4.element.Tag or a.ul is None:
                works.append(title + second)
                a.string = a.text.split("/")[0]
                continue
            # 多级列表下的工作清单
            for b in a.ul.contents:
                works.append(title + second + " " + b.next.replace('<p>', '').replace('</p>', ''))
                b.string = b.text.split("/")[0]
    return works


def create_work_log(work, sprint, project):
    user = configUtils.user()
    thread_list = []
    for i in work:
        sum = i.split('/')[0]
        for d in i.replace(sum, '').split('/'):
            if d == '':
                continue
            d = d.replace(' ','')
            date = datetime.strptime(str(datetime.now().year) + '-' + d.split(':')[0], '%Y-%m-%d')
            spend = d.split(':')[1] if len(d.split(':')) == 2 else '8h'
            t = MyThread(create_work, (sprint, sum, date, user, project, '任务', spend))
            while threading.active_count() > 20:
                time.sleep(0.4)
            t.start()
            thread_list.append(t)
    msg = []
    for i in thread_list:
        ret = i.get_result()
        if ret and not msg.__contains__(ret):
            msg.append(i.get_result())
    if msg:
        raise ReportError("部分提交结果错误,请改正后继续提交!: \n{}".format("".join(msg)))
    else:
        raise ReportError("提交成功!: \n 新建tempo数量:{}个".format(len(thread_list)))


def completed(text):
    lines = text.split('\n')
    r1 = re.compile(r'^[\s]*[0-9]+\.(.*)', re.S)
    r2 = re.compile(r'^[\s]*[0-9]+\. (.*)', re.S)
    for i, t in enumerate(lines):
        if not t:
            continue
        if t.startswith(' '):
            # 补齐空格
            sp = math.ceil((len(t) - len(t.lstrip())) / 4) * 4 * ' '
            t = sp + t.lstrip()
            lines[i] = t
        if re.match(r1, t) and not re.match(r2, t):
            lines[i] = re.sub(re.findall(r1, t)[0], ' ' + re.findall(r1, t)[0], t, count=1)
        if t and t.lstrip().startswith('-') and not t.lstrip().startswith('- '):
            lines[i] = re.sub('-', '- ', t, count=1)
    return "\n".join(lines)


def work(text, sprint, project):
    ptitle = re.compile(r'^[\s]*[0-9]+\. (.*)', re.S)
    pst = re.compile(r'^[\s]*[-*+] +(.*)', re.S)
    format = ''
    for i, t in enumerate(text.split('\n')):
        if t == '' or t.isspace() or t.startswith("## "):
            continue
        # 标题
        if re.match(ptitle, t) is not None or t.startswith('- '):
            if t.__contains__("/") or t.__contains__(":"):
                raise ReportError("第{}行错误,标题不能包含'/'或':'  \n错误内容: {}".format(i + 1, t))
        else:
            # 子标题
            sub = re.match(pst, t)
            if sub:
                # 补齐空格
                st = t[0:sub.regs[1][0]]
                sp = math.ceil((len(st) - len(st.lstrip())) / 2) * 4 * ' '
                t = sp + t.lstrip()
            else:
                raise ReportError(
                    "第{}行错误 \n标题或子标题必须以数字加.加空格或者-加空格或者##空格 "
                    "\neg: '1. 主标题1' 或 '- 主标题2' \n 或 ## 2022-06-13_06-17工作 \n错误内容: {}".format(
                        i + 1, t))
        # 校验时间消耗
        if len(t.split("/")) > 1:
            for index, v in enumerate(t.split('/')[1:]):
                d = v.replace(' ', '')
                if len(d.split(':')) > 1:
                    time = d.split(':')[1]
                    if not time.endswith('h') or not time[0: len(time) - 1].replace(".", '').isdigit():
                        raise ReportError(
                            "第{}行错误 \n时间消耗格式错误，必须是正确的日期 \neg: 01:01 或 01:01:2h \n错误内容: ({})".format(i + 1, d))
                try:
                    datetime.strptime(str(datetime.now().year) + '-' + d.split(':')[0], '%Y-%m-%d')
                except:
                    raise ReportError("第{}行错误 \n时间消耗格式错误，必须是正确的日期 \neg: 01:01 或 01:01:2h \n错误内容: ({})".format(i + 1, d))
        else:
            if t.__contains__("/") or t.__contains__(":"):
                raise ReportError("第{}行错误 \n子标题不允许包含:符号 \neg: '1. 图平台' 或 '- 图平台'  \n错误内容: ({})".format(i + 1, t))

        format += t + '\n'
    list = read_data(bs4.BeautifulSoup(markdown.markdown(format).replace("\n", ''), 'html.parser'))
    create_work_log(list, sprint, project)

import configparser
import json
import os
import sys

from jira import JIRA

from util.cyUtils import cyUtils

config = configparser.ConfigParser()
cp = os.path.join(os.path.dirname(sys.argv[0]), 'config.ini')
lf = os.path.join(os.path.dirname(sys.argv[0]), 'error.log')
export = os.path.join(os.path.dirname(sys.argv[0]), '项目支持统计.xlsx')
config.read(cp, encoding='utf-8')

host = 'https://jira.xxx.cn'
groups = ['请选择部门', '平台服务组', '测试组', '前端组', '大数据', '算法', '产品']
range = ['Week', 'Month', 'Year']
group_range = ['按区域', '按项目', '按部门', '按姓名']
prod_range = ['按产品', '按部门', '按姓名']

projects = {'Atlas图平台': '11723', '产品组工作': '11707', '前端组工作': '11708', '大数据及图挖掘组': '11711', '平台服务组': '11713', '平台架构组工作': '11710', '测试组': '11706', '算法组': '11709'}

jiras = None

prods = None
prjs = None

if not config.has_section('General'):
    config.add_section('General')


def project():
    return projects[list(projects.keys())[group_index()]]


def jira_client():
    global jiras
    if jiras is None:
        jiras = JIRA(host, max_retries=1, basic_auth=(user(), passwd()))
    return jiras

def get_prods():
    global prods
    if prods is None:
        try:
            prods = jira_client().editmeta('APITEAM-9246')['fields']['customfield_12000']['allowedValues']
        except:
            return None
    return prods

def get_prjs():
    global prjs
    if prjs is None:
        try:
            prjs = jira_client().editmeta('APITEAM-9246')['fields']['customfield_11907']['allowedValues']
        except:
            return None
    return prjs

def jira_cookie():
    return jira_client()._session.cookies


def user():
    if config['General'].__contains__('user'):
        return cyUtils().decrypt(config['General']['user'])


def permissions():
    issue = jira_client().issue('APITEAM-9246')
    permission = json.loads(issue.fields.description.replace(' ', ''))['permission']
    return permission.__contains__(user())


def passwd():
    if config['General'].__contains__('passwd'):
        return cyUtils().decrypt(config['General']['passwd'])

def my_graoup():
    if config['General'].__contains__('myGroup'):
        return config['General']['myGroup']


def path():
    if config['General'].__contains__('path'):
        return config['General']['path']


def group_index():
    try:
        return int(config['General']['group'])
    except:
        return 0


def range_index():
    try:
        return int(config['General']['range'])
    except:
        return 0


def set_group(group):
    config.read(cp, encoding='utf-8')
    config.set("General", 'group', str(group))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def set_range(group):
    config.read(cp, encoding='utf-8')
    config.set("General", 'range', str(group))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)

def set_prod_range(group):
    config.read(cp, encoding='utf-8')
    config.set("General", 'rangeP', str(group))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def set_path(group):
    if group == '' and config.has_option("General", 'path'):
        config.remove_option("General", 'path')
    config.read(cp, encoding='utf-8')
    config.set("General", 'path', str(group))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def set_user(user):
    config.read(cp, encoding='utf-8')
    config.set("General", 'user', str(user))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def set_passwd(passwd):
    config.read(cp, encoding='utf-8')
    config.set("General", 'passwd', str(passwd))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def set_content(option, content):
    config.read(cp, encoding='utf-8')
    config.set("General", option, str(content))
    with open(cp, "w+", encoding='utf-8') as f:
        config.write(f)


def get_content(option):
    if config['General'].__contains__(option):
        return config['General'][option]

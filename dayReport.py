# encoding=utf-8
import datetime
import json
from login import login

# 加载全局配置
with open("./config.json", "r", encoding="utf-8") as f:
    configs = f.read()
configs = json.loads(configs)


# 合并填报参数
def load_params(ss, mode):
    json_form = get_report_data(ss)  # 获取昨日填报信息
    if json_form is False:
        return False
    params = {
        "DZ_JSDTCJTW": 37,
        "DZ_DBRQ": "%Y-%m-%d",
        "CZRQ": "%Y-%m-%d %H:%M:%S",
        "CREATED_AT": "%Y-%m-%d %H:%M:%S",
        "NEED_CHECKIN_DATE": "%Y-%m-%d"
    }
    try:
        local = configs['dailyReport'][mode]
        params.update(local)
    except Exception:
        print("【加载本地配置失败，使用昨日信息进行填报】")

    # get time
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    today_list = ['CZRQ', 'CREATED_AT', 'NEED_CHECKIN_DATE']
    yesterday_list = ['DZ_DBRQ']
    for key in params.keys():
        # 填充日期
        if key in yesterday_list:
            params[key] = yesterday.strftime(params[key])
        elif key in today_list:
            params[key] = today.strftime(params[key])
        json_form[key] = params[key]
    # print(params)
    return json_form


def doReport(session, mode=''):
    """
    session: 已登录的 requests.session 对象
    mode:  填报配置 home, school 等，(留空使用昨天的填报信息)，可自行修改 config.json 文件
    """
    # 进入填报页面（获取sessionid）
    session.get("http://ehall.seu.edu.cn/appShow?appId=5821102911870447")

    url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/mobile/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'

    json_form = load_params(session, mode)
    res = session.post(url, data=json_form)
    try:
        if json.loads(res.text)['datas']['T_REPORT_EPIDEMIC_CHECKIN_SAVE'] == 1:
            print("填报成功！")
        else:
            print("填报失败！")
    except Exception:
        print(res.text)
        print("填报失败！")


# 获取昨日填报信息
def get_report_data(ss):
    # 进入填报页面（获取sessionid）
    ss.get("http://ehall.seu.edu.cn/appShow?appId=5821102911870447")
    url = "http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/getMyDailyReportDatas.do"
    params = {'rysflb': 'BKS', 'pageSize': 10, 'pageNumber': 1}
    res = ss.post(url, data=params)
    try:
        last_report = json.loads(
            res.text)['datas']['getMyDailyReportDatas']['rows'][0]
        # print(last_report)
    except Exception:
        print("【获取历史记录失败，请手动填报】")
        return False
    return last_report


if __name__ == '__main__':
    ss = login(configs['user']['cardnum'], configs['user']['password'])
    if ss:
        doReport(ss)

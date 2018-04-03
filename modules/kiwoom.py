# -*- coding: utf-8 -*-
import sys
import threading
import time

from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *

# import auto_login
import constant as const
import notification
import screen
from util import *
from __module import ModuleClass
import db_insert


class Api(ModuleClass):
    req = []
    input_value = []
    app = None
    account = ""
    start_date = ""
    subject_codes = []
    db_manager = None

    def __init__(self, start_date=""):
        super(Api, self).__init__()

        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KFOPENAPI.KFOpenAPICtrl.1")
        self.ocx.OnEventConnect[int].connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData[str, str, str, str, str].connect(self.OnReceiveTrData)

        self.start_date = start_date
        self.db_manager = db_insert.DBInsert()

        if self.connect == 0:
            self.app.exec_()

    '''
    Interface Methods
    '''

    @property
    def connect(self):
        """
        로그인 윈도우를 실행한다.
        로그인이 성공하거나 실패하는 경우 OnEventConnect 이벤트가 발생하고 이벤트의 인자 값으로 로그인 성공 여부를 알 수 있다.
        :return: 0 - 성공, 음수값은 실패
        """

        if self.ocx.dynamicCall("GetConnectState()") == 0:
            rtn = self.ocx.dynamicCall("CommConnect(1)")
            if rtn == 0:
                self.log.info("연결 성공")

                # auto login
                # lg = auto_login.Login()
                # lg.run()
            else:
                self.log.info("연결 실패")

            return rtn

    def get_login_info(self, sTag):
        """
        로그인한 사용자 정보를 반환한다.
        :param sTag: 사용자 정보 구분 TAG값
            “ACCOUNT_CNT” ? 전체 계좌 개수를 반환한다.
            "ACCNO" ? 전체 계좌를 반환한다. 계좌별 구분은 ‘;’이다.
            “USER_ID” - 사용자 ID를 반환한다.
            “USER_NAME” ? 사용자명을 반환한다.
            “KEY_BSECGB” ? 키보드보안 해지여부. 0:정상, 1:해지
            “FIREW_SECGB” ? 방화벽 설정 여부. 0:미설정, 1:설정, 2:해지
            Ex) openApi.GetLoginInfo(“ACCOUNT_CNT”);
        :return: TAG값에 따른 데이터 반환
        """
        return self.ocx.dynamicCall("GetLoginInfo(QString)", [sTag]).rstrip(';')

    def get_dynamic_subject_code(self):
        lists = ['MTL', 'ENG', 'CUR', 'IDX', 'CMD']
        for code in lists:
            self.set_input_value("상품코드", code)
            self.comm_rq_data("상품별현재가조회", "opt10006", "", screen.S0010)

    def get_dynamic_subject_market_time(self):
        lists = ['MTL', 'ENG', 'CUR', 'IDX', 'CMD']
        for list_ in lists:
            self.set_input_value("품목구분", list_)
            self.comm_rq_data("장운영정보조회", "opw50001", "", screen.S0011)

    def request_tick_info(self, subject_code, tick_unit, prevNext):

        self.set_input_value("종목코드", subject_code)
        self.set_input_value("시간단위", tick_unit)

        rqTag = "해외선물옵션틱차트조회" + "_" + subject_code + "_" + tick_unit

        self.comm_rq_data(rqTag, "opc10001", prevNext, screen.S9999)

    def send_request(self):
        if len(self.req) > 0:
            config = self.req[0]
            self.log.debug("send_request(), config : %s" % config)
            # log.debug("current thread : %s" % threading.current_thread().__class__.__name__)
            for input_value in config["InputValue"]:
                # log.debug("set input value, id : %s, value : %s" % (input_value[0], input_value[1]))
                self.ocx.dynamicCall("SetInputValue(QString, QString)", input_value[0], input_value[1])

            rtn = self.ocx.dynamicCall("CommRqData(QString, QString, QString, QString)", config['sRQName'],
                                       config['sTrCode'], config['nPrevNext'], config['sScreenNo'])
            # log.debug("send_request(), rtn value : %s" % rtn)

            if rtn == 0:
                del self.req[0]

                # debug code
                if len(self.req) > 0:
                    time.sleep(0.25)
                    self.send_request()
            else:
                self.err_log.error('send request() : %s' % parse_error_code(rtn))

    def set_input_value(self, sID, sValue):
        """
        Tran 입력 값을 서버통신 전에 입력한다.
        :param sID: 아이템명
        :param sValue: 입력 값
        Ex) openApi.SetInputValue(“종목코드”, “000660”);
            openApi.SetInputValue(“계좌번호”, “5015123401”);
        """
        try:
            self.log.debug("set_input_value(), sID: %s, sValue: %s" % (sID, sValue))
            # rq_thread.set_input_value(sID, sValue)
            self.input_value.append([sID, sValue])
        except Exception as err:
            self.log.error(get_error_msg(err))

    def comm_rq_data(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        try:
            self.log.debug("comm_rq_data(), sRQName: %s, sTrCode: %s, nPrevNext: %s, sScreenNo: %s"
                           % (sRQName, sTrCode, nPrevNext, sScreenNo))
            request_config = {"InputValue": self.input_value,
                              "sRQName": sRQName,
                              "sTrCode": sTrCode,
                              "nPrevNext": nPrevNext,
                              "sScreenNo": sScreenNo}

            self.input_value = []
            self.req.append(request_config)

            time.sleep(0.25)
            self.send_request()

        except Exception as err:
            self.log.error(get_error_msg(err))

    def quit(self):
        """ Quit the server """
        QApplication.quit()
        sys.exit()

    '''
    Control Event Handlers
    '''

    def OnEventConnect(self, nErrCode):
        """
        통신 연결 상태 변경시 이벤트
        :param nErrCode: 에러 코드 - 0이면 로그인 성공, 음수면 실패, 에러코드 참조
        """
        self.log.info("OnEventConnect received")

        if nErrCode == 0:
            self.log.info("로그인 성공")
            # 계좌번호 저장
            self.account = self.get_login_info("ACCNO")
            self.log.info("계좌번호 : " + self.account)

            # 다이나믹 종목 정보 요청
            self.get_dynamic_subject_code()

            # self.send_request()

        elif nErrCode == -101:
            # wait_time = (06:45).to_sec() - time.time()
            # time.sleep(wait_time)
            # const.MODE = const.DB_INSERT
            # DB INSERT CODE
            pass

        else:
            # 로그인 실패 로그 표시 및 에러코드별 에러내용 발송
            self.err_log.error('로그인 실패[%s]' % parse_error_code(nErrCode))
            self.quit()

    def OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext):
        """
        Tran 수신시 이벤트
        서버통신 후 데이터를 받은 시점을 알려준다.
        :param py: 화면번호
        :param sRQName: 사용자구분 명
        :param sTrCode: Tran 명
        :param sRecordName: Record 명
        :param sPreNext: 연속조회 유무
        :param nDataLength: 1.0.0.1 버전 이후 사용하지 않음.
        :param sErrorCode: 1.0.0.1 버전 이후 사용하지 않음.
        :param sMessage: 1.0.0.1 버전 이후 사용하지 않음.
        :param sSplmMsg: 1.0.0.1 버전 이후 사용하지 않음.
        """
        self.log.debug("current thread : %s" % threading.current_thread().__class__.__name__)
        self.log.debug("onReceiveTrData, sScrNo : %s, sRQName : %s, sTrCode : %s, sRecordName : %s, sPreNext : %s" % (
            sScrNo, sRQName, sTrCode, sRecordName, sPreNext))

        try:
            if sRQName == '상품별현재가조회':
                self.log.debug("onRecieveTrData: 상품별현재가조회")
                const.RECEVIED_PRODUCT_CNT += 1
                for i in range(20):
                    subject_code = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode,
                                                        sRecordName, i, '종목코드n').strip()  # 현재가 = 틱의 종가
                    if subject_code == "": break

                    self.log.debug("상품별현재가조회, 종목코드 : %s" % subject_code)
                    self.subject_codes.append(subject_code)

                if const.TOTAL_PRODUCT_CNT == const.RECEVIED_PRODUCT_CNT:
                    self.get_next_subject_data()

            elif '해외선물옵션틱차트조회' in sRQName:
                params = sRQName.split('_')
                chart_type = const.틱차트
                time_unit = params[2]
                subject_code = params[1]

                self.log.debug("해외선물옵션틱차트조회 params : %s" % params)

                data_str = self.ocx.dynamicCall("GetCommFullData(QString, QString, int)", sTrCode,
                                                sRecordName, 0)

                tmp_data = parse_data(data_str.split())

                if (len(tmp_data) < 10):
                    self.log.info("%s 종목 해당 종목 데이터 미량으로 Pass." % subject_code)
                    self.get_next_subject_data()
                    return
                recv_working_day = tmp_data[0][3]

                if len(self.data) == 0 and len(tmp_data) < 600:
                    self.log.info("%s 종목 해당 종목 데이터 미량으로 Pass." % subject_code)
                    self.get_next_subject_data()
                    return

                # self.log.info(tmp_data[0])
                if recv_working_day < self.tmp_start_date:
                    while True:
                        tuple = tmp_data[0]
                        if tuple[3] < self.tmp_start_date or datetime.datetime.strptime(tuple[3],
                                                                                        "%Y-%m-%d").date() == datetime.date.today():
                            tmp_data.pop(0)
                            if len(tmp_data) == 0: break
                        else:
                            break

                    self.data = tmp_data + self.data
                    self.db_manager.insert_data(subject_code, self.data)
                    self.log.info("%s 종목 DB 저장 완료." % subject_code)
                    self.get_next_subject_data()
                elif len(self.data) >= 600 and str(tmp_data[-1][3]) < str(self.data[0][3]):
                    # 싸이클 돔
                    if self.db_manager.is_empty_table(subject_code) or self.last_working_day < recv_working_day:
                        while True:
                            tuple = tmp_data[0]
                            if tuple[3] > self.tmp_start_date:
                                tmp_data.pop(0)
                                if len(tmp_data) == 0: break
                            else:
                                break

                        self.data = tmp_data + self.data
                        self.db_manager.insert_data(subject_code, self.data)
                        self.log.info("%s 종목 DB 저장 완료." % subject_code)
                        self.get_next_subject_data()
                # DB를 넣는데 당일 개장후 넣을때 들어가는 부분
                elif len(self.data) >= 600 and str(tmp_data[-1][3]) > str(self.data[0][3]):
                    if self.last_working_day < recv_working_day:
                        while True:
                            tmp_data.reverse()
                            tuple = tmp_data[0]
                            if tuple[3] > self.tmp_start_date:
                                tmp_data.pop(0)
                                if len(tmp_data) == 0: break
                            else:
                                break
                        tmp_data.reverse()
                        self.data = tmp_data + self.data
                        self.db_manager.insert_data(subject_code, self.data)
                        self.log.info("%s 종목 DB 저장 완료." % subject_code)
                        self.get_next_subject_data()
                else:
                    while True:
                        tuple = tmp_data[0]
                        if datetime.datetime.strptime(tuple[3], "%Y-%m-%d").date() == datetime.date.today():
                            tmp_data.pop(0)
                            if len(tmp_data) == 0: break
                        else:
                            break
                    self.data = tmp_data + self.data
                    #self.log.info("%s 종목 연속조회 요청." % subject_code)
                    self.request_tick_info(subject_code, "1", sPreNext)

                '''
                recv_working_day = tmp_data.get_working_day()
                if recv_working_day < start_date:
                    a = 내 시작일
                    self.data.append(tmp_data[a:])
                    db_manager.insert(self.data)
                    get_next_subject_data
                elif recv_working_day > tmp_data_working_day:
                    싸이클 돔
                    if table is empty OR 테이블의 마지막 workingday가 내가 받아온 workingday보다 이전일때:
                        다 넣어
                        get_next_subject_data
                    else 
                        다 버림
                        get_next_subject_data
                else:
                    self.data.append(tmp_data[1:])
                    request_tick_info(subject_code, 1, prevNext)
                            '''

        except Exception as err:
            self.log.error(get_error_msg(err))

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())

    def get_next_subject_data(self):
        try:
            start_date = self.start_date
            if len(self.subject_codes) > 0:
                subject_code = self.subject_codes.pop(0)
                # print(subject_code)
                # if subject_code =='FDAXM18':
                #     subject_code = self.subject_codes.pop(0)
                self.data = []
                self.last_working_day = self.db_manager.get_last_working_day(subject_code)
                self.log.info("%s 종목 last_working_day : %s" % (subject_code, self.last_working_day))

                if start_date > self.last_working_day:
                    self.log.info("입력일이 마지막 저장된 영업일 이후입니다. (%s)" % subject_code)
                    self.get_next_subject_data()
                else:
                    self.log.info("%s 종목 start_date : %s" % (subject_code, start_date))
                    if start_date == "": self.tmp_start_date = get_next_date(self.last_working_day)
                    self.log.info("%s 종목 tmp_start_date : %s" % (subject_code, self.tmp_start_date))
                    self.request_tick_info(subject_code, "1", "")
            elif len(self.subject_codes) <= 0:
                notification.sendMessage('DB검증을 시작합니다.',None)
                db_subect_code = self.db_manager.get_subject_code()
                #db에 있는 모든 2018년도 월물 찾아서 그중 금,유로,크루드,mini-S&P,엔화를 찾아서 DB검증실시
                for db_sub_code in db_subect_code:
                    self.last_working_day = self.db_manager.get_last_working_day(db_sub_code[0])
                    if(self.db_manager.check_subject_code(db_sub_code[0], self.last_working_day)==None):
                        pass
                    else:
                        if(db_sub_code[0].find('GC')==0 or db_sub_code[0].find('6E')==0 or db_sub_code[0].find('CL')==0 or db_sub_code[0].find('ES')==0 or db_sub_code[0].find('6J')==0) :
                            d = self.db_manager.check_first_input(db_sub_code[0], self.last_working_day)
                            l = self.db_manager.check_last_input(db_sub_code[0], self.last_working_day)
                            if(d=='err'or l=='err'):
                                notification.sendMessage('틀렸다...%s'%db_sub_code[0],None)
                            elif((l[0]-d[0])>datetime.timedelta(hours=22,minutes=59,seconds=30)):
                                self.log.info("%s종목 정상데이터 시작 %s - 끝 %s"%(db_sub_code[0],d[0].isoformat(),l[0].isoformat()))
                            else:
                                self.log.info("%s 종목의 입력갑의 spread가 틀렸다...%s" % (db_sub_code[0],(l[0]-d[0])))
                                notification.sendMessage('%s 종목의 입력갑의 spread가 틀렸다...%s' % (db_sub_code[0],(l[0]-d[0])),None)
                        #항생은 시작시간과 마감시간이 다름
                        elif(db_sub_code[0].find('HSI')==0):
                            d = self.db_manager.check_first_input(db_sub_code[0], self.last_working_day)
                            l = self.db_manager.check_last_input(db_sub_code[0], self.last_working_day)
                            if (d == 'err' or l == 'err'):
                                notification.sendMessage('틀렸다...%s' % db_sub_code[0],None)
                            elif ((l[0] - d[0]) > datetime.timedelta(hours=23,minutes=14)):
                                self.log.info(
                                    "%s종목 정상데이터 시작 %s - 끝 %s" % (db_sub_code[0], d[0].isoformat(), l[0].isoformat()))
                            else:
                                self.log.info("%s 종목의 입력갑의 spread가 틀렸다...%s" % (db_sub_code[0], (l[0] - d[0])))
                                notification.sendMessage(
                                    '%s 종목의 입력갑의 spread가 틀렸다...%s' % (db_sub_code[0], (l[0] - d[0])),None)
                notification.sendMessage('DB정상입력확인완료',None)
        except Exception as err:
            self.log.error(get_error_msg(err))

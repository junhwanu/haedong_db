# -*- coding: utf-8 -*-
import sys
import threading
import time

from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *

import auto_login
import constant as const
import screen
from util import *
from __module import ModuleClass


class Api(ModuleClass):
    req = []
    input_value = []
    app = None
    account = ""
    subject_code = ''

    def __init__(self):
        super(Api, self).__init__()

        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KFOPENAPI.KFOpenAPICtrl.1")
        self.ocx.OnEventConnect[int].connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData[str, str, str, str, str].connect(self.OnReceiveTrData)

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
                lg = auto_login.Login()
                lg.start()

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

        self.comm_rq_data(rqTag, "opc10001", prevNext, self.subject_var.info[subject_code]['화면번호'])

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
                    self.last_req_time = time.time()
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

            now = time.localtime()
            if const.MODE == const.REAL and \
                    ((now.tm_wday == 5 and get_time(0, None) > 600) or (now.tm_wday == 6)):
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
            self.telepot.set_account(self.account)
            self.telepot.send_message('해동이 정상 시작 됨.')
            self.log.info("계좌번호 : " + self.account)

            if const.MODE is const.REAL:
                # 다이나믹 종목 정보 요청
                self.get_dynamic_subject_code()
                self.get_futures_deposit()
                # self.get_my_deposit_info()

                # 종목 정보 로그 찍기
                self.log.info("참여 종목 : %s" % self.subject_var.info.values())

            self.send_request()

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

    def OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext, candle=None):
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
        self.log.info("onReceiveTrData, sScrNo : %s, sRQName : %s, sTrCode : %s, sRecordName : %s, sPreNext : %s" % (sScrNo, sRQName, sTrCode, sRecordName, sPreNext))

        try:
            if sRQName == '상품별현재가조회':
                self.log.debug("onRecieveTrData: 상품별현재가조회")
                for i in range(20):
                    subject_code = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode,
                                                        sRecordName, i, '종목코드n').strip()  # 현재가 = 틱의 종가
                    subject_symbol = subject_code[:2]
                    self.log.debug("상품별현재가조회, 종목코드 : %s" % subject_code)
                    if subject_symbol in self.subject_var.info:
                        self.log.info("금일 %s의 종목코드는 %s 입니다." % (self.subject_var.info[subject_symbol]["종목명"], subject_code))
                        self.subject_var.info[subject_code] = self.subject_var.info[subject_symbol]
                        self.strategy_var.info[subject_code] = self.strategy_var.info[subject_symbol]
                        del self.subject_var.info[subject_symbol]
                        del self.strategy_var.info[subject_symbol]

                        self.chart_manager.init_data(subject_code)
                        # 초기 데이터 요청
                        for chart_config in self.strategy_var.info[subject_code][self.subject_var.info[subject_code]['전략']][const.차트]:
                            type_ = chart_config[0]
                            time_unit = chart_config[1]

                            self.log.debug("chart_config : %s" % chart_config)
                            if type_ == const.틱차트:
                                self.request_tick_info(subject_code, time_unit, "")
                            elif type_ == const.분차트:
                                self.request_min_info(subject_code, time_unit, "")

            elif '해외선물옵션틱차트조회' in sRQName:
                params = sRQName.split('_')
                chart_type = const.틱차트
                time_unit = params[2]
                subject_code = params[1]

                self.log.debug("해외선물옵션틱차트조회 params : %s" % params)

                if subject_code in self.subject_var.info:
                    if const.MODE is const.REAL:
                        data_str = self.ocx.dynamicCall("GetCommFullData(QString, QString, int)", sTrCode,
                                                        sRecordName, 0)

                        chart_data = self.chart_manager.data[subject_code][chart_type][time_unit]  # 차트 타입과 시간단위에 맞는 차트 불러옴

                        if len(chart_data['임시데이터']) == 0:
                            ''' 가장 처음 데이터가 수신 되었을 때 '''
                            self.log.info("데이터 수신 시작. 차트구분 : %s, 시간단위 : %s" % (chart_type, time_unit))
                            chart_data['임시데이터'] = data_str.split()

                            chart_data['현재가변동횟수'] = int(chart_data['임시데이터'][0])
                            chart_data['현재캔들'] = {}
                            chart_data['현재캔들']['현재가'] = float(chart_data['임시데이터'][1])
                            chart_data['현재캔들']['거래량'] = int(chart_data['임시데이터'][2])
                            chart_data['현재캔들']['체결시간'] = str(chart_data['임시데이터'][3])
                            chart_data['현재캔들']['시가'] = float(chart_data['임시데이터'][4])
                            chart_data['현재캔들']['고가'] = float(chart_data['임시데이터'][5])
                            chart_data['현재캔들']['저가'] = float(chart_data['임시데이터'][6])
                            chart_data['현재캔들']['영업일자'] = str(chart_data['임시데이터'][7])

                            chart_data['임시캔들'] = []    # 초기 데이터 수신 중 완성된 캔들을 임시로 저장하고, 수신이 완료된 후 Push

                            if chart_data['현재가변동횟수'] == int(time_unit):
                                self.log.debug("수신 된 첫 캔들이 이미 완성된 캔들이므로, 임시 캔들에 추가함.")
                                chart_data['임시캔들'].append(chart_data['현재캔들'])
                                self.chart_manager.init_current_candle(subject_code, chart_type, time_unit)

                            for tick in chart_data['임시틱']:
                                ''' 첫 번째 데이터 수신 전 해당 차트로부터 들어온 Tick들 처리 '''
                                if chart_data['현재가변동횟수'] == 0:
                                    chart_data['현재캔들']['시가'] = tick[0]

                                chart_data['현재가변동횟수'] += 1
                                if tick[0] < chart_data['현재캔들']['저가']:
                                    chart_data['현재캔들']['저가'] = tick[0]
                                if tick[0] > chart_data['현재캔들']['고가']:
                                    chart_data['현재캔들']['고가'] = tick[0]

                                if chart_data['현재가변동횟수'] == time_unit:
                                    chart_data['현재캔들']['체결시간'] = tick[1]
                                    chart_data['현재캔들']['현재가'] = tick[0]
                                    chart_data['현재가변동횟수'] = 0
                                    if chart_data['인덱스'] == -1:
                                        chart_data['임시캔들'].append(chart_data['현재캔들'])
                                    else:
                                        self.chart_manager.push(subject_code, chart_type, time_unit, chart_data['현재캔들'])
                        else:
                            ''' 데이터 수신 중간 '''
                            self.log.info("데이터 수신 중. 차트구분 : %s, 시간단위 : %s" % (chart_type, time_unit))
                            chart_data['임시데이터'] = chart_data['임시데이터'] + data_str.split()[1:]

                        if len(chart_data['임시데이터']) / 7 > self.strategy_var.info[subject_code][self.subject_var.info[subject_code]['전략']][const.차트변수][chart_type][time_unit][const.초기캔들수]:
                            ''' 데이터 수신 완료 '''

                            self.log.info("데이터 수신 완료. 차트구분 : %s, 시간단위 : %s" % (chart_type, time_unit))
                            current_idx = len(chart_data['임시데이터']) - 7

                            candle = {}
                            while current_idx > 8:
                                candle['현재가'] = float(chart_data['임시데이터'][current_idx])
                                candle['거래량'] = int(chart_data['임시데이터'][current_idx + 1])
                                candle['체결시간'] = str(chart_data['임시데이터'][current_idx + 2])
                                candle['시가'] = float(chart_data['임시데이터'][current_idx + 3])
                                candle['고가'] = float(chart_data['임시데이터'][current_idx + 4])
                                candle['저가'] = float(chart_data['임시데이터'][current_idx + 5])
                                candle['영업일자'] = str(chart_data['임시데이터'][current_idx + 6])
                                current_idx -= 7

                                self.chart_manager.push(subject_code, chart_type, time_unit, candle)

                            if len(chart_data['임시캔들']) > 0:
                                self.log.info("데이터 수신 중 완성된 임시캔들들 Push.")
                                for candle in chart_data['임시캔들']:
                                    self.chart_manager.push(subject_code, chart_type, time_unit, candle)

                            isEnd = True
                            for chart_config in self.strategy_var.info[subject_code][self.subject_var.info[subject_code]['전략']][const.차트]:
                                chart_type = chart_config[0]
                                time_unit = chart_config[1]

                                if self.chart_manager.data[subject_code][chart_type][time_unit]['인덱스'] < \
                                        self.strategy_var.info[subject_code][self.subject_var.info[subject_code]['전략']][const.차트변수][chart_type][time_unit][const.초기캔들수]:
                                    isEnd = False
                                    break

                            if isEnd:
                                self.chart_manager.data[subject_code]['상태'] = '매매가능'

                        else:
                            self.request_tick_info(subject_code, time_unit, sPreNext)

                    elif const.MODE is const.TEST:
                        pass

        except Exception as err:
            self.log.error(get_error_msg(err))

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())

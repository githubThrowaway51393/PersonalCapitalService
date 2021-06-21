from flask import Flask, json
from persCapAPI import *
from jsonutils import *
from dateutils import *
from encryptor import *
from stringutils import *
from holdings import *
from accounts import *
from transactions import *
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
import time
import atexit
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from flask_basicauth import BasicAuth

api = Flask(__name__)

#This is likely not how you want to handle secrets. You'd probably want to store them elsewhere and reference them here. If you're using some sort of CI/CD building like Jenkins, you can use secrets through that application and pass them in as environment variables
api.config['BASIC_AUTH_USERNAME'] = 'ENTER_A_USER'
api.config['BASIC_AUTH_PASSWORD'] = 'ENTER_A_PASSWORD'

basic_auth = BasicAuth(api)
pc = setup_login();
    
def init_scheduler(pc):
    print("Refreshing the session")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=pc.refresh_session, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

def is_received(received):
    return received == "received"
    
@api.route('/')
@basic_auth.required
def hello_world():
    return 'HELLO WORLD!!!!'
  
@api.route('/accounts', methods=['GET'])
@basic_auth.required
def get_accounts():
    return get_account_values_as_json(pc), 200
    
@api.route('/trans/<int:num_days>', methods=['GET'])
@basic_auth.required
def get_transactions(num_days):
    to_return = get_transactions_response_before_today(pc, num_days)
    return return_as_json(to_return), 200
    
@api.route('/trans/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    return return_as_json(to_return), 200

@api.route('/trans/<string:accountName>/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_transactions_between_dates_by_account(accountName, start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_transactions_by_account(to_return, accountName)
    return return_as_json(), 200
    
@api.route('/trans/all/lastmonth', methods=['GET'])
@basic_auth.required
def get_all_of_last_months_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = basic_transactions_cleanup(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/<string:accountName>/lastmonth', methods=['GET'])
@basic_auth.required
def get_all_of_last_months_transactions_by_account(accountName):
    to_return = get_last_months_transactions(pc)
    to_return = basic_transactions_cleanup(to_return)
    to_return = get_transactions_by_account(to_return, accountName)
    return return_as_json(to_return), 200
    
@api.route('/trans/expenses/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_expense_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_expense_transactions(to_return)
    return return_as_json(to_return), 200

@api.route('/trans/expenses/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_expense_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_expense_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/expenses/all', methods=['GET'])
@basic_auth.required
def get_all_expense_transactions():
    to_return = get_transactions_response_before_today(pc, 9999)
    to_return = get_expense_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/<string:invtype>/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_investment_transactions(invtype):
    to_return = get_last_months_transactions(pc)
    to_return = get_investment_transactions(to_return, invtype)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/Shares_In/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_sharesin_investment_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_sharesin_investment_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/Shares_In/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_sharesin_investment_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_sharesin_investment_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/Shares_Out/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_sharesout_investment_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_sharesout_investment_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/Shares_Out/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_sharesout_investment_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_sharesout_investment_transactions(to_return)
    return return_as_json(to_return), 200

@api.route('/trans/investments/<string:invtype>/<string:accountName>/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_investment_transactions_by_account(accountName, invtype):
    to_return = get_last_months_transactions(pc)
    to_return = get_investment_transactions(to_return, invtype)
    to_return = get_transactions_by_account(to_return, accountName)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/<string:invtype>/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_last_months_investment_transactions_between_dates(start, end, invtype):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_investment_transactions(to_return, invtype)
    return return_as_json(to_return), 200
    
@api.route('/trans/investments/<string:invtype>/<string:accountName>/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_last_months_investment_transactions_between_dates_by_account(accountName, start, end, invtype):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_investment_transactions(to_return, invtype)
    to_return = get_transactions_by_account(to_return, accountName)
    return return_as_json(to_return), 200
    
@api.route('/trans/dividends/<string:recieved>/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_dividend_transactions(recieved):
    to_return = get_last_months_transactions(pc)
    to_return = get_dividend_transactions(to_return, is_received(recieved))
    return return_as_json(to_return), 200
    
@api.route('/trans/dividends/<string:recieved>/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_dividend_transactions_between_dates(start, end, recieved):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_dividend_transactions(to_return, is_received(recieved))
    return return_as_json(to_return), 200
    
@api.route('/trans/dividends/<string:recieved>/<string:accountName>/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_dividend_transactions_by_account(accountName, recieved):
    to_return = get_last_months_transactions(pc)
    to_return = get_dividend_transactions(to_return, is_received(recieved))
    to_return = get_transactions_by_account(to_return, accountName)
    return return_as_json(to_return), 200
    
@api.route('/trans/dividends/<string:recieved>/<string:accountName>/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_dividend_transactions_between_dates_by_account(accountName, start, end, recieved):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_dividend_transactions(to_return, is_received(recieved))
    to_return = get_transactions_by_account(to_return, accountName)    
    return return_as_json(to_return), 200
    
@api.route('/trans/match/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_401k_match_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_401k_transactions(to_return, True)
    return return_as_json(to_return), 200
    
@api.route('/trans/match/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_401k_match_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_401k_transactions(to_return, True)
    return return_as_json(to_return), 200    
 
@api.route('/trans/401k/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_401k_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_401k_transactions(to_return, False)
    return return_as_json(to_return), 200
    
@api.route('/trans/401k/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_401k_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_401k_transactions(to_return, False)
    return return_as_json(to_return), 200
    
@api.route('/trans/401k/rollover/<string:start>/<string:end>', methods=['GET'])
@basic_auth.required
def get_401k_rollover_transactions_between_dates(start, end):
    to_return = get_transactions_response_between_dates(pc, start, end)
    to_return = get_401k_rollover_transactions(to_return)
    return return_as_json(to_return), 200   
    
@api.route('/trans/401k/rollover/thismonth', methods=['GET'])
@basic_auth.required
def get_this_months_401k_rollover_transactions():
    to_return = get_this_months_transactions(pc)
    to_return = get_401k_rollover_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/trans/401k/rollover/lastmonth', methods=['GET'])
@basic_auth.required
def get_last_months_401k_rollover_transactions():
    to_return = get_last_months_transactions(pc)
    to_return = get_401k_rollover_transactions(to_return)
    return return_as_json(to_return), 200
    
@api.route('/holdings', methods=['GET'])
@basic_auth.required
def get_holdings():
    return get_holdings_as_json(pc), 200
    
@api.route('/holdings/classifications', methods=['GET'])
@basic_auth.required
def get_holdings_classifications():
    return get_holding_classifications_as_json(pc), 200

@api.errorhandler(Exception)
def generic_error(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": traceback.format_exc(),
    })
    response.content_type = "application/json"
    return response
    
@api.errorhandler(404)
def error_404(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": traceback.format_exc(),
    })
    response.content_type = "application/json"
    return response

@api.errorhandler(500)
def error_500(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": traceback.format_exc(),
    })
    response.content_type = "application/json"
    return response

if __name__ == '__main__':
    init_scheduler(pc)
    api.run(host="0.0.0.0", debug=True)
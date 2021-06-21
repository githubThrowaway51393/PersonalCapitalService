from persCapAPI import *
from jsonutils import *
from dateutils import *
from encryptor import *
from stringutils import *
from fileio import *

DATE_FORMAT='%Y-%m-%d'   

def set_category_for_transaction(transaction, pc):
    matched = next(item for item in pc.cat_map["categories"] if item["id"] == transaction['categoryId'])
    cat = { "category": matched['name'] }
    transaction.update(cat)
    
def set_category_for_list_of_transactions(transactions, pc):
    for t in transactions:
        set_category_for_transaction(t, pc)
    return transactions

def get_transactions_response_between_dates(pc, start_date, end_date):  
    res = pc.fetch('/transaction/getUserTransactions', {
        'sort_cols': 'transactionTime',
        'sort_rev': 'true',
        'page': '0',
        'rows_per_page': '100',
        'startDate': start_date,
        'endDate': end_date,
        'component': 'DATAGRID'
    })
    try:
        trans = res.json()['spData']['transactions']
    except KeyError: 
        trans = {}
    return set_category_for_list_of_transactions(trans, pc)
  
def get_last_months_transactions(pc):
    return get_transactions_response_between_dates(pc, get_first_of_last_month(DATE_FORMAT), get_last_of_last_month(DATE_FORMAT))
 
def get_this_months_transactions(pc):
    return get_transactions_response_between_dates(pc, get_first_of_this_month(DATE_FORMAT), get_last_of_this_month(DATE_FORMAT))
 
def get_transactions_response_before_today(pc, days):
    now = datetime.now()
    start_date = (now - (timedelta(days=days+1))).strftime(DATE_FORMAT)
    end_date = (now - (timedelta(days=1))).strftime(DATE_FORMAT)
    return get_transactions_response_between_dates(pc, start_date, end_date) 
    
def basic_transactions_cleanup(dict):
    remove_from_json_list = read_ignore_file_into_list("transactiondataignore.txt");
    for t in dict:
        for p in remove_from_json_list:
            t.pop(p,None)
        
    return dict
    
def get_expense_transactions(dict):
    dict = basic_transactions_cleanup(dict)
    for i in reversed(range(len(dict))):
        if(dict[i]['isSpending']==False or dict[i]['isCashIn']==True):
            del dict[i]
            
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_dividend_transactions(dict, received):
    dict = basic_transactions_cleanup(dict)
    for i in reversed(range(len(dict))):
        try:
            item = dict[i]['transactionType']
        except KeyError:
            del dict[i]
            continue
        if(item!='Reinvest Dividend'):
            if(not received):
                del dict[i]
        if(item!='Dividend Received'):
            if(received):
                del dict[i]
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_investment_transactions(dict, invtype):
    dict = basic_transactions_cleanup(dict)
    for i in reversed(range(len(dict))):
        try:
            item = dict[i]['transactionType']
        except KeyError:
            del dict[i]
            continue
        if(item!=invtype):
            del dict[i]
                
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_sharesin_investment_transactions(dict):
    dict = get_investment_transactions(dict, "Shares In")['transactions']
    for i in reversed(range(len(dict))):
        try:
            amount = dict[i]['amount']
            quantity = dict[i]['quantity']
            desc = dict[i]['description']
        except KeyError:
            del dict[i]
            continue
        if(amount==0.0 or quantity==0):
            del dict[i]
            continue
        if('transfer In' in desc):
            del dict[i]
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_sharesout_investment_transactions(dict):
    dict = get_investment_transactions(dict, "Shares Out")['transactions']
    for i in reversed(range(len(dict))):
        try:
            amount = dict[i]['amount']
            quantity = dict[i]['quantity']
            desc = dict[i]['description']
        except KeyError:
            del dict[i]
            continue
        if(amount==0.0 or quantity==0):
            del dict[i]
            continue
        if('transfer In' in desc):
            del dict[i]
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_transactions_by_account(dict, account):
    try:
        trans = dict['transactions']
    except Exception:
        trans = dict
    for i in reversed(range(len(trans))):
        if(trans[i]['accountName'] != account):
            del trans[i]
    
    trans = {
        "transactions" : trans
    }
    return trans
    
def get_transactions_by_symbol_or_desc(dict, identifier):
    try:
        trans = dict['transactions']
    except Exception:
        trans = dict
    for i in reversed(range(len(trans))):
        try:
            item = trans[i]['symbol']
        except Exception:
            item = trans[i]['description']
        if(item != identifier):
            del trans[i]
    
    trans = {
        "transactions" : trans
    }
    return trans
    
def get_401k_rollover_transactions(dict):
    dict = basic_transactions_cleanup(dict)
    for i in reversed(range(len(dict))):
        try:
            item = dict[i]['transactionType']
            category = dict[i]['category']
            quantity = dict[i]['quantity']
        except KeyError:
            del dict[i]
            continue
        if(quantity==0):
            del dict[i]
            continue
        if(item!='Adjusted Sell' or category!='Securities Trades'):
            del dict[i]
    
    trans = {
        "transactions" : dict
    }
    return trans
    
def get_401k_transactions(dict, match):
    dict = basic_transactions_cleanup(dict)
    #First get all contributions
    for i in reversed(range(len(dict))):
        try:
            item = dict[i]['transactionType']
            category = dict[i]['category']
            quantity = dict[i]['quantity']
        except KeyError:
            del dict[i]
            continue
        if(quantity==0):
            del dict[i]
            continue
        if(item!='Contribution' and category!='Retirement Contributions'):
            del dict[i]
    compare_dict = dict.copy()
    #Then delete duplicates which have a higher or lower value depending on desired (match vs original contribs)        
    for i in reversed(range(len(compare_dict))):
        first = compare_dict[i]
        for j in range(len(compare_dict)):
            check = compare_dict[j]
            if(first['userTransactionId'] == check['userTransactionId']):
                continue
            if(first['description']==check['description']):
                if(first['transactionDate']==check['transactionDate']):
                    if(first['amount'] <= check['amount']):
                        if(match):
                            del compare_dict[j]
                            del dict[j]
                            break
                        else:
                            break
                        
    trans = {
        "transactions" : dict
    }
    return trans

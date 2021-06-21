from persCapAPI import *
from jsonutils import *
from dateutils import *
from encryptor import *
from stringutils import *
from fileio import *
from accounts import * 

IGNORE_PATH = "./ignores/"

def get_holdings_as_json(pc):
    remove_from_json_list = read_ignore_file_into_list("holdingsdataignore.txt")
    
    accounts = get_account_values_new_as_json(pc)
    res = pc.fetch('/invest/getHoldings')
    hold_json = decode_utf8(json.dumps(res.json()['spData'], ensure_ascii=False, sort_keys=True))
    hold_json = json.loads(hold_json)
    hold_json.pop('classifications',None)
    hold_json.pop('holdingsTotalValue',None)
    
    for h in hold_json['holdings']:
        if(h.get('ticker') is None or h.get('ticker')==""):
            h = set_missing_ticker(pc, h)
        for r in remove_from_json_list:
            h.pop(r,None)
        h = set_account_type_for_holding(pc, accounts, h)
        
        
    return return_as_json(hold_json)
    
def get_holding_classifications_as_json(pc):
    remove_from_json_list = read_ignore_file_into_list("holdingsdataignore.txt")
    
    accounts = get_account_values_new_as_json(pc)
    res = pc.fetch('/invest/getHoldings',  {
        'classificationStyles': "[\"allocation\"]"
    })
    class_json = decode_utf8(json.dumps(res.json()['spData'], ensure_ascii=False, sort_keys=True))
    class_json = json.loads(class_json)
    class_json.pop('holdings',None)
    class_json.pop('holdingsTotalValue',None)
    
    main_classifications = class_json['classifications'][0]['classifications']
    
    upper_classes = []
    for upper_class in main_classifications:
        to_add = {
            'type' : upper_class['classificationTypeName'],
            'percentOfTotal' : (upper_class['percentOfTMV'] / 100),
            'value' : upper_class['value']
        }
        if(upper_class.get('classifications') is not None):
            lower_classes = []
            for lower_class in upper_class.get('classifications'):
                a_class = {
                    'type' : lower_class['classificationTypeName'],
                    'percentOfTotal' : (lower_class['percentOfTMV'] / 100),
                    'value' : lower_class['value']
                }
                lower_classes.append(a_class)
            to_add['inner_types'] = lower_classes
        upper_classes.append(to_add)
    
    allocations = {
        'allocations' : upper_classes
    }
    
    return return_as_json(allocations)
    
def get_asset_classification(pc, sourceAssetId, userAccountId):
    remove_from_json_list = read_ignore_file_into_list("holdingsdataignore.txt")
    
    
    res = pc.fetch("/invest/getAssetClassification", {
        'sourceAssetId': sourceAssetId,
        'userAccountId': userAccountId,
        'classificationStyles': "[\"all\"]"
    })
    asset_json = decode_utf8(json.dumps(res.json()['spData'], ensure_ascii=False, sort_keys=True))
    asset_json = json.loads(asset_json)

    return asset_json
    
def get_manual_ticker(pc, sourceAssetId, userAccountId):
    asset = get_asset_classification(pc, sourceAssetId, userAccountId)
    
    try:
        item = asset['portfolioComponents'][0]
        to_return = { 
            "symbol": item['symbol'],
            "description": item['symbol'],
            "sourceAssetId": sourceAssetId,
            "percentage": item['percentage']
        }
        return to_return
    except Exception:
        to_return = {
            "symbol": "CASH",
            "description": sourceAssetId,
            "sourceAssetId": sourceAssetId,
            "percentage": 100.00
        }
        return to_return
    
def set_missing_ticker(pc, holding):
    sourceAssetId = holding['sourceAssetId']
    userAccountId = holding['userAccountId']
    modified_holding = holding
    info = get_manual_ticker(pc, sourceAssetId, userAccountId)
    modified_holding['ticker']=info['symbol']
    return modified_holding
    
def set_account_type_for_holding(pc, accounts, holding):
    modified_holding = holding
    try:
        acc = holding['accountName']
    except Exception:
        modified_holding['accountType']=""
        return modified_holding
    acc = get_account_from_accounts(accounts, acc)
    info = get_clean_account_type_from_account(acc)
    modified_holding['accountType']=info
    return modified_holding
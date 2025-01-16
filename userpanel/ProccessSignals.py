import json
import re
from datetime import datetime

def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str.strip(), "%Y/%m/%d  |  %H:%M")
    except ValueError:
        return None

def process_signals(data):

    currency_pattern = r"[\s🟢🔴]*(\w+)(?:/)?\s+usdt|Spot"
    trade_type_pattern = r"(long|sell|short|spot)"
    entry_pattern = r"Entry\s*[:;]\s*([\d.]+)"
    tp_pattern = r"Tp\s*([\d.\s]+)"
    sl_pattern = r"Sl\s*[:;]\s*([\d.]+|Hold)"
    margin_pattern = r"Margin\s*[:;]\s*([\d%]+)"
    leverage_pattern = r"Leverage\s*[:;]?\s*([\dX\s]+)"
    status_patterns = {
        "profit": r"(سیگنال.*سود|TP|Profit|رسید)",
        "partial_profit": r"(سیو سود|Secure Profit)",
        "cancel": r"(کنسل|لغو|ببندید)",
        "sl": r"(SL|استاپ خورده)"
    }

  
    signal_status = {} 

    for message in data:
        text = message['text']
        related_message = message.get('relatedMessage')
        

        if related_message:
            related_id = related_message['id']
            if re.search(status_patterns["sl"], text, re.IGNORECASE):
                signal_status[related_id] = "SL"
            elif re.search(status_patterns["profit"], text, re.IGNORECASE):
                signal_status[related_id] = "Profit"
            elif re.search(status_patterns["partial_profit"], text, re.IGNORECASE):
                signal_status[related_id] = "Partial Profit"
            elif re.search(status_patterns["cancel"], text, re.IGNORECASE):
                signal_status[related_id] = "Cancel"
            
      
            if "لغو" in text or "کنسل" in text:
                signal_status[related_id] = "Disabled"
            continue


    results = []
    for message in data:
        text = message['text']
        send_time = parse_date(message['sendTime'])
        related_message = message.get('relatedMessage')
        
      
        if related_message:
            continue
        
        result = {
            'id': message['id'],
            'text': text,
            'send_time': send_time.isoformat() if send_time else "N/A"
        }
 
        currency_match = re.search(currency_pattern, text, re.IGNORECASE)
        result['currency'] = currency_match.group(1) if currency_match else "N/A"

        trade_type_match = re.search(trade_type_pattern, text, re.IGNORECASE)
        result['trade_type'] = trade_type_match.group(1).capitalize() if trade_type_match else "N/A"
        
     
        entry_match = re.search(entry_pattern, text, re.IGNORECASE)
        result['entry'] = float(entry_match.group(1)) if entry_match else None
    
        tp_match = re.search(tp_pattern, text, re.IGNORECASE)
        result['take_profits'] = [float(tp.strip()) for tp in tp_match.group(1).split()] if tp_match else []

        sl_match = re.search(sl_pattern, text, re.IGNORECASE)
        result['stop_loss'] = float(sl_match.group(1)) if sl_match and sl_match.group(1) != "Hold" else "Hold"
        

        margin_match = re.search(margin_pattern, text, re.IGNORECASE)
        result['margin'] = margin_match.group(1) if margin_match else "N/A"
    
        leverage_match = re.search(leverage_pattern, text, re.IGNORECASE)
        result['leverage'] = leverage_match.group(1).strip() if leverage_match else "N/A"
        
  
        result['status'] = signal_status.get(message['id'], "Active")
        

        if not result['currency'] or result['currency'] == "N/A":
            continue

        results.append(result)

    return results



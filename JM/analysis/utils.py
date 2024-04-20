import pandas as pd
import re

def load_log(log_file):
    timestamp_pattern = r"\"timestamp\": \d+"
    observation_pattern = r'\[\d+.?\d,\d+.?\d+,\d+?.\d+,\d+.?\d,-\d+.?\d+,\d+.?\d+,\d+.?\d+]'
    observation = pd.DataFrame(columns=['timestamp', 'ASK', 'BID', 'TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY'])

    with open(log_file, 'r') as f:
        lines = f.readlines()
    
        sandbox_start = 1
        sandbox_end = 2
        while not lines[sandbox_end] == '\n':
            if lines[sandbox_end].startswith('{'):
                sandbox_start = sandbox_end
                while not lines[sandbox_end].startswith('}'):
                    sandbox_end += 1
                entry = ''.join(lines[sandbox_start:sandbox_end+1])
                time = re.findall(timestamp_pattern, entry)
                text = re.findall(observation_pattern, entry)
                if len(time) == 1 and len(text) == 1:
                    time = int(time[0].split(' ')[1])
                    text = text[0][1:-1].split(',')
                    observation.loc[len(observation)] = [time] + [float(x) for x in text]
            sandbox_end += 1
        
        activity_start = 1
        while not lines[activity_start].startswith('Activities log:'):
            activity_start += 1
        activity_start += 1
        activity_end = activity_start + 1
        while lines[activity_end] != '\n':
            activity_end += 1

        trade_start = activity_end + 1
        while not lines[trade_start].startswith('Trade History:'):
            trade_start += 1
        trade_start += 1
        trade_end = len(lines)
        trade_history = ''.join(lines[trade_start:trade_end])

    activity_log = pd.read_csv(log_file, skiprows=activity_start, nrows=activity_end-activity_start-1, sep=';').set_index(['product','day','timestamp'])
    trade_history = pd.read_json(trade_history)
    observation['ORCHIDS'] = (observation['ASK'] + observation['BID'])/2

    return activity_log, trade_history, observation
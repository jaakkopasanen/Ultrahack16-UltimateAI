import numpy as np
import dateutil.parser

def get_transaction_weekday(transaction):
    date_string = transaction['details']['posted']
    return dateutil.parser.parse(date_string).weekday()

def get_transaction_month(transaction):
    date_string = transaction['details']['posted']
    return dateutil.parser.parse(date_string).month

def get_transaction_hour(transaction):
    date_string = transaction['details']['posted']
    return dateutil.parser.parse(date_string).hour

def get_transaction_balance(transaction):
    return transaction['details']['new_balance']['amount']

def get_is_transaction_weekend(transaction):
    day_of_week = get_transaction_weekday(transaction)
    return day_of_week > 4



def create_cluster_features(transactions):

    """
    Compute cluster features
    amount mean, amount std, hour average, hour std, month average,
    month std, day average, day std, percentage of weekdays,
    percentage of weekends
    """

    feats = []
    # amount statistics
    values = np.array([float(t['details']['value']['amount']) for t in transactions])
    mean = values.mean()
    std = values.std()
    feats.append(mean)
    feats.append(std)

    # hour statistics
    hour_data = np.array([get_transaction_hour(t) for t in transactions])
    hour_average = hour_data.mean()
    hour_std = hour_data.std()
    feats.append(hour_average)
    feats.append(hour_std)

    # month statistics
    month_data = np.array([get_transaction_month(t) for t in transactions])
    month_average = month_data.mean()
    month_std = month_data.std()
    feats.append(month_average)
    feats.append(month_std)

    # day statistics
    day_data = np.array([get_transaction_weekday(t) for t in transactions])
    day_average = day_data.mean()
    day_std = day_data.std()
    feats.append(day_average)
    feats.append(day_std)

    # percentage of weekdays and weekend days
    weekends = day_data > 4
    weekdays = day_data <= 4
    weekends_ratio = weekends.sum() / weekends.shape[0]
    weekdays_ratio = weekdays.sum() / weekdays.shape[0]
    feats.append(weekdays_ratio)
    feats.append(weekends_ratio)

    # new balances
    new_balances = np.array([float(t['details']['new_balance']['amount']) for t in transactions])
    new_balances_mean = new_balances.mean()
    new_balances_std = new_balances.std()
    feats.append(new_balances_mean)
    feats.append(new_balances_std)

    # relative amounts
    relative_amounts = values / new_balances
    relative_amounts_average = relative_amounts.mean()
    relative_amounts_std = relative_amounts.std()
    feats.append(relative_amounts_average)
    feats.append(relative_amounts_std)

    return np.array(feats)

if __name__ == '__main__':
    from pprint import pprint
    from ObpApi.api_credentials import *
    from ObpApi.ObpApi import ObpApi
    from test_users import TEST_USERS

    user = TEST_USERS[10]
    obp_api = ObpApi(
        host='https://op.openbankproject.com',
        version='2.1.0',
        direct_login_url='/my/logins/direct',
        oauth_url='/oauth',
        oauth_callback_url='http://localhost',
        consumer_key=OBP_CONSUMER_KEY,
        consumer_secret=OBP_CONSUMER_SECRET
    )
    login_success = obp_api.login_direct(user['username'], user['password'])
    # login_success = obp_api.initiate_oauth()
    # obp_api.hello()
    accounts = obp_api.get_all_private_accounts()
    # for acc in accounts:
    #     account = obp_api.get_account(acc['bank_id'], acc['id'], 'owner')
    #     print('{currency} {amount} @ {iban}'.format(
    #         currency=account['balance']['currency'],
    #         amount=account['balance']['amount'],
    #         iban=account['IBAN'])
    #     )
    #
    transactions = obp_api.get_transactions(accounts[0]['bank_id'],
                                            accounts[0]['id'], view='owner')
    print(transactions)
    feats = create_cluster_features(transactions)
    print(feats)

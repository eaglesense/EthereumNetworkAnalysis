from web3 import Web3
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.notebook import trange
import time
import operator

def update_dict(dictionary, str_value):
	if str_value in dictionary:
		dictionary[str_value] = dictionary.get(str_value) + 1
	else:
		dictionary[str_value] = 1

def print_transaction_statistics(dictionary, time_unit):
	df = pd.DataFrame(dictionary.items(), columns = [time_unit, 'Transactions'])
	print(df.to_string(index=False))
	print("--------------------")

def get_key_with_max_value_from_dict(dictionary):
	# TODO return multiple values if multiple keys have the same maximum value
	return max(dictionary.items(), key=operator.itemgetter(1))[0]

def convert_numeric_to_gregorian(dictionary, time_unit):
	if time_unit is 'Day':
		numeric = ['0', '1', '2', '3', '4', '5', '6']
		gregorian = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
		convert_dict_keys(dictionary, numeric, gregorian)
	elif time_unit is 'Month':
		numeric = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
		gregorian = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		convert_dict_keys(dictionary, numeric, gregorian)
	else:
		raise Exception("Invalid value of time_unit " + str(time_unit) + "!")

def convert_dict_keys(dictionary, current_arr, target_arr):
	if len(current_arr) == len(target_arr):
		for i in range(len(target_arr)):
			if current_arr[i] in dictionary:
				dictionary[target_arr[i]] = dictionary[current_arr[i]]
				del dictionary[current_arr[i]]
	else:
		raise Exception("Given arrays have different length!")

def plot_dict_as_bar_chart(dictionary):
	keys = list(dictionary.keys())
	values = list(dictionary.values())
	plt.bar(range(len(dictionary)), list(values), tick_label=keys)
	plt.title("Transaction Overview")
	plt.xlabel("Time Window")
	plt.ylabel("Number of Transactions")
	plt.show()

def main():
	# connect to blockchain
	blockchain_address = 'wss://websockets.bloxberg.org'
	print("Connecting to " + str(blockchain_address) + " ...")
	w3 = Web3(Web3.WebsocketProvider(blockchain_address))
	if w3.isConnected():
		print("Successfully connected to " + str(blockchain_address))

		# obtain transactions
		start_block = 2000000
		end_block = 2000500

		transactions = []
		for block_id in trange(start_block, end_block):
		    block = w3.eth.getBlock(block_id, full_transactions=True)
		    for transaction_index in block.transactions:
		        transactions.append([block.timestamp, block_id, transaction_index['to'], transaction_index['from']])

		# determine times of transactions
		years_dict = {}
		months_dict = {}
		days_dict = {}
		hours_dict = {}
		time_dict = {}

		for i in range(len(transactions)):
			result = time.localtime(transactions[i][0])
			update_dict(years_dict, str(result.tm_year))
			update_dict(months_dict, str(result.tm_mon))
			update_dict(days_dict, str(result.tm_wday))
			update_dict(hours_dict, str(result.tm_hour))
			update_dict(time_dict, str(result.tm_hour) + ":" + str(result.tm_min))

		convert_numeric_to_gregorian(days_dict, 'Day')
		convert_numeric_to_gregorian(months_dict, 'Month')

		# print statistics
		print("Printing statistic of " + str(len(transactions)) + " transactions (block numbers " + str(start_block) + "-" + str(end_block) + "):\n")

		print_transaction_statistics(years_dict, 'Year')
		print_transaction_statistics(months_dict, 'Month')
		print_transaction_statistics(days_dict, 'Day')
		print_transaction_statistics(hours_dict, 'Hour')
		print_transaction_statistics(time_dict, 'Time')

		# print transaction peaks
		year_peak = get_key_with_max_value_from_dict(years_dict)
		month_peak = get_key_with_max_value_from_dict(months_dict)
		day_peak = get_key_with_max_value_from_dict(days_dict)
		hour_peak = get_key_with_max_value_from_dict(hours_dict)
		time_peak = get_key_with_max_value_from_dict(time_dict)

		print("Year with most transactions is " + str(year_peak))
		print("Month with most transactions is " + str(month_peak))
		print("Day with most transactions is " + str(day_peak))
		print("Hour with most transactions is " + str(hour_peak))
		print("Time with most transactions is " + str(time_peak))

		# plot statistics
		plot_dict_as_bar_chart(hours_dict)
	else:
		print("ERROR: Connection to " + str(blockchain_address) + " could not be established!")

if __name__ == '__main__':
	main()

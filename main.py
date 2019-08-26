"""
  Author: Harry L. Sauers
  - A basic script to scrape options pricing from the web. -
"""

from bs4 import BeautifulSoup
import datetime, time
import requests
from apscheduler.schedulers.background import BackgroundScheduler

YAHOO_URL = "https://finance.yahoo.com/quote/SPY/options?date="

def get_datestamp():
  options_url = YAHOO_URL
  today = int(time.time())
  # print(today)
  date = datetime.datetime.fromtimestamp(today)
  yy = date.year
  mm = date.month
  dd = date.day

  dd += 1
  options_day = datetime.date(yy, mm, dd)
  datestamp = int(time.mktime(options_day.timetuple()))
  # print(datestamp)
  # print(datetime.datetime.fromtimestamp(options_stamp))

  # vet timestamp, then return if valid
  for i in range(0, 7):
    test_req = requests.get(options_url + str(datestamp)).content
    content = BeautifulSoup(test_req, "html.parser")
    # print(content)
    tables = content.find_all("table")
    if tables != []:
      # print(datestamp)
      return str(datestamp)
    else:
      # print("Bad datestamp!")
      dd += 1
      options_day = datetime.date(yy, mm, dd)
      datestamp = int(time.mktime(options_day.timetuple()))
 
  return str(-1)


def fetch_options():
  # print("Hello World!")
  data_url = YAHOO_URL + get_datestamp()
  data_html = requests.get(data_url).content
  # print(data_html)
  content = BeautifulSoup(data_html, "html.parser")
  # print(content)

  options_tables = []
  tables = content.find_all("table")
  for i in range(0, len(content.find_all("table"))):
    options_tables.append(BeautifulSoup(str(tables[i]), "html.parser"))

  calls = options_tables[0].find_all("tr")[1:]  # first row is header

  itm_calls = []
  otm_calls = []

  for call_option in calls:
    if "in-the-money" in str(call_option):
      itm_calls.append(call_option)
    else:
      otm_calls.append(call_option)

  itm_call = itm_calls[-1]
  otm_call = otm_calls[0]

  # print(str(itm_call) + " \n\n " + str(otm_call) + "\n\n")

  itm_call_data = []
  for td in BeautifulSoup(str(itm_call), "html.parser").find_all("td"):
    itm_call_data.append(td.text)

  # print(itm_call_data)

  itm_call_info = {'contract': itm_call_data[0], 'last_trade': itm_call_data[1][:10],
                    'strike': itm_call_data[2], 'last': itm_call_data[3], 
                    'bid': itm_call_data[4], 'ask': itm_call_data[5], 'volume': itm_call_data[8], 'iv': itm_call_data[10]}

  # print(itm_call_info)

  # otm call
  otm_call_data = []
  for td in BeautifulSoup(str(otm_call), "html.parser").find_all("td"):
    otm_call_data.append(td.text)

  # print(otm_call_data)

  otm_call_info = {'contract': otm_call_data[0], 'last_trade': otm_call_data[1][:10],
                    'strike': otm_call_data[2], 'last': otm_call_data[3], 
                    'bid': otm_call_data[4], 'ask': otm_call_data[5], 'volume': otm_call_data[8], 'iv': otm_call_data[10]}

  # print(otm_call_info)

  # put options data

  puts = options_tables[1].find_all("tr")[1:]  # first row is header

  itm_puts = []
  otm_puts = []

  for put_option in puts:
    if "in-the-money" in str(put_option):
      itm_puts.append(put_option)
    else:
      otm_puts.append(put_option)

  itm_put = itm_puts[0]
  otm_put = otm_puts[-1]

  # print(str(itm_put) + " \n\n " + str(otm_put) + "\n\n")

  itm_put_data = []
  for td in BeautifulSoup(str(itm_put), "html.parser").find_all("td"):
    itm_put_data.append(td.text)

  # print(itm_put_data)

  itm_put_info = {'contract': itm_put_data[0], 'last_trade': itm_put_data[1][:10],
                    'strike': itm_put_data[2], 'last': itm_put_data[3], 
                    'bid': itm_put_data[4], 'ask': itm_put_data[5], 'volume': itm_put_data[8], 'iv': itm_put_data[10]}

  # print(itm_put_info)

  # otm put
  otm_put_data = []
  for td in BeautifulSoup(str(otm_put), "html.parser").find_all("td"):
    otm_put_data.append(td.text)

  # print(otm_put_data)

  otm_put_info = {'contract': otm_put_data[0], 'last_trade': otm_put_data[1][:10],
                    'strike': otm_put_data[2], 'last': otm_put_data[3], 
                    'bid': otm_put_data[4], 'ask': otm_put_data[5], 'volume': otm_put_data[8], 'iv': otm_put_data[10]}

  # print(itm_call_info)
  # print(otm_call_info)
  # print(itm_put_info)
  # print(otm_put_info)
  # print(len(options_tables))

  options_list = {'calls': {'itm': itm_call_info, 'otm': otm_call_info}, 'puts': {'itm': itm_put_info, 'otm': otm_put_info}, 'date': datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d")}

  # print(options_list)

  return options_list


def write_to_csv(options_data):
  import csv
  with open('options.csv', 'a', newline='\n') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow([str(options_data)])


def run():
  today = int(time.time())
  date = datetime.datetime.fromtimestamp(today)
  yy = date.year
  mm = date.month
  dd = date.day

  # must use 12:30 for Unix time instead of 4:30 NY time
  next_close = datetime.datetime(yy, mm, dd, 12, 30)

  # if program was run after market hours
  if next_close < datetime.datetime.now():
    dd += 1
    next_close = datetime.datetime(yy, mm, dd, 12, 30)

  # do operations here
  """ This is where we'll write our last bit of code. """
  options = {}

  # ensures option data doesn't break the program if internet is out
  try:
    options = fetch_options()
  except:
    print("Check your connection and try again.")
  
  # if no options are returned - market must be closed. 
  if options == {}:
    print("Market is closed... Rescheduling in 24 hours.")
  else:
    # write to file
    write_to_csv(options)

  # schedule next job
  scheduler.add_job(func=run, trigger="date", run_date = next_close)

  print("Job scheduled! | " + str(next_close))


scheduler = BackgroundScheduler()


def schedule():
  scheduler.add_job(func=run, trigger="date", run_date = datetime.datetime.now())
  scheduler.start()


if __name__ == "__main__":
  # schedule()
  run()

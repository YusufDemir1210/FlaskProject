import flask
import json
import math

# taking data from JSON files
usersFile = open('users.json', 'r')
simulationsFile = open('simulations.json', 'r')

usersData = json.load(usersFile)
simulationsData = json.load(simulationsFile)


def calculateDate(datetime):
    # min datetime in this data is 45231
    if datetime < 45247: # 45247 is 1 December 2023
        return str(datetime - 45216) + " November 2023"
    if datetime < 45278: # 45278 is 1 January 2024
        return str(datetime - 45246) + " December 2023"
    return str(datetime - 45277) + " January 2024"


# storing the data in dictionaries to use later on
companySimDict = dict()
companyNames = dict()
for simulation in simulationsData['simulations']:
    sim_id = simulation['simulation_id']
    companyId = simulation['company_id']
    companySimDict[sim_id] = companyId
    if companyId not in companyNames.keys():
        companyNames[companyId] = simulation['company_name']


companyUserDict = dict()
userCounts = dict()
userStartingDateDict = dict()
for user in usersData['users']:
    user_id = user['user_id']

    simulation_id = user['simulation_id']
    companyId = companySimDict[simulation_id]
    companyName = companyNames[companyId]
    userCounts[companyName] = userCounts.get(companyName, 0) + 1

    userSet = companyUserDict.get(companyId, set())
    userSet.add(user_id)
    companyUserDict[companyId] = userSet

    userStartingDateDict[user_id] = math.floor(user['signup_datetime'])


companyDailyUserDict = dict()
for companyId in companySimDict.values():
    tempDict = dict()
    for day in range(45231, 45292):  # 45231 is min and 45921 is max
        dailyUserCount = 0
        for userId in companyUserDict[companyId]:
            if userStartingDateDict[userId] <= day: dailyUserCount += 1
        tempDict[calculateDate(day)] = dailyUserCount
    companyDailyUserDict[companyId] = tempDict

import matplotlib.pyplot as plt

plt.figure(figsize=(20, 12))
for companyId in companyNames.keys():
    dailyUserCounts = list(companyDailyUserDict[companyId].values())
    dates = list(companyDailyUserDict[companyId].keys())
    companyName = companyNames[companyId]
    plt.plot(dates, dailyUserCounts, label = companyName)

plt.xlabel('Date')
plt.ylabel('Number of Users')
plt.title('Daily Number of Users for Each Company')
plt.xticks(rotation=270)
plt.legend()
plt.tight_layout()

plot_dir = "static/daily_user_counts.png"
plt.savefig(plot_dir)
plt.close()



# creating the web app
app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('table_plot.html', companies=userCounts, plot_dir=plot_dir)

if __name__ == '__main__':
    app.run(debug=True)
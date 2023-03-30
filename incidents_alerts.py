### DEVELOPED BY PAGERDUTY PROFESSIONAL SERVICES/SUCCESS ON DEMAND
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
### IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
### FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
### AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
### LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
### OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
### THE SOFTWARE.

### This code gets all  & alerts for every incident

from pdpyras import APISession
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import *

API_ACCESS_KEY = 'YOUR API KEY HERE'
days_to_get = 2  # Days of data you want to get


session = APISession(API_ACCESS_KEY)
list_incidents = pd.DataFrame()
list_alerts = pd.DataFrame()
offset = 0

today = datetime.today()
start_date = today - relativedelta(days=int(days_to_get - 1))
# declare the days that you want to go back asking for incidents

for x in range(days_to_get):
    offset = 0
    start = start_date + relativedelta(days=int(x))
    end = start_date + relativedelta(days=int(x + 1))

    response = session.get(
        "/incidents?since=" + str(start)[0:10] + "&until=" + str(end)[0:10] + "&limit=100&total=true&offset=" + str(
            offset))
    dataframe_incidents = pd.json_normalize(response.json()["incidents"], max_level=None)
    list_incidents = pd.concat([list_incidents, dataframe_incidents], ignore_index=True, axis=0)

    # this is going to fill the list_incidents dataframe with pagination

    while response.json()["more"] and offset < 9900:  # more than 10.000 record would fail
        limit = response.json()["limit"]
        offset = offset + int(limit)
        response = session.get("/incidents?since=" + str(start)[0:10] + "&until=" + str(end)[0:10] + "&limit=100&total=true&offset=" + str(offset))
        dataframe_incidents = pd.json_normalize(response.json()["incidents"], max_level=None)
        list_incidents = pd.concat([list_incidents, dataframe_incidents], ignore_index=True, axis=0)
print(len(list_incidents))

offset = 0
for s in range(len(list_incidents)):
    response = session.get("/incidents/" + str(list_incidents.id[s]) + "/alerts?limit=100&offset=" + str(offset))
    dataframe_alerts = pd.json_normalize(response.json()["alerts"], max_level=None)
    dataframe_alerts["IncidentID"] = list_incidents.id[s]
    list_alerts = pd.concat([list_alerts, dataframe_alerts], ignore_index=True, axis=0)
    print(list_alerts)

    while response.json()["more"] and offset < 9900:  # more than 10.000 record would fail
        limit = response.json()["limit"]
        offset = offset + int(limit)
        response = session.get("/incidents/" + str(list_incidents.id[s]) + "/alerts?limit=100&offset=" + str(offset))
        dataframe_alerts = pd.json_normalize(response.json()["alerts"], max_level=None)
        dataframe_alerts["IncidentID"] = list_incidents.id[s]
        list_alerts = pd.concat([list_alerts, dataframe_alerts], ignore_index=True, axis=0)


print(list_incidents)
print(list_alerts)

df1 = list_alerts
df1.to_csv('alerts.csv')

df1 = list_incidents
df1.to_csv('incidents.csv')

today2 = datetime.today()
execution_time = today2 - today
print(execution_time)

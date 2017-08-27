import sqlite3
import datetime
import jenkins
#import request

conn = sqlite3.connect('jenkinsjob.db')


def connectToJenkinsURL():

    # Connect to Jenkins instance
    url = 'http://localhost:8080'
    username = 'ENTER_YOUR_USER_NAME'
    password = 'ENTER_YOUR_PASSWORD'
    server = jenkins.Jenkins(url, username=username, password=password)
    return server


def setupDB():
    #conn = sqlite3.connect('jenkinsjob.db')
    cursor = conn.cursor()
    # Create the JenkinsJobs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS jenkins_jobs_list
                (job_id INTEGER, job_name TEXT, checked_time DateTime, 
                status TEXT, building TEXT, duration TEXT)''')
    conn.commit
    conn.close


class Jobs(object):

    server = connectToJenkinsURL()

    authenticated = False
    try:
        server.get_whoami()
        authenticated = True
    except jenkins.JenkinsException as e:
        print('An error occured while authenticating user')
        authenticated = False

    if authenticated:
        setupDB()

        # Get List of all available jobs
        joblist = server.get_all_jobs()
        jid = 0
        for x in joblist:
            jobName = x['name']
            print('The job name: ' + jobName)
            #lastJobID = getLastJobID(jobName)
            lastJobID = None
            lastBuildNumber = server.get_job_info(jobName)['lastBuild']['number']
            if lastJobID is None:
                start = 0
            else:
                start = lastJobID

            # Save the list to databse
            try:
                with conn:
                    curs = conn.cursor()
                    curJob = server.get_build_info(jobName, 1)
                    checked_time = datetime.datetime.fromtimestamp(curJob['timestamp'] * 0.001)
                    curs.execute('INSERT INTO jenkins_jobs_list VALUES (?,?,?,?,?,?)', (curJob['id'], jobName, checked_time, curJob['result'], curJob['building'], curJob['duration']))
            except sqlite3.Error as sqlError:
                print("An error occured while inserting data "+str(sqlError))
            print('The last build ' + str(lastBuildNumber))

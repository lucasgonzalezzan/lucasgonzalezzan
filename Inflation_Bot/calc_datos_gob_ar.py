import apidata

def cumulative_months(months):  
    w = 1  # start with 100%
    for i in range(months): # from last month backwards multiply the increase in inflation
        w = (float(apidata.ipc[init-i][1]) + 1) * w     # each month is a list with [0] = date, [1] IPC increase
    return (w - 1) * 100    #return as %

def average_months(months):
    w = 1
    for i in range(months):
        w = (float(apidata.ipc[init-i][1]) + 1) * w     
    return (pow(w , 1/months) - 1) * 100     #root of the inflation in the amount of months, return as %

def project_months(months, IPC = 1):  #IPC defaul 1%
    w = (IPC / 100) + 1  #from %
    return (pow(w , months) - 1) * 100    #power of inflation rate in the amount of months, return as %

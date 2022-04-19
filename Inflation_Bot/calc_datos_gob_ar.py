import apidata

def cumulative_meses(meses, init = -1):   #Init: default start from last item in list
    w = 1
    for i in range(meses):
        w = (float(apidata.ipc[init-i][1]) + 1) * w     #[0] = date, [1] IPC
    return (w - 1) * 100    #return as %

def promedio_meses(meses, init = -1):
    w = 1
    for i in range(meses):
        w = (float(apidata.ipc[init-i][1]) + 1) * w     
    return (pow(w , 1/meses) - 1) * 100     #root of the inflation in the amount of months, return as %

def project_meses(meses, IPC = 1):  #IPC defaul 1%
    w = (IPC / 100) + 1  #from %
    return (pow(w , meses) - 1) * 100    #return as %

import os
import sys
import matplotlib.pyplot as plt

def runMN1(n, loss):
    os.system(f'cp {sys.argv[1]} {n}_{sys.argv[1]}')
    os.system(f'sudo python3 execute_mn.py 40 {n}_{sys.argv[1]} {n}_{sys.argv[2]} {loss}')
    logFile = open(f'{n}_{sys.argv[1]}_sending_log.txt', 'rb')
    logFile.seek(-60, 2)
    logFile.readline()
    goodput = logFile.readline().decode().split(' ')[2]
    rtt = logFile.readline().decode().split(' ')[3]
    logFile.close()
    os.system(f'sudo rm {n}_{sys.argv[1]}*;sudo rm {n}_{sys.argv[2]}*')
    return float(goodput), float(rtt)

def runMN2(n, wsize):
    os.system(f'cp {sys.argv[1]} {n}_{sys.argv[1]}')
    os.system(f'sudo python3 execute_mn.py {wsize} {n}_{sys.argv[1]} {n}_{sys.argv[2]} 1')
    logFile = open(f'{n}_{sys.argv[1]}_sending_log.txt', 'rb')
    logFile.seek(-60, 2)
    logFile.readline()
    goodput = logFile.readline().decode().split(' ')[2]
    rtt = logFile.readline().decode().split(' ')[3]
    logFile.close()
    os.system(f'sudo rm {n}_{sys.argv[1]}*;sudo rm {n}_{sys.argv[2]}*')
    return float(goodput), float(rtt)

def plot(xAxis, xName, fName, resRtt, resGp):
    plt.figure(figsize=(12, 6), dpi=100)

    ax = plt.subplot(121, xlabel=xName, ylabel='avg RTT')
    ax.bar(range(4), resRtt, width=0.2, color='r', align='center')
    ax.set_xticks(range(4))
    ax.set_xticklabels(xAxis)
    for i, v in enumerate(resRtt):
        plt.text(i, v*1.03, f'{v:.2f}', color='r', fontweight='bold')

    bx = plt.subplot(122, xlabel=xName, ylabel='Goodput')
    bx.bar(range(4), resGp, width=0.2, color='b', align='center')
    bx.set_xticks(range(4))
    bx.set_xticklabels(xAxis)
    for i, v in enumerate(resGp):
        plt.text(i, v*1.03, f'{v:.2f}', color='b', fontweight='bold')

    plt.savefig(os.path.join(fName), dpi=100, format='png', bbox_inches='tight')
    

if __name__ == '__main__':
    #plotting 1
    loss = ['1', '2', '4', '8']
    resRtt = [0., 0., 0., 0.]
    resGp = [0., 0., 0., 0.]
    
    if sys.argv[3] == '0' or sys.argv[3] == '2':
        for i in range(4):
            success = 0
            for j in range(10):
                try:
                    print(f'trial {j} with loss {loss[i]}%')
                    goodput, rtt = runMN1(j, loss[i])
                except (ValueError,IndexError) as e:
                    os.system(f'sudo rm {j}_{sys.argv[1]}*;sudo rm {j}_{sys.argv[2]}*')
                    continue
                success += 1
                resRtt[i] += rtt
                resGp[i] += goodput

            if success == 0 :
                success = 1
            resRtt[i] /= success
            resGp[i] /= success
    
        print('now plotting the first results')
        plot(loss, 'loss', 'loss.png', resRtt, resGp)

    #plotting 2
    if sys.argv[3] == '1' or sys.argv[3] == '2':
        wsize = ['8', '16', '32', '64']
        resRtt = [0., 0., 0., 0.]
        resGp = [0., 0., 0., 0.]

        for i in range(4):
            success = 0
            for j in range(10):
                try:
                    print(f'trial {j} with wsize {wsize[i]}')
                    goodput, rtt = runMN2(j, wsize[i])
                except (ValueError,IndexError) as e:
                    os.system(f'sudo rm {j}_{sys.argv[1]}*;sudo rm {j}_{sys.argv[2]}*')
                    continue
                success += 1
                resRtt[i] += rtt
                resGp[i] += goodput

            if success == 0 :
                success = 1
            resRtt[i] /= success
            resGp[i] /= success
        
        print('now plotting the first results')
        plot(wsize, 'window size', 'window_size.png', resRtt, resGp)
    

        
import sys
import json
import requests
from multiprocessing import Process
import multiprocessing
import argparse

parser = argparse.ArgumentParse()
parser.add_argument("--sentence", type=list)
args = parser.parse_args()


def get_scan_result(ip_addr, sentence, result):
    r = requests.post("http://%s:4444/getString" %(ip_addr), data={'String': sentence})
    scan_result = json.loads(r.text)
    result[ip_addr] = scan_result
    # resultDict = []
    # for elements in scan_result:
    #    tmp = {}
    #    tmp['scanId'] = elements
    #    resultDict.append(tmp)
    # print("result dict is")
    # print(resultDict)
    # return scan_result, resultDict

if __name__ == '__main__':
    IP_ADDR = ['localhost', '143.248.49.202', '143.248.49.197', '143.248.49.64']
    procs = []
    manager = multiprocessing.Manager()
    result = manaer.dict()

    input_sentence = "".join(args.sentence)

    for _ip in IP_ADDR:
        proc = Process(target=get_scan_result, args=(_ip, input_sentence, result))
        proces.append(proc)
        proc.start()

    for p in procs:
        p.join()

    final = []
    for _ip in IP_ADDR:
        final += result(_ip)

    with open('/home/ivy/IVIST_server/flask-backend/result_idx.txt', 'w') as text:
        for scanID in final:
            text.write(str(scanID)+'\n')



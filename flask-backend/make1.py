import csv
import time



with open('./real_fianl.tsv', 'w') as real:
    real_writer = csv.writer(real, delimiter='\t')
    real_writer.writerow(['image_id', 'real_id', '_id'])

    with open('./final_scan_dic.tsv', 'r') as tsv:
        tsv_reader = csv.reader(tsv)
        for line in tsv_reader:
            start = time.time()
            if line[0].split('\t')[0] != 'image_id':
                print "##########    Processing ", line[0], "   ##########"
                scanID = line[0].split('\t')[0]
                vid_key = line[0].split('\t')[1]
                video_num = str(vid_key.split('_')[0])
                keyframe = int(vid_key.split('_')[1])

                with open('/mnt/hard2/dataset/video_data/tsv/%s.tsv' %(video_num), 'r') as ref:
                    ref_reader = csv.reader(ref)
                    i = 0
                    for li in ref_reader:
                        if i == keyframe:
                            real_writer.writerow([scanID, vid_key, video_num+'_'+str(li[0].split('\t')[0])+'-'+str(li[0].split('\t')[2])])

                        i += 1
            print "Time per line : ", time.time() - start




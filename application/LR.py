from pathlib import Path
import sys
import pandas as pd
from pba import Interval, sometimes, always, Pbox, KN
from engine import *

sys.path.append(Path(__file__))

questionnaire_txt = pd.read_csv('default_questionnaire_v2.csv')
raw_cm = pd.read_csv('mackie_confusion_matrix2.csv')

# Clean CM 
unique_tests = np.unique(raw_cm['Test'])
out = []
for t in unique_tests:
    idX = raw_cm.loc[:, 'Test'] == t
    data = raw_cm.loc[idX, ['tp', 'fp', 'fn', 'tn']]
    tp = sum(data['tp'])
    fp = sum(data['fp'])
    fn = sum(data['fn'])
    tn = sum(data['tn'])
    out.append(np.array([raw_cm.loc[np.where(idX)[0][0], 'HALOQid'], tp, fp, fn, tn]))
    
clean_cm = pd.DataFrame(np.concatenate([out]), columns = ['Qid','tp', 'fp', 'fn', 'tn'], index = unique_tests)
    
Imprecise_LR = {}
for i in clean_cm.index:
    idq = clean_cm.loc[i, 'Qid']
    Imprecise_LR[idq] = {}
    Imprecise_LR[idq]['question_text'] = i
    Imprecise_LR[idq]['Sensitivity'] = KN(clean_cm.loc[i,'tp'], (clean_cm.loc[i,'tp'] + clean_cm.loc[i,'fn']))  # clean_cm.loc[i, 'Qid']
    Imprecise_LR[idq]['Specificity'] = KN(clean_cm.loc[i,'tn'], (clean_cm.loc[i,'tn'] + clean_cm.loc[i,'fp']))  # clean_cm.loc[i, 'Qid']
    Imprecise_LR[idq]['posLR'] = calcPosLR(Imprecise_LR[idq]['Sensitivity'], Imprecise_LR[idq]['Specificity'])
    Imprecise_LR[idq]['negLR']= calcNegLR(Imprecise_LR[idq]['Sensitivity'], Imprecise_LR[idq]['Specificity'])


# Plot c-boxes
for i in list(Imprecise_LR.keys()):
    fig, ax = plt.subplots(nrows=2, ncols=2, sharey = True, figsize=(5,6))
    fig.suptitle(Imprecise_LR[i]['question_text'], fontsize=16)
    ax[0, 0].plot(Imprecise_LR[i]['Sensitivity'].left, np.linspace(0,1,200) )
    ax[0, 0].set_xlabel('Sensitivity')
    ax[0, 0].plot(Imprecise_LR[i]['Sensitivity'].right, np.linspace(0,1,200) )
    ax[0, 1].plot(Imprecise_LR[i]['Specificity'].left, np.linspace(0,1,200) )
    ax[0, 1].set_xlabel('Specificity')
    ax[0, 1].plot(Imprecise_LR[i]['Specificity'].right, np.linspace(0,1,200) )
    ax[0, 0].set_ylabel('Confidence')
    ax[1, 0].plot(Imprecise_LR[i]['posLR'].left, np.linspace(0, 1, 200) )
    ax[1, 0].plot(Imprecise_LR[i]['posLR'].right, np.linspace(0, 1, 200) )
    PLR = questionnaire_txt.loc[questionnaire_txt['Qid']==i,'PLR']
    ax[1, 0].plot([PLR,PLR],[0,1],c='r')
    ax[1, 0].set_xlabel('+ve LR')
    ax[1, 1].plot(Imprecise_LR[i]['negLR'].left, np.linspace(0, 1, 200) )
    ax[1, 1].plot(Imprecise_LR[i]['negLR'].right, np.linspace(0, 1, 200) )
    NLR = questionnaire_txt.loc[questionnaire_txt['Qid']==i,'NLR']
    ax[1, 1].plot([NLR,NLR],[0,1],c='r')
    ax[1, 1].set_xlabel('-ve LR')
    ax[1, 0].set_ylabel('Confidence')
    fig.layout='tight'
    plt.savefig('/Users/dominiccalleja/GCA_App/GCA_engine/LRfigures/{}.png'.format(i))
    plt.show()


class CBoxLR():

    def __init__(self):

    

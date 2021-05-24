import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlrd

def smooth(series,num):
    interp=[]
    date=[]
    arr=np.array(series)
    ind=series.index
    N=num
    for  i,num in enumerate(arr):
        temp= arr[len(arr)-i-N:len(arr)-1-i]
        mu= temp.mean()
        interp.append(mu)
        if i==0:
            date.append(ind[len(ind)-1])
        else:
            date.append(ind[len(ind)-1-i])
    res = pd.DataFrame({"date":date,"mu":interp})
    return(res)

def getcumulatives(dat_sum):
    res=[]
    for i in range(len(dat_sum)):
        if i ==0:
            res.append(dat_sum["num"][i+1]) 
        else:
            res.append(dat_sum["num"][0:i+1].sum())
        
        
    return(res)

def computeratio(dat_sum,data_vaxx_sum_diff):
    from numpy import inf
    new_vaxxs_ = []
    dat_sum_temp = []
    datum_temp =[]
    for i,date in enumerate(dat_sum.index):
        if i < len(dat_sum.index)-1:
            t=data_vaxx_sum_diff[data_vaxx_sum_diff.index==date].loc[:,"new_vaccinations"][0]
            new_vaxxs_.append(t)
            dat_sum_temp.append(dat_sum["num"][i])
            datum_temp.append(dat_sum.index[i])


    AER = [(dat_sum_temp[i]/new_vaxxs_[i])*100 for i in range(len(new_vaxxs_))]
    for i in range(len(AER)):
        if AER[i] ==inf:
            AER[i]=0
                
    df=pd.DataFrame({"date": datum_temp,"rate":AER})
        
    df=df.set_index("date")
    return(df)


def plotbyvaccine(dat_owid_sums,dat_sum,hosp_dat_sum,death_dat_sum,data_vaxx_sum_diff,string):
    from numpy import inf
    plt.switch_backend("agg")
    dat_sum = dat_sum[dat_sum["Suspect/interacting Drug List (Drug Char - Indication PT - Action taken - [Duration - Dose - Route])"].str.contains(string,na=False)]
    #dat_sum = dat_sum[dat_sum["num"]>0]
    hosp_dat_sum = hosp_dat_sum[hosp_dat_sum["Suspect/interacting Drug List (Drug Char - Indication PT - Action taken - [Duration - Dose - Route])"].str.contains(string,na=False)]
    #hosp_dat_sum = hosp_dat_sum[hosp_dat_sum["num"]>0]
    death_dat_sum = death_dat_sum[death_dat_sum["Suspect/interacting Drug List (Drug Char - Indication PT - Action taken - [Duration - Dose - Route])"].str.contains(string,na=False)]
    #death_dat_sum = death_dat_sum[death_dat_sum["num"]>0]
    #print(dat_sum)
    
    
    box = dict(facecolor='white', pad=5, alpha=0.2) # bos
    labelx = -0.05  # axes coords
    fig, ax = plt.subplots(6, 1,figsize=(16,18),sharex=True, 
                           gridspec_kw={
                               #'width_ratios': [2, 1],
                               'height_ratios': [2,2, 1,1,1,1]})

    fig.suptitle("Impfgeschehen in der European Economic Area (EEA)\n"+"Impfstoff:"+string,fontsize=20)
    #################
    ax[0].set_title("Übersicht pro Tag")
    ax[0].fill_between(dat_sum.index,dat_sum["num"],
                       label="Impfnebenwirkungen",alpha=0.4,color="tab:orange")
    ax[0].fill_between(hosp_dat_sum.index,hosp_dat_sum["num"],
                       label="schwere Nebenwirkungen",alpha=0.4,color="black")
    ax[0].fill_between(death_dat_sum.index,death_dat_sum["num"],
                       label="Impftote",color="red",alpha=0.4)
    ax[0].set_ylabel('Anzahl pro Tag')
    ax[0].yaxis.set_label_coords(labelx, 0.5)
    ax[0].plot(data_vaxx_sum_diff.index[0:len(data_vaxx_sum_diff.index)-3],
               (data_vaxx_sum_diff["new_vaccinations"][0:len(data_vaxx_sum_diff.index)-3]/data_vaxx_sum_diff["new_vaccinations"].max())*dat_sum["num"].max(),#########
               color="tab:purple",label="Impfungen EEA pro Tag")

    # secondary axis conversion factor
    ratio=data_vaxx_sum_diff["new_vaccinations"].max()/dat_sum["num"].max()

    #define function and inverse function
    secax_y = ax[0].secondary_yaxis(
        'right', functions=(lambda x: x*ratio, lambda x: x/ratio))

    secax_y.set_ylabel('Impfungen pro Tag in Mio',color="tab:purple")
    secax_y.tick_params(axis='y', colors='tab:purple')
    ax[0].legend(loc="upper left")
    ####################
    #################### kumulatives


    cumsum = getcumulatives(dat_sum)
    cumsumhosp = getcumulatives(hosp_dat_sum)
    cumsumdeath = getcumulatives(death_dat_sum)

    # sideeffect rates
    vac_total=data_vaxx_sum_diff[data_vaxx_sum_diff.index == dat_sum.index[-2]]["total_vaccinations"]
    total_rate=(cumsum[-1]/vac_total)*100
    hosp_rate=(cumsumhosp[-1]/vac_total)*100
    death_rate=(cumsumdeath[-1]/vac_total)*100
    print("rate:",str(total_rate[0])[0:5])

    ax[1].set_title("Übersicht kumulativ")
    ax[1].set_ylabel("schwere Nebenwirkungen und Tote kumulativ")
    ax[1].yaxis.set_label_coords(labelx, 0.5)

    ax[1].plot(dat_sum.index,(cumsum/max(cumsum))*(max(cumsumhosp)*2),color="tab:blue",label="alle Nebenwirkungen")
    ax[1].scatter(dat_sum.index[-1],[(cumsum/max(cumsum))*(max(cumsumhosp)*2)][0][-1],color="tab:blue",linewidth=3)
    ax[1].text(dat_sum.index[-1],[(cumsum/max(cumsum))*(max(cumsumhosp)*2)][0][-1]-max(cumsumhosp)*0.3,
               str(round(cumsum[-1]))+"\n"+str(total_rate[0])[0:5]+" %",fontweight="bold")

    ax[1].plot(hosp_dat_sum.index,cumsumhosp,color="tab:orange",label="schwere Nebenwirkungen")
    ax[1].scatter(hosp_dat_sum.index[-1],cumsumhosp[-1],color="tab:orange",linewidth=3)
    ax[1].text(hosp_dat_sum.index[-1],cumsumhosp[-1]+max(cumsumhosp)*0.1,
               str(round(cumsumhosp[-1]))+"\n"+str(hosp_rate[0])[0:5]+" %",fontweight="bold")

    ax[1].plot(death_dat_sum.index,cumsumdeath,color="tab:red",label="Impftote")
    ax[1].scatter(death_dat_sum.index[-1],cumsumdeath[-1],color="tab:red",linewidth=3)
    ax[1].text(death_dat_sum.index[-1],cumsumdeath[-1]+max(cumsumhosp)*0.1,
               str(round(cumsumdeath[-1]))+"\n"+str(death_rate[0])[0:5]+" %",
               fontweight="bold")#,va='bottom',ha="center"


    ax[1].legend(loc="upper left")
    # secondary axis conversion factor
    ratio1=((max(cumsum))/(max(cumsumhosp)*2))

    #define function and inverse function
    secax_y1 = ax[1].secondary_yaxis(
        'right', functions=(lambda x: x*ratio1, lambda x: x/ratio1))

    secax_y1.set_ylabel('Alle Nebenwirkungen kumulativ',color="tab:blue")
    secax_y1.tick_params(axis='y', colors='tab:blue')


    ####################
    #new deaths in range of available data (new deaths owid)
    new_deaths = []
    for i,date in enumerate(death_dat_sum.index):
        new_deaths.append(dat_owid_sums[dat_owid_sums.index==str(date)[0:10]].loc[:,"new_deaths_smoothed"][0])
    #print(new_deaths)
    #death rate from available data
    DR = (death_dat_sum["num"]/new_deaths)*100
    DR_mu=DR.mean()
    ax[2].set_title("Wie viele Impftote relativ zu Covid-Toten?")
    ax[2].hlines(DR_mu,death_dat_sum.index[0],death_dat_sum.index[-1],color="grey",linestyle="dashed",
                 label="Mittelwert: "+str(DR_mu)[0:5]+" %")
    ax[2].plot(death_dat_sum.index,DR,label="Impftote relativ zu Covid-Toten",
               color="tab:blue",alpha=0.8)
    sm=smooth(DR,7)
    ax[2].plot(sm["date"],sm["mu"],color="black",label="7d smoothed mean",linewidth=3)
    ax[2].text(sm["date"][0],sm["mu"][0]+DR.max()*0.1,
               str(sm["mu"][0])[0:5]+ " %",fontweight="bold")
    ax[2].scatter(sm["date"][0],sm["mu"][0],color="black",linewidth=3)
    ax[2].set_ylabel('Verhältnis [%]')
    ax[2].yaxis.set_label_coords(labelx, 0.5)
    ax[2].legend()
    ##################
    #new adverse effects in range of available data
    AER=computeratio(dat_sum,data_vaxx_sum_diff)
    #adverse effect ratio from available data (vaxxinations owid)
    if data_vaxx_sum_diff["vaccine"][0]=="Oxford/AstraZeneca":
        AER = AER.iloc[20::,:]

    if data_vaxx_sum_diff["vaccine"][0]=="Moderna":
        AER = AER.iloc[20::,:]
        
    if data_vaxx_sum_diff["vaccine"][0]=="Johnson&Johnson":
        AER = AER.iloc[30::,:]
    
    AER_mu=AER["rate"].mean()
    #print(AER,datum_temp)
    ax[3].set_title("Anteil von Impfnebenwirkungen")
    ax[3].hlines(AER_mu,dat_sum.index[0],dat_sum.index[-1],color="grey",linestyle="dashed",
                 label="Mittelwert: "+str(AER_mu)[0:5]+" %")
    
    sm2=smooth(AER["rate"],7)
    
    ax[3].plot(AER.index,AER["rate"],label="Impfnebenwirkungsrate",color="tab:orange",alpha=0.8)
    ax[3].plot(sm2["date"],sm2["mu"],color="black",label="7d smoothed mean",linewidth=3)
    ax[3].text(sm2["date"][0],sm2["mu"][0]+AER.max()*0.1,
               str(sm2["mu"][0])[0:5]+ " %",fontweight="bold")
    ax[3].scatter(sm2["date"][0],sm2["mu"][0],color="black",linewidth=3)
    ax[3].set_ylabel('Verhältnis [%]')
    ax[3].yaxis.set_label_coords(labelx, 0.5)
    ax[3].legend(loc="upper left")
    ##############
    #new hospitalizations in range of available data
    HR = computeratio(hosp_dat_sum,data_vaxx_sum_diff)
    if data_vaxx_sum_diff["vaccine"][0]=="Oxford/AstraZeneca":
        HR= HR.iloc[20::,:]
    if data_vaxx_sum_diff["vaccine"][0]=="Johnson&Johnson":
        HR = HR.iloc[30::,:]
    print("HR:",HR)
    HR_mu=HR["rate"].mean()
    ax[4].set_title("Anteil schwerer Nebenwirkungen (Hospitalization/Disabling/Death)")
    ax[4].hlines(HR_mu,hosp_dat_sum.index[0],hosp_dat_sum.index[-1],color="grey",linestyle="dashed",
                 label="Mittelwert: "+str(HR_mu)[0:5]+" %")

    ax[4].plot(HR.index,HR["rate"],label="Anteil schwerer Nebenwirkungen",color="black",alpha=0.8)

    sm2=smooth(HR["rate"],7)
    ax[4].plot(sm2["date"],sm2["mu"],color="black",label="7d smoothed mean",linewidth=3)
    ax[4].text(sm2["date"][0],sm2["mu"][0]+HR.max()*0.1,
               str(sm2["mu"][0])[0:5]+ " %",fontweight="bold")
    ax[4].scatter(sm2["date"][0],sm2["mu"][0],color="black",linewidth=3)
    ax[4].set_ylabel('Verhältnis [%]')
    ax[4].yaxis.set_label_coords(labelx, 0.5)
    ax[4].legend(loc="upper left")
    ##############
    #new deaths in range of available data
    DR2 = computeratio(death_dat_sum,data_vaxx_sum_diff)
    if data_vaxx_sum_diff["vaccine"][0]=="Oxford/AstraZeneca":
        DR2= DR2.iloc[25::,:]
    if data_vaxx_sum_diff["vaccine"][0]=="Johnson&Johnson":
        DR2= DR2.iloc[25::,:]
    DR2_mu=DR2.mean()
    ax[5].set_title("Anteil Impftote")
    ax[5].hlines(DR2_mu,death_dat_sum.index[0],death_dat_sum.index[-1],color="grey",linestyle="dashed",
                 label="Mittelwert: "+str(DR2_mu)[0:5]+" %")
    
    ax[5].plot(DR2.index,DR2["rate"],label="Impfsterberate",color="tab:red",alpha=0.8)
    sm1=smooth(DR2,7)
    ax[5].plot(sm1["date"],sm1["mu"],color="black",label="7d smoothed mean",linewidth=3)
    ax[5].set_ylabel('Verhältnis [%]')
    ax[5].yaxis.set_label_coords(labelx, 0.5)
    ax[5].text(sm1["date"][0],sm1["mu"][0]+DR2.max()*0.1,
               str(sm1["mu"][0])[0:5]+ " %",fontweight="bold")
    ax[5].scatter(sm1["date"][0],sm1["mu"][0],color="black",linewidth=3)

    import matplotlib.dates as mdates
    ax[5].xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax[5].xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
    plt.gcf().autofmt_xdate()

    plt.legend(loc="upper left")#
    #fig.show()
    #fig.savefig(string + ".svg",format="svg", dpi=1200)
    return(fig)

def buildNetwork(dat_filtered):
    symptoms_sum=dat_filtered.groupby(["EV Gateway Receipt Date",'Reaction List PT (Duration – Outcome - Seriousness Criteria)']).agg("sum").reset_index()
    symptoms_sum

    adverse =[]
    for i in range(len(symptoms_sum)):
        te=symptoms_sum.iloc[i,1].split("<BR><BR>")
        #print(len(te))
        for l in range(len(te)):
            adverse.append(te[l].split(" (")[0])

    #get top100 unique symptoms
    un_symptoms=pd.Series(adverse).unique()
    sym =[]
    n =[]
    
    for i in range(len(un_symptoms)):
        n.append(len(pd.Series(adverse)[pd.Series(adverse)==un_symptoms[i]]))
        sym.append(un_symptoms[i])

    adverse_num_df = pd.DataFrame({"symptom":pd.Series(sym),"n":pd.Series(n)})
    adverse_num_df=adverse_num_df.sort_values(by=['n'])
    #top100
    a=adverse_num_df["symptom"].iloc[len(adverse_num_df)-100:len(adverse_num_df)]
    print(list(a))
    b=np.array(list(a))
    c="|".join(b)
    #df mit top100
    dat_filtered=dat_filtered[dat_filtered['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.contains(c,na=False)]
    # len(dat) für pA Berechnung
    N=len(dat_filtered)
    #p(B u A) = p(A u B)
    #--> p(B u A) = p(B|A)*p(A) = p(A|B)*p(B)
    # if dependent events: P(B|A) = P(A u B) / P(A)
    # if independent events: P(B|A) = P(B)
    edge1=[]
    edge2=[]
    edge_to=[]
    edge_from=[]
    edge_pA = []
    edge_pB =[]
    edge_pAIB = []
    edge_pBIA = []
    edge_pAuB = []
    edge_pBuA = []
    # check if dependent events: P(B|A) = P(A u B) / P(A)
    edge_check = []
    
    node_id=[]
    node_name=[]
    node_pA = []

    for j in range(len(b)):
        node_id.append(j)
        node_name.append(b[j])

        temp=dat_filtered[dat_filtered['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.contains(b[j])]

        #node Probability
        pA=len(temp)/N
        node_pA.append(pA)

        for i in range(len(b)):
            e2=int(np.where(pd.Series(b)==b[i])[0][0])
            if b[i] != b[j]:
                #edge from/to  ids
                edge1.append(j)
                #what is index of actual [remaining] element in the original array(b)?
                edge2.append(e2)
                #edge from/to names
                edge_from.append(b[j])
                edge_to.append(b[i])

                #A num symptoms 
                nA=len(temp)
                #
                #calculate  pB|A
                nBIA=len(temp[temp['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.contains(b[i])])
                pBIA = nBIA/nA
                edge_pBIA.append(pBIA)
                #calculate  pBuA
                edge_pBuA.append(pBIA*pA)
                
                #calculate pA|B 
                temp_b=dat_filtered[dat_filtered['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.contains(b[i])]
                nB=len(temp_b)
                pB= nB/N
                edge_pB.append(pB)
                
                nAIB = len(temp_b[temp_b['Reaction List PT (Duration – Outcome - Seriousness Criteria)'].str.contains(b[j])])
                pAIB=nAIB/nB
                edge_pAIB.append(pAIB)
                #calculate pAuB
                pAuB = pAIB*pB
                edge_pAuB.append(pAuB)
                
                #if dependent events: P(B|A) = P(A u B)/P(A)
                edge_check.append(pAuB/pA)


    edges=pd.DataFrame({'from': edge1, 'to': edge2,
                        'value': edge_pBIA,
                        "title":["P(B|A): " + str(round(i *100,2))+ "%" for i in edge_pBIA],
                        "fnode":edge_from,"tnode":edge_to,
                        "pB": edge_pB,"calculated PBIA": edge_check,
                       "p(A|B)":edge_pAIB,"p(B|A)":edge_pBIA,"p(BuA)":edge_pBuA,"p(AuB)":edge_pAuB
                       })
    edges=edges.iloc[:,0:8]
    #filter edges by candidates in range of calculated BIA and empiric BIA +- 10%
    edges=edges[(edges["calculated PBIA"] < (edges["value"]*1.1))&(edges["calculated PBIA"] > (edges["value"]*0.9))] #10 %
    
    nodes=pd.DataFrame({'id': node_id,'value': node_pA ,'label': node_name,'title': ["P(A): " + str(i*100)[0:5]+"%" for i in node_pA]})
    nodes

    return edges,nodes
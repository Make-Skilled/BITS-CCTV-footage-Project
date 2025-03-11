from flask import Flask ,render_template,request,redirect,session
from web3 import Web3,HTTPProvider
import json
import requests
import ipfshttpclient

# ipfs daemon

def connectWithBlockchain(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    if acc==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    
    artifact_path="../build/contracts/CCTVFootage.json"

    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3

def connectWithVideoFeed(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    if acc==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    
    artifact_path="../build/contracts/VideoFeed.json"

    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3


app = Flask(__name__)
app.secret_key='1234'

@app.route('/')
def lan():
    return render_template('landing.html')

@app.route('/signup')
def signup():
    return render_template('SelectSignUp.html')

@app.route('/signin')
def signin():
    return render_template('SelectSignIn.html')

@app.route('/govtsignup')
def govtsigup():
    return render_template('GovtSignUpForm.html')

@app.route('/pvtsignup')
def pvtsignup():
    return render_template('PvtSignUpForm.html')

@app.route('/signinform')
def siginform():
    return render_template('SignInForm.html')

@app.route('/pvtsignupform',methods=['post'])
def pvtsignupform():
    name=request.form['name']
    email=request.form['email']
    password=request.form['password']
    repassword=request.form['repassword']
    if(password!=repassword):
        return render_template('PvtSignUpForm.html',err='Passwords didnt matched')
    else:
        try:
            contract,web3=connectWithBlockchain(0)
            tx_hash=contract.functions.addPrivateOfficial(name,email,password).transact()
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return render_template('PvtSignUpForm.html',res='Signup Successful')
        except :
            return render_template('PvtSignUpForm.html',err='Already exist')
    
@app.route('/govtsignupform',methods=['post'])
def govtsignupform():
    name=request.form['name']
    email=request.form['email']
    password=request.form['password']
    repassword=request.form['repassword']
    if(password!=repassword):
        return render_template('GovtSignUpForm.html',err='Passwords didnt matched')
    else:
        try:
            contract,web3=connectWithBlockchain(0)
            tx_hash=contract.functions.addGovernmentOfficial(name,email,password).transact()
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return render_template('GovtSignUpForm.html',res='Signup Successful')
        except:
            return render_template('GovtSignUpForm.html',err='Already exist')

@app.route('/signinformdata',methods=['post'])
def signinformdata():
    choice=request.form['choice']
    email=request.form['email']
    password=request.form['password']
    print(choice,email,password)
    if(choice=='3'):
        contract,web3=connectWithBlockchain(0)
        adminEmail,adminPassword=contract.functions.viewAdmin().call()
        if (adminEmail==email and adminPassword==password):
            session['username']=email
            session['type']=3
            return redirect('/admindashboard')
        else:
            return render_template('SignInForm.html',err='Invalid Credentials')
    elif(choice=='2'):
        contract,web3=connectWithBlockchain(0)
        _gids,_gname,_gemail,_gpassword,_gstatuses=contract.functions.viewGovernmentOfficial().call()
        try:
            emailindex=_gemail.index(email)
            if(_gstatuses[emailindex]==1):
                if(password==_gpassword[emailindex]):
                    session['username']=email
                    session['type']=2
                    session['id']=_gids[emailindex]
                    return redirect('/govtdashboard')
                else:
                    return render_template('SignInForm.html',err='Invalid Credentials')
            else:
                return render_template('SignInForm.html',err='Wait for Admin Approval')
        except:
            return render_template('SignInForm.html',err='You have to register before login')
    elif(choice=='1'):
        contract,web3=connectWithBlockchain(0)
        _pids,_pname,_pemail,_ppassword,_pstatuses=contract.functions.viewPrivateOfficial().call()
        try:
            emailindex=_pemail.index(email)
            if(_pstatuses[emailindex]==1):
                if (password==_ppassword[emailindex]):
                    session['username']=email
                    session['type']=1
                    session['id']=_pids[emailindex]
                    return redirect('/privatedashboard')
                else:
                    return render_template('SignInForm.html',err='Invalid Credentials')
            else:
                return render_template('SignInForm.html',err='Wait for Admin Approval')
        except:
            return render_template('SignInForm.html',err='You have to register before login')
    return render_template('SignInForm.html',res='Invalid Credentials')

@app.route('/privatedashboard')
def privatedashboardPage():
    return render_template('Pvt/index.html')

@app.route('/govtdashboard')
def govtdashboardPage():
    contract,web3=connectWithBlockchain(0)
    _pids,_pname,_pemail,_ppassword,_pstatuses=contract.functions.viewPrivateOfficial().call()
    data=[]
    for i in range(len(_pids)):
        dummy=[]
        dummy.append(_pids[i])
        dummy.append(_pname[i])
        data.append(dummy)

    contract,web3=connectWithVideoFeed(0)
    _streamids,_owners,_dates,_times,_videohashes=contract.functions.viewHashes().call()
    dates=[]
    times=[]
    for i in range(len(_streamids)):
        if _dates[i] not in dates:
            dates.append(_dates[i])
        if _times[i] not in times:
            times.append(_times[i])

    return render_template('Govt/index.html',l=len(data),dashboard_data=data,l1=len(dates),dashboard_data1=dates,l2=len(times),dashboard_data2=times)

@app.route('/sendreq',methods=['POST'])
def sendreq():
    agency=request.form['agency']
    date=request.form['date']
    time=request.form['time']
    print(agency,date,time)
    requestby=int(session['id'])
    requestto=int(agency)

    contract,web3=connectWithVideoFeed(0)
    _streamids,_owners,_dates,_times,_videohashes=contract.functions.viewHashes().call()
    reqstreamid=0
    print(_streamids,_owners,_dates,_times,_videohashes,agency)
    for i in range(len(_streamids)):
        if date==_dates[i] and time==_times[i] and _owners[i]==int(agency):
            reqstreamid=_streamids[i]
    print(reqstreamid,date,time)
    if(reqstreamid):
        contract,web3=connectWithVideoFeed(0)
        tx_hash=contract.functions.sendrequest(requestby,requestto,reqstreamid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

    contract,web3=connectWithBlockchain(0)
    _pids,_pname,_pemail,_ppassword,_pstatuses=contract.functions.viewPrivateOfficial().call()
    data=[]
    for i in range(len(_pids)):
        dummy=[]
        dummy.append(_pids[i])
        dummy.append(_pname[i])
        data.append(dummy)

    contract,web3=connectWithVideoFeed(0)
    _streamids,_owners,_dates,_times,_videohashes=contract.functions.viewHashes().call()
    dates=[]
    times=[]
    for i in range(len(_streamids)):
        if _dates[i] not in dates:
            dates.append(_dates[i])
        if _times[i] not in times:
            times.append(_times[i])

    if reqstreamid==0:
        return render_template('Govt/index.html',err="request error",l=len(data),dashboard_data=data,l1=len(dates),dashboard_data1=dates,l2=len(times),dashboard_data2=times)
    else:
        return render_template('Govt/index.html',res="request sent",l=len(data),dashboard_data=data,l1=len(dates),dashboard_data1=dates,l2=len(times),dashboard_data2=times)

@app.route('/admindashboard')
def admindashboardPage():
    contract,web3=connectWithBlockchain(0)
    _gids,_gname,_gemail,_gpassword,_gstatuses=contract.functions.viewGovernmentOfficial().call()
    data=[]
    for i in range(len(_gids)):
        dummy=[]
        dummy.append(_gids[i])
        dummy.append(_gname[i])
        dummy.append(_gemail[i])
        dummy.append(_gstatuses[i])
        data.append(dummy)
    _pids,_pname,_pemail,_ppassword,_pstatuses=contract.functions.viewPrivateOfficial().call()
    data1=[]
    for i in range(len(_pids)):
        dummy=[]
        dummy.append(_pids[i])
        dummy.append(_pname[i])
        dummy.append(_pemail[i])
        dummy.append(_pstatuses[i])
        data1.append(dummy)
    return render_template('Admin/index.html',l=len(data),dashboard_data=data,l1=len(data1),dashboard_data1=data1)

@app.route('/logout')
def logout():
    session['username']=None
    session['type']=None
    return redirect('/')

@app.route("/govt/<id1>/<id2>")
def govt(id1,id2):
    print(id1,id2)
    contract,web3=connectWithBlockchain(0)
    tx_hash=contract.functions.updateGovernmentOfficial(int(id1),int(id2)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/admindashboard')

@app.route("/private/<id1>/<id2>")
def private(id1,id2):
    print(id1,id2)
    contract,web3=connectWithBlockchain(0)
    tx_hash=contract.functions.updatePrivateOfficial(int(id1),int(id2)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/admindashboard')

@app.route("/reqaccept/<id1>/<id2>")
def reqaccept(id1,id2):
    print(id1,id2)
    reqid=int(id1)
    reqstatus=int(id2)

    contract,web3=connectWithVideoFeed(0)
    tx_hash=contract.functions.updaterequest(reqid,reqstatus).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/pvtrequests')


@app.route('/storageHistory')
def storageHistory():
    contract,web3=connectWithVideoFeed(0)
    _streamids,_owners,_dates,_times,_videohashes=contract.functions.viewHashes().call()
    data=[]
    for i in range(len(_owners)):
        if(int(_owners[i])==int(session['id'])):
            dummy=[]
            dummy.append(_streamids[i])
            dummy.append(_dates[i])
            dummy.append(_times[i])
            dummy.append(_videohashes[i])
            data.append(dummy)
    return render_template('Pvt/storage_history.html',l=len(data),dashboard_data=data)

@app.route('/pvtrequests')
def pvtrequests():
    contract,web3=connectWithVideoFeed(0)
    _requestby,_requestto,_reqstreamids,_reqstatus,_reqids=contract.functions.viewrequest().call()
    data=[]
    for i in range(len(_reqids)):
        if(_requestto[i]==session['id']):
            dummy=[]
            dummy.append(_requestby[i])
            contract,web3=connectWithBlockchain(0)
            _gids,_gname,_gemail,_gpassword,_gstatuses=contract.functions.viewGovernmentOfficial().call()
            gindex=_gids.index(_requestby[i])
            dummy.append(_gname[gindex])
            dummy.append(_gemail[gindex])
            dummy.append(_reqstreamids[i])
            dummy.append(_reqstatus[i])
            dummy.append(_reqids[i])
            data.append(dummy)
    return render_template('Pvt/requests.html',l=len(data),dashboard_data=data)

@app.route('/accesskeys')
def accesskeys():
    contract,web3=connectWithVideoFeed(0)
    _requestby,_requestto,_reqstreamids,_reqstatus,_reqids=contract.functions.viewrequest().call()
    _streamids,_owners,_dates,_times,_videohashes=contract.functions.viewHashes().call()

    data=[]
    for i in range(len(_reqids)):
        if(int(session['id'])==int(_requestby[i])):
            dummy=[]
            dummy.append(_requestto[i])
            contract,web3=connectWithBlockchain(0)
            _pids,_pname,_pemail,_ppassword,_pstatuses=contract.functions.viewPrivateOfficial().call()
            pindex=_pids.index(_requestto[i])
            dummy.append(_pname[pindex])
            dummy.append(_reqstreamids[i])
            dummy.append(_reqstatus[i])
            dummy.append(_reqids[i])
            streamindex=_streamids.index(_reqstreamids[i])
            dummy.append(_videohashes[streamindex])
            data.append(dummy)
    return render_template('Govt/get_accesskey.html',l=len(data),dashboard_data=data)

@app.route('/evidenceaudit')
def evidenceaudit():
    return render_template('Govt/evidence_verification.html')

@app.route('/audit', methods=['POST'])
def audit():
    chooseFile = request.files['chooseFile']
    chooseFile1 = request.files['chooseFile1']
    
    # Define the IPFS API endpoint
    ipfs_url = 'http://127.0.0.1:5001/api/v0/add'
    
    # Upload first file
    files = {'file': (chooseFile.filename, chooseFile.stream, chooseFile.mimetype)}
    response = requests.post(ipfs_url, files=files)
    video_hash = response.json().get('Hash')
    print(video_hash)
    
    # Upload second file
    files1 = {'file': (chooseFile1.filename, chooseFile1.stream, chooseFile1.mimetype)}
    response1 = requests.post(ipfs_url, files=files1)
    video_hash1 = response1.json().get('Hash')
    print(video_hash1)
    
    # Compare file hashes
    if video_hash1 == video_hash:
        return render_template('Govt/evidence_verification.html', res='Verified and OK')
    else:
        return render_template('Govt/evidence_verification.html', err='Fraud Evidence')
if __name__=="__main__":
    app.run(host='0.0.0.0',port=9001,debug=True)
from flask import Flask,request,jsonify
from db import DB

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/create",methods=['post'])
def create():
    try:
        if not request.json and not request.data and not request.form:
            return jsonify({'status':'failure','reason':'payload cannot be empty'}),400
        if request.json:
            data = dict(request.json)
        elif request.form:
            data = dict(request.form)
        if not data['username']:
            return jsonify({'status':'failure','reason':'username cannot be blank'}),400

        else:
            db_obj = DB()
            username = data['username']
            friends = []
            friends_request = []
            res = db_obj.friendsCollection.find_one({'username':username})
            if res!=None:
                return jsonify({'status':'failure','reason':'username already created'}),400
            else:
                db_obj.insertdata(username,friends,friends_request)
                return jsonify({'result':'success'}),201
    except Exception as e :
        return jsonify({'status':'failure','reason':'Something went wrong . Paylaod cannot be processed'}),500

@app.route("/add/<usernameA>/<usernameB>",methods=['post'])
def add(usernameA,usernameB):
    if '$' in usernameA:
        usernameA = usernameA.strip('$')
    if '$' in usernameB:
        usernameB = usernameB.strip('$')
    db_obj = DB()
    res_usernameA = db_obj.friendsCollection.find_one({'username':usernameA})
    res_usernameB = db_obj.friendsCollection.find_one({'username':usernameB})
    if  res_usernameA == None or res_usernameB == None :
        return jsonify({'status':'failure','reason':'one of the username not found'}),400
    else:
        userAdetails_dict = dict(res_usernameA)
        userBdetails_dict = dict(res_usernameB)
        if usernameB in userAdetails_dict['friends'] and usernameA in userBdetails_dict['friends']:
            return jsonify({'status':'failure','reason':'already friends'}),400
        elif usernameB in userAdetails_dict['friends_request']:
            db_obj.friendsCollection.update_one({'username':usernameA},{'$push':{'friends':usernameB}})
            db_obj.friendsCollection.update_one({'username':usernameB},{'$push':{'friends':usernameA}})
            db_obj.friendsCollection.update_one({'username':usernameB},{'$pull':{'friends_request':usernameA}})
            db_obj.friendsCollection.update_one({'username':usernameA},{'$pull':{'friends_request':usernameB}})
            print('3')
            return jsonify({'status':'success','update':'Both user {0} and {1} are friends'.format(usernameA,usernameB)}),202
        elif usernameA in userBdetails_dict['friends_request']:
            print('4')
            return jsonify({'status':'failure','reason':'{0} already in {1} friends request list'.format(usernameA,usernameB)})
        else:
            db_obj.friendsCollection.update_one({'username':usernameB},{'$push':{'friends_request':usernameA}})
            print('5')
            return jsonify({'status':'success','update':'User {0} has sucessfully raised friend request to {1}'.format(usernameA,usernameB)}),202

@app.route("/friendRequests/<username>",methods=['get'])
def friendRequests(username):
    if '$' in username:
        username = username.strip('$')
    db_obj = DB()
    res = db_obj.friendsCollection.find_one({'username':username})
    if  res == None  :
        return jsonify({'status':'failure','reason':'username not found'}),400
    elif res['friends_request'] == []:
        return jsonify({'status':'failure','reason':'{0} has no friend requests'.format(username)}),404
    else:
        return jsonify({'friend_requests':res['friends_request']}),200
        

@app.route("/friends/<username>",methods=['get'])
def friends(username):
    if '$' in username:
        username = username.strip('$')
    db_obj = DB()
    res = db_obj.friendsCollection.find_one({'username':username})
    if res == None  :
        return jsonify({'status':'failure','reason':'username not found'}),400
    elif res['friends'] == []:
        return jsonify({'status':'failure','reason':'{0} has no friends'.format(username)}),404
    else:
        return jsonify({'friends':res['friends']}),200
        
@app.route("/suggestions/<username>",methods=['get'])
def suggestions(username):
    if '$' in username:
        username = username.strip('$')
    db_obj = DB()
    res = db_obj.friendsCollection.find_one({'username':username})
    if res == None  :
        return jsonify({'status':'failure','reason':'username not found'}),400
    elif res['friends'] == []:
        return jsonify({'status':'failure','reason':'{0} has no friends'.format(username)}),404
    else:
        suggestions_list = []
        searched_user = []
        for user in res['friends']:
            searched_user.append(user)
            res_temp = db_obj.friendsCollection.find_one({'username':user})
            li = res_temp['friends'].copy()
            if username in li:
                li.remove(username)
            for i in li:
                if i not in suggestions_list and i not in res['friends']:
                    suggestions_list.append(i)
 
        count = 2 
        while(count>0):
            templist =  suggestions_list.copy()
            for user in templist:
                if user not in searched_user:
                    searched_user.append(user)
                    res_temp = db_obj.friendsCollection.find_one({'username':user})
                    li = res_temp['friends'].copy()
                    if username in li:
                        li.remove(username)
 
                    for i in li:
                        if i not in suggestions_list and i not in res['friends']:
                            suggestions_list.append(i)

            count = count -1 
        if suggestions_list == []:
            return jsonify({'status':'failure','reason':'{0} has all friends, So no suggestions'.format(username)}),400
        else:
            return jsonify({'suggestions':suggestions_list}),200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
from pymongo import MongoClient

class DB:
    def __init__(self):
        self.client = MongoClient('localhost',27017)
        self.db = self.client['testDBFriends']
        self.friendsCollection = self.db['friendsCollection']

    def insertdata(self,username,friends,friends_request):
        self.friendsCollection.insert_one(

            {
                'username':username,
                'friends':friends,
                'friends_request':friends_request
            }
        )
if __name__=='__main__':
    db =DB()
 
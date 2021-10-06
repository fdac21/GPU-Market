import pymongo, json, pprint, argparse

#Simple script to insert data into mongodb in the correct format using the cli

user = 'jhammer3'
topic = 'topic'

client = pymongo.MongoClient (host="da1.eecs.utk.edu")
db = client ['fdac21mp2']
coll = db[user]

defaultTopic=''
defaultTitle='MP2'
defaultLicense='None'
defaultDescription=''
defaultUrls=[]

requiredVals = {                            \
    'owner': user,                          \
    'topic': defaultTopic,                  \
    'title': defaultTitle,                  \
    'license': defaultLicense,              \
    'description': defaultDescription,      \
    'urls': defaultUrls                     \
}

def checkRecorded():
    pp = pprint.PrettyPrinter(indent=1,width=65)
    for r in coll.find({'owner': user}):
        print(pp.pformat(r))

def insertRow(args):
    for key in requiredVals:
        if key not in args:
            args[key] = requiredVals[key]
    coll.insert_one(args)

def main(args):
    if len(args.keys()) == 0:
        checkRecorded()
    else:
        insertRow(args)

class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs='*', action=ParseKwargs, dest='kwargs')
    args = parser.parse_args()
    main(vars(args)['kwargs'])

if __name__ == "__main__":
    cli()

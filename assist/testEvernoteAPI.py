from evernote.api.client import EvernoteClient
# https://sandbox.yinxiang.com/shard/s1/notestore
dev_token = u"S=s1:U=bb:E=16d3d5c58d5:C=16d194fd3c8:P=1cd:A=en-devtoken:V=2:H=8efe3f9d94f8270f1e06eb8b235c9eca"
client = EvernoteClient(token=dev_token)
noteStore = client.get_note_store()
notebooks = noteStore.listNotebooks()
for n in notebooks:
    print(n.name)
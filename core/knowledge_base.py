import json,uuid,pathlib
BASE=pathlib.Path(__file__).parent.parent/'data'/'knowledge_base.json'
def load_kb():
 try:
  return json.loads(BASE.read_text())
 except:
  return {'documents':[],'classifications':{}}
def save_kb(k):
 BASE.parent.mkdir(exist_ok=True)
 BASE.write_text(json.dumps(k,indent=2))
def add_document(e):
 k=load_kb();e['id']=str(uuid.uuid4());k['documents'].append(e);save_kb(k);return e
def list_documents():
 return load_kb().get('documents',[])

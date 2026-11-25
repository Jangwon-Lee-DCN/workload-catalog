from pathlib import Path
import tempfile,shutil,subprocess,yaml,json
R=Path(__file__).resolve().parents[2]
for side in ['core','edge']:
 with tempfile.TemporaryDirectory(prefix='ims-porch-render-') as directory:
  root=Path(directory)/side;shutil.copytree(R/'free5gc-ims'/side,root)
  def render():
   r=subprocess.run(['kpt','fn','render',str(root),'--image-pull-policy=IfNotPresent'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   assert r.returncode==0,r.stdout.decode()[-2000:]
  render()
  path=root/'setters.yaml';s=yaml.safe_load(path.read_text());s['data']['mysql-password']='native-roundtrip-password'
  if side=='edge':s['data']['phone-hostname']='voice.203.0.113.20.sslip.io'
  path.write_text(yaml.safe_dump(s,sort_keys=False));render()
  docs=[]
  for p in root.rglob('*.yaml'):
   docs += [x for x in yaml.safe_load_all(p.read_text()) if isinstance(x,dict)]
  secret=next(x for x in docs if x.get('kind')=='Secret' and x['metadata']['name']=='ims-db-auth')
  assert secret['stringData']['root-password']=='native-roundtrip-password'
  assert (root/'set-render-state.yaml').is_file()
  before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.yaml')};render()
  after={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.yaml')};assert before==after,'Re-render is not idempotent'
  print(side,'SETTERS_ROUNDTRIP_AND_IDEMPOTENCE_PASS',flush=True)

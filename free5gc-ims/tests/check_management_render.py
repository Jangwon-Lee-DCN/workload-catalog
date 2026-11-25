from pathlib import Path
import yaml,tempfile,shutil,subprocess,concurrent.futures,sys
R=Path(__file__).resolve().parents[2]
cases={'workload-repository':('catalog-name','ims-changed-catalog'),'gpu-services':('gpu-cluster-name','ims-changed-gpu'),'gpu-cluster':('gpu-cluster-name','ims-changed-gpu'),'aws-clusters':('core-cluster-name','ims-changed-core'),'eni-controller':('controller-image','docker.io/example/controller:render-test'),'eni-pool':('aws-region','us-east-1'),'cluster-bindings':('core-cluster-name','ims-changed-core'),'gpu-bindings':('gpu-cluster-name','ims-changed-gpu')}
def check(name,case):
 with tempfile.TemporaryDirectory(prefix='ims-management-'+name) as tmp:
  root=Path(tmp)/name;shutil.copytree(R/'infra/capa-free5gc'/name,root)
  def render():
   p=subprocess.run(['kpt','fn','render',str(root),'--image-pull-policy=IfNotPresent'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT);assert p.returncode==0,p.stdout.decode()[-1500:]
  render();p=root/'setters.yaml';d=yaml.safe_load(p.read_text());d['data'][case[0]]=case[1];p.write_text(yaml.safe_dump(d,sort_keys=False));render()
  assert any(case[1] in p.read_text() for p in root.rglob('*.yaml') if p.name not in ['setters.yaml','set-render-state.yaml']),name
  before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.yaml')};render();after={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.yaml')};assert before==after,(name,'not idempotent')
  print(name,'MANAGEMENT_PORCH_SETTERS_ROUNDTRIP_PASS',flush=True)
if len(sys.argv)>1:
 cases={name:cases[name] for name in sys.argv[1:]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(lambda item:check(*item),cases.items()):pass

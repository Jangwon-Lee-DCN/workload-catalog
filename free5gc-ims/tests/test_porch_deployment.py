import pathlib,yaml,unittest,copy,types,urllib.error,unittest.mock as mock,fnmatch
R=pathlib.Path(__file__).resolve().parents[2]
code=yaml.safe_load((R/'free5gc-ims/gpu/20-platform/bootstrap-code.yaml').read_text())['data']['bootstrap.py'];ns={'__name__':'test'};exec(compile(code,'bootstrap.py','exec'),ns)
class Api:
 def __init__(self):
  self.rows={}
  for namespace,name in [('qwen-tts-lab','voice-model-download'),('qwen-tts-lab','voice-env-setup'),('voice-system','voice-stt-model'),('gpu-cr-system','voice-installation-reference')]:self.rows['/apis/batch/v1/namespaces/'+namespace+'/jobs/'+name]={'status':{'conditions':[{'type':'Complete','status':'True'}]}}
  for namespace,name in [('gpu-cr-system','voice-private-inputs'),('gpu-cr-system','gpu-cr-node-agent'),('kube-system','nvidia-device-plugin-daemonset')]:self.rows['/apis/apps/v1/namespaces/'+namespace+'/daemonsets/'+name]={'metadata':{'generation':2},'status':{'observedGeneration':2,'desiredNumberScheduled':1,'numberAvailable':1}}
  for name in ['controller','webhook']:self.rows['/apis/apps/v1/namespaces/knative-serving/deployments/'+name]={'metadata':{'generation':2},'spec':{'replicas':1},'status':{'observedGeneration':2,'availableReplicas':1}}
  self.rows['/apis/gpu-cr.io/v1alpha1']={'resources':[{'name':'gpucheckpoints'}]}
  self.rows['/apis/serving.knative.dev/v1']={'resources':[{'name':'services'}]}
 def maybe(self,path):return self.rows.get(path)
class Tests(unittest.TestCase):
 def test_generated_repository_packages_survive_management_legacy_path_exclusions(self):
  # Existing management installs retain retired bootstrap paths as excluded history.
  patterns=['core/**','core-cluster/**','core-repo/**','edge/**','edge-cluster/**','edge-repo/**']
  for side in ['core','edge']:
   variant=yaml.safe_load((R/'infra/capa-free5gc/aws-clusters'/(side+'-cluster')/'82-repo-packagevariant.yaml').read_text())
   package=variant['spec']['downstream']['package'].replace('@{'+side+'-cluster-name}',side)
   for filename in ['repository.yaml','gitrepository.yaml','token.yaml']:
    self.assertFalse(any(fnmatch.fnmatchcase(package+'/'+filename,p) for p in patterns),(side,package,filename))
 def test_downstream_argo_excludes_porch_metadata_at_every_package_depth(self):
  for side in ['core','edge']:
   path=R/'infra/capa-free5gc/aws-clusters'/(side+'-cluster')/'82-argoapp-packagevariant.yaml'
   variant=yaml.safe_load(path.read_text());cfg=variant['spec']['pipeline']['mutators'][1]['configMap'];app={'apiVersion':'argoproj.io/v1alpha1','kind':'Application','metadata':{'name':'test'},'spec':{'source':{}}}
   ctx=types.SimpleNamespace(resource_list={'functionConfig':{'data':cfg},'items':[app]});exec(compile(cfg['source'],str(path),'exec'),{'ctx':ctx})
   patterns=app['spec']['source']['directory']['exclude'].strip('{}').split(',')
   for prefix in ['', 'public/', 'cert-manager/', 'nested/subpackage/']:
    for name in ['Kptfile','package-context.yaml','setters.yaml','set-render-state.yaml','function-results.yaml']:
     self.assertTrue(any(fnmatch.fnmatchcase(prefix+name,p) for p in patterns),(side,prefix+name))
   for name in ['secrets.yaml','deployment.yaml','cert-manager/resources.yaml','public/resources.yaml']:
    self.assertFalse(any(fnmatch.fnmatchcase(name,p) for p in patterns),(side,name))
 def test_staged_gpu_packages_exclude_kptfile_from_bootstrap_resources(self):
  for stage in ['00-namespaces','10-crds','20-platform','30-models','40-faas']:
   root=R/'free5gc-ims/gpu'/stage
   resources=[]
   for path in root.rglob('*'):
    if path.is_file() and (path.name=='Kptfile' or path.suffix in ['.yaml','.yml']):
     for obj in yaml.safe_load_all(path.read_text()):
      if isinstance(obj,dict) and obj.get('metadata',{}).get('annotations',{}).get('config.kubernetes.io/local-config')!='true':resources.append(obj)
   self.assertTrue(resources,stage)
   self.assertFalse(any(x.get('kind')=='Kptfile' for x in resources),stage)
   if stage=='10-crds':self.assertIn('gpucheckpoints.gpu-cr.io',[x['metadata']['name'] for x in resources])
 def test_management_function_input_names_are_unique(self):
  paths=list((R/'infra/capa-free5gc').glob('*/setters.yaml'))
  names=[yaml.safe_load(path.read_text())['metadata']['name'] for path in paths]
  self.assertEqual(len(names),len(set(names)))
 def test_argo_skips_function_inputs(self):
  paths=list((R/'infra/capa-free5gc').glob('*/setters.yaml'))+[R/'free5gc-ims'/side/'setters.yaml' for side in ['core','edge']]
  for path in paths:
   annotations=yaml.safe_load(path.read_text())['metadata']['annotations']
   self.assertEqual(annotations['config.kubernetes.io/local-config'],'true')
   self.assertEqual(annotations['argocd.argoproj.io/hook'],'Skip',str(path))
 def test_ready(self):self.assertTrue(ns['platform_ready'](Api()))
 def test_absent_each_prerequisite(self):
  for key in Api().rows:
   a=Api();del a.rows[key];self.assertFalse(ns['platform_ready'](a),key)
 def test_pending_jobs(self):
  for key in Api().rows:
   if '/jobs/' in key:
    a=Api();a.rows[key]['status']={};self.assertFalse(ns['platform_ready'](a),key)
 def test_failed_job(self):
  a=Api();key=next(iter(a.rows));a.rows[key]['status']['conditions']=[{'type':'Failed','status':'True'}]
  with self.assertRaisesRegex(RuntimeError,'voice-model-download'):ns['platform_ready'](a)
 def test_old_generation_not_ready(self):
  for key in Api().rows:
   if '/apps/' in key:
    a=Api();a.rows[key]['status']['observedGeneration']=1;self.assertFalse(ns['platform_ready'](a),key)
 def test_daemonset_zero_not_ready(self):
  a=Api();a.rows['/apis/apps/v1/namespaces/gpu-cr-system/daemonsets/voice-private-inputs']['status']['desiredNumberScheduled']=0;self.assertFalse(ns['platform_ready'](a))
 def test_wait_retry_then_ready(self):
  with mock.patch.dict(ns,{'platform_ready':mock.Mock(side_effect=[urllib.error.HTTPError('url',404,'not ready',{},None),False,True]),'time':types.SimpleNamespace(monotonic=mock.Mock(side_effect=[0,1,2,3]),sleep=mock.Mock())}):ns['wait_platform'](Api(),10)
 def test_wait_timeout(self):
  with mock.patch.dict(ns,{'platform_ready':mock.Mock(return_value=False),'time':types.SimpleNamespace(monotonic=mock.Mock(side_effect=[0,11]),sleep=mock.Mock())}):
   with self.assertRaises(TimeoutError):ns['wait_platform'](Api(),10)
if __name__ == '__main__':
 unittest.main()

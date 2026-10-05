import json, os
def load(path,default):
 try:
  with open(path,encoding='utf-8') as f:return json.load(f)
 except Exception:return default
live=load('real_data/ted_live_normalized.json',[]);report=load('reports/live_ted_500_report.json',{});intel=load('reports/intelligence_report.json',{});quality=load('reports/quality_report.json',{});gate=load('reports/quality_validation_summary.json',{})
run_status=report.get('status','never');last_sync=report.get('run_at') if run_status in ('complete','partial') else None
status={'version':"0.8.5",'early_signals':37,'master_projects':34,'live_records':len(live),'classified_opportunities':intel.get('classified_opportunities',0),'classification_rate_pct':quality.get('classification_rate_pct',0),'opportunities':488+intel.get('classified_opportunities',0),'lifecycle_links':intel.get('lifecycle_candidates',0),'last_sync':last_sync,'ted_run_status':run_status,'ted_errors':len(report.get('errors',[])),'ted_requested':report.get('requested',500),'project_type_classified':report.get('project_type_classified',0),'trade_classified':report.get('trade_classified',0),'quality_confident':gate.get('customer_facing_confident',0),'quality_review':gate.get('held_for_review',0),'quality_unknown':gate.get('suppressed_unknown',0),'quality_records':gate.get('records_evaluated',0)}
os.makedirs('docs/data',exist_ok=True)
with open('docs/data/status.json','w',encoding='utf-8') as f:json.dump(status,f,ensure_ascii=False,indent=2)
print(json.dumps(status,ensure_ascii=False,indent=2))

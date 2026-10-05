"""Bulk feed runner with provenance and checkpoints.

Transport adapters yield normalized SourceEvent dictionaries. This runner persists raw records,
processes them in batches, and records a checkpoint after each successful batch.
"""
import json,os
from pipeline import run

class BulkRunner:
    def __init__(self,db_path,checkpoint_path,batch_size=250):
        self.db_path=db_path; self.checkpoint_path=checkpoint_path; self.batch_size=batch_size

    def execute(self,records):
        records=list(records); all_projects=[]
        checkpoint={"records_total":len(records),"records_processed":0,"batches":0,"status":"running"}
        for i in range(0,len(records),self.batch_size):
            batch=records[i:i+self.batch_size]
            # Current dev pipeline resolves inside each batch. Production persistence later performs
            # cross-batch resolution; keep all raw events immutable now.
            projects=run(batch,self.db_path)
            all_projects.extend(projects)
            checkpoint.update({"records_processed":min(i+len(batch),len(records)),
                               "batches":checkpoint["batches"]+1})
            with open(self.checkpoint_path,"w",encoding="utf-8") as f: json.dump(checkpoint,f,indent=2)
        checkpoint["status"]="complete"
        with open(self.checkpoint_path,"w",encoding="utf-8") as f: json.dump(checkpoint,f,indent=2)
        return all_projects,checkpoint

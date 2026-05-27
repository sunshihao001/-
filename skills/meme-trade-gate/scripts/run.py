"""run.py — Skill 06: meme-trade-gate 主入口"""
from __future__ import annotations
import sys,json
from datetime import datetime,timezone,timedelta
sys.path.insert(0,"/root/sikk-gmgn/skills")
from common.file_io import get_run_dir, save_json, save_markdown
from common.validators import save_validated_json
from common.phase_state import complete_phase,set_gate_decision,block_phase
from common.rule_loader import load_gate_rules, evaluate_gate_rules

def sf(v,d=0.0):
    try:return float(v)
    except Exception:return d

def run(token_address:str, chain:str="sol")->dict:
    rd=get_run_dir(token_address); now=datetime.now(timezone.utc); out=_base(token_address,chain,now)
    try:
        tp=json.load(open(rd/"token_panel.json",encoding="utf-8")); wr=json.load(open(rd/"wallet_roles.json",encoding="utf-8")); ws=json.load(open(rd/"wallet_structure.json",encoding="utf-8")); ev=json.load(open(rd/"evidence_chain.json",encoding="utf-8"))
    except Exception as e:
        out["status"]="ERROR"; out["gate_decision"]="NEED_MORE_DATA"; out["blocker_reasons"].append(f"前置文件缺失: {e}"); _save(token_address,out,"ERROR"); return out
    if tp.get("status")=="BLOCK":
        out["status"]="PASS"; out["gate_decision"]="BLOCK"; out["blocker_reasons"].append("token_panel.status = BLOCK"); _save(token_address,out,"PASS"); return out
    rules=load_gate_rules()
    triggered=evaluate_gate_rules(rules,tp,wr,ws,ev)
    # 修正复杂规则：G03 需要 mint + freeze 同时 false；G05 需要 wash + dominant WASH；G17 bundler > sm+kol
    triggered=_apply_complex_rules(triggered,tp,wr,ws,ev)
    out["decision_reasons"]=triggered
    out["gate_score"]=calculate_gate_score(tp,wr,ws,ev)
    out["downgrade_reasons"]=_collect_downgrades(tp,wr,ws,ev)
    out["missing_fields"]=_collect_missing(tp,wr,ws,ev)
    out["confidence_score"]=ev.get("confidence_score",0.0)
    out["evidence"]=ev.get("behavior_signals",[])
    out["counter_evidence"]=ev.get("counter_evidence",[])
    out["gate_decision"]=decide(triggered,out["gate_score"],tp,wr,ws,ev,out)
    out["phase_permission"]={"research_allowed":True,"paper_allowed":out["gate_decision"]=="PAPER_ONLY","semi_auto_allowed":False,"auto_allowed":False}
    out["next_review_conditions"]=next_review_conditions(triggered)
    out["status"]="PASS"
    out["next_action"]="COMPLETED" if out["gate_decision"] in ("BLOCK","WATCH","NEED_MORE_DATA","PAPER_ONLY") else "COMPLETED"
    _save(token_address,out,"PASS")
    _save_md(token_address,out)
    return out

def _apply_complex_rules(triggered,tp,wr,ws,ev):
    ids={r["rule_id"]:r for r in triggered}
    # remove G03 unless both false
    if "G03" in ids and not (tp.get("security",{}).get("renounced_mint") is False and tp.get("security",{}).get("renounced_freeze_account") is False):
        triggered=[r for r in triggered if r["rule_id"]!="G03"]
    if tp.get("security",{}).get("renounced_mint") is False and tp.get("security",{}).get("renounced_freeze_account") is False and "G03" not in ids:
        triggered.append({"rule_id":"G03","rule_name":"Unrenounced","triggered":True,"input_value":"mint=false, freeze=false","threshold":"both false","contribution":"block"})
    if "G05" in ids and ev.get("dominant_behavior")!="WASH":
        triggered=[r for r in triggered if r["rule_id"]!="G05"]
    if tp.get("security",{}).get("is_wash_trading") and ev.get("dominant_behavior")=="WASH" and "G05" not in ids:
        triggered.append({"rule_id":"G05","rule_name":"Wash Trading","triggered":True,"input_value":"wash+WASH","threshold":"both","contribution":"block"})
    sm=wr.get("wallet_summary",{}).get("smart_money_count",0); kol=wr.get("wallet_summary",{}).get("kol_count",0); bundler=wr.get("wallet_summary",{}).get("bundler_count",0)
    if bundler>sm+kol and "G17" not in ids:
        triggered.append({"rule_id":"G17","rule_name":"Bundler Dominated","triggered":True,"input_value":bundler,"threshold":f"> {sm+kol}","contribution":"watch"})
    return triggered

def calculate_gate_score(tp,wr,ws,ev):
    sec=tp.get("security",{}); score=0; breakdown={"security_score":0,"smart_money_score":0,"structure_score":0,"behavior_score":0,"total_score":0,"max_possible":100}
    s=0
    if sec.get("renounced_mint") and sec.get("renounced_freeze_account"): s+=10
    rr=sf(sec.get("rug_ratio")); s+=10 if rr<0.1 else 5 if rr<0.3 else 0
    top=sf(sec.get("top_10_holder_rate")); s+=5 if top<0.2 else 2 if top<0.4 else 0
    if sec.get("creator_token_status")=="creator_close": s+=5
    breakdown["security_score"]=s; score+=s
    sm=wr.get("smart_money_behavior",{}); cnt=wr.get("wallet_summary",{}).get("smart_money_count",0); s=0
    s+=15 if cnt>=5 else 10 if cnt>=3 else 5 if cnt>=1 else 0
    s+=10 if sm.get("sm_net_direction")=="accumulating" else 5 if sm.get("sm_net_direction")=="neutral" else 0
    if sf(sm.get("sm_avg_unrealized_pnl"))>0: s+=5
    breakdown["smart_money_score"]=s; score+=s
    risk=ws.get("structure_risk",{}).get("overall_structure_risk"); s=20 if risk=="low" else 10 if risk=="medium" else 0
    breakdown["structure_score"]=s; score+=s
    beh=ev.get("dominant_behavior"); s=15 if beh=="ACCUMULATION" else 10 if beh=="EARLY_STAGE" else 0
    conf=sf(ev.get("confidence_score")); s+=5 if conf>=0.8 else 3 if conf>=0.6 else 0
    breakdown["behavior_score"]=s; score+=s
    breakdown["total_score"]=min(score,100); return breakdown

def decide(triggered,score,tp,wr,ws,ev,out):
    if any(r.get("contribution") in ("block","BLOCK") or r.get("rule_id") in ["G01","G02","G03","G04","G05","G06"] for r in triggered): return "BLOCK"
    if ev.get("status")=="NEED_MORE_DATA" or out["missing_fields"] or any(x.get("status")=="ERROR" for x in [tp,wr,ws]): return "NEED_MORE_DATA"
    watch_count=sum(1 for r in triggered if r.get("rule_id","").startswith("G1"))
    total=score["total_score"]
    if watch_count<=2 and sf(ev.get("confidence_score"))>=0.5 and ev.get("dominant_behavior") in ("ACCUMULATION","EARLY_STAGE") and wr.get("wallet_summary",{}).get("smart_money_count",0)>=1 and tp.get("basic_info",{}).get("liquidity",0)>=10000 and tp.get("security",{}).get("rug_ratio",1)<0.3 and total>=66:
        return "PAPER_ONLY"
    if total<=20: return "BLOCK" if triggered else "WATCH"
    return "WATCH"

def _collect_downgrades(*objs):
    out=[]
    for o in objs: out += o.get("downgrade_reasons",[])
    return list(dict.fromkeys(out))
def _collect_missing(*objs):
    out=[]
    for o in objs: out += o.get("missing_fields",[])
    return list(dict.fromkeys(out))
def next_review_conditions(triggered):
    m={"G10":"Re-evaluate when creator_token_status changes to creator_close","G12":"Re-evaluate when smart_degen_count >= 1","G13":"Re-evaluate when SM selling stops or new SM enters","G14":"Re-evaluate when liquidity > $50k","G19":"Re-evaluate when more data available or structure analysis improves"}
    return [m[r["rule_id"]] for r in triggered if r.get("rule_id") in m]
def _base(token,chain,now):
    return {"schema_version":"1.0","skill_name":"meme-trade-gate","task_id":f"{token}_{now.strftime('%Y%m%dT%H%M%SZ')}","token_address":token,"chain":chain,"timestamp":now.isoformat(),"status":"","gate_decision":"","decision_reasons":[],"gate_score":{},"phase_permission":{"research_allowed":True,"paper_allowed":False,"semi_auto_allowed":False,"auto_allowed":False},"next_review_conditions":[],"evidence":[],"counter_evidence":[],"confidence_score":0.0,"downgrade_reasons":[],"blocker_reasons":[],"missing_fields":[],"valid_until":(now+timedelta(minutes=15)).isoformat(),"next_action":"COMPLETED","handoff_to":"controller"}
def _save(token,out,status):
    save_validated_json(out,get_run_dir(token)/"trade_gate.json"); complete_phase(token,"trade_gate",status); set_gate_decision(token,out.get("gate_decision"))
def _save_md(token,out):
    md=f"# Trade Gate: {token}\n\nDecision: {out['gate_decision']}\nScore: {out['gate_score'].get('total_score')}/100\nConfidence: {out['confidence_score']}\n\nRules: {', '.join(r['rule_id'] for r in out['decision_reasons'])}\n"
    save_markdown(md,get_run_dir(token)/"trade_gate.md")
if __name__=="__main__":
    import argparse; p=argparse.ArgumentParser(); p.add_argument("token_address"); p.add_argument("--chain",default="sol"); a=p.parse_args(); print(json.dumps(run(a.token_address,a.chain),ensure_ascii=False,indent=2))

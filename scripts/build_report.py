#!/usr/bin/env python3
"""Generate HTML, Markdown and optional PDF from verified execution evidence."""
import argparse
import datetime as dt
import html
import json
import re
import textwrap
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REFS=[
 ('Project specification','Secure OS (CS5101) - Project Handout.pdf, version 1.0, supplied by the user; 35 pages'),
 ('Ubuntu Desktop','https://ubuntu.com/download/desktop'),
 ('Lima installation','https://lima-vm.io/docs/installation/'),
 ('Lima snapshot limitations','https://lima-vm.io/docs/config/snapshots/'),
 ('Docker official Ubuntu installation','https://docs.docker.com/engine/install/ubuntu/'),
 ('Ubuntu AppArmor','https://ubuntu.com/server/docs/how-to/security/apparmor/'),
 ('Linux process status','https://man7.org/linux/man-pages/man5/proc_pid_status.5.html'),
 ('Linux memory mappings','https://man7.org/linux/man-pages/man2/mmap.2.html'),
 ('Linux capabilities','https://man7.org/linux/man-pages/man7/capabilities.7.html'),
 ('systemd execution controls','https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html'),
 ('OpenSSH manuals','https://www.openssh.com/manual.html'),
]
FINDINGS=[
 ('F1','Confidentiality / authorization','Bob can read the synthetic incident record at mode 0644.','root:securelab and 0640; Alice remains an authorized reader.','Bob read denied; Alice read succeeds.'),
 ('F2','Integrity / authorization','World-writable configuration allows Bob to modify settings.','Change mode 0666 to 0640.','Bob write test changes from allowed to denied.'),
 ('F3','Integrity / isolation','A mode-0777 directory allows Bob to create entries.','Use root:securelab and 0750.','Bob creates a file before; creation is denied afterward.'),
 ('F4','Attack surface','An unnecessary HTTP listener exposes a fixture on guest loopback port 8088.','Stop the dedicated practice service.','HTTP succeeds before; connection fails and socket is absent afterward.'),
 ('F5','Privilege separation','A sleep worker runs as root despite requiring no privileged operations.','Run as nobody with NoNewPrivileges and ProtectSystem=strict.','Observe root UID before and nobody UID plus NoNewPrivs=1 afterward.'),
 ('F6','Integrity monitoring','No protected comparison baseline exists for the practice configuration.','Store a root-readable SHA-256 baseline outside the fixture.','Clean check passes, deliberate drift fails, restored file passes.'),
]

def evidence_excerpt(n,log):
    log=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '',log)
    log=log.replace('\x00','')
    lines=[x for x in log.splitlines() if x and not x.startswith('+') and not x.startswith('UTC:') and not x.startswith('Mission:')]
    patterns={1:r'UID|GID|uid=',2:r'hello.txt|write\(|close\(|Hello from',3:r'PID:|Command:|Uid:|Threads:|CapEff:|NoNewPrivs:|Open file',4:r'PID =|&secret|\[stack\]|\[heap\]',5:r'run [0-9]|Expected:|Actual',6:r'received:',7:r'^[-d]|VERIFIED',8:r'user:|mask:|VERIFIED',9:r'uid=|Current:|cap_net|Bounding',10:r'Copying|exit:|stack smashing|ERROR:|SUMMARY:|Accepted:|Rejected:',11:r'Canary|PIE|NX|RELRO|GNU_STACK|stack_chk|^[012]$',12:r'VERIFIED|incident|Permission denied',13:r'^[a-f0-9]{64}|OK|FAILED|VERIFIED',14:r'securelab-.*: ',15:r'address_space|^Uid:|^Threads:|^CapEff:',16:r'Hello from Docker|Ubuntu|namespace|pid:\[|Cgroup|67108864|^32$|CapEff|NoNewPrivs|Read-only|^[0-9]+ [0-9]+$',17:r'allowed.txt:|denied.txt:|securelab-probe|apparmor="DENIED"',18:r'VERIFIED|allowed.txt:|denied.txt:|Current:',19:r'Verified:|Default:|^Uid:|^NoNewPrivs:|nobody|^0077|^600 ',20:r'LOCAL_SSH|uid=|Accepted publickey|127.0.0.1:2222|passwordauthentication|permitrootlogin',21:r'Linux |PRETTY_NAME|Virtualization|Hypervisor|^apple|^kvm|aarch64',22:r'^F[1-6] VERIFIED'}
    selected=[x for x in lines if re.search(patterns[n],x)]
    if not selected: selected=lines[-8:]
    # Preserve race counts and AppArmor evidence; wrap safely for printable output.
    limit={5:24,8:13,16:16,19:12}.get(n,9)
    return '\n'.join(selected[:limit])[:2500]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',type=Path)
    ap.add_argument('--no-pdf',action='store_true')
    a=ap.parse_args()
    run=a.run or ROOT/(ROOT/'evidence/latest.txt').read_text().strip()
    if not run.is_absolute(): run=ROOT/run
    manifest=json.loads((run/'manifest.json').read_text())
    notes=json.loads((ROOT/'docs/mission-notes.json').read_text())
    design_tables=json.loads((ROOT/'docs/design-tables.json').read_text())
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    count=sum(x['status']=='verified' for x in manifest['missions'].values())
    records=[]
    for r in notes:
        m=manifest['missions'].get(f'{r["id"]:02d}')
        rr=dict(r,execution=m)
        rr['log_path']=str((run/m['log']).relative_to(ROOT)) if m else ''
        rr['excerpt']=evidence_excerpt(r['id'],(run/m['log']).read_text(errors='replace')) if m else 'Not executed.'
        records.append(rr)
    summary=(f'{count}/22 mission scripts verified in run {manifest["run_id"]}. '
             'This includes a six-finding practice assessment, not the unavailable instructor challenge. '
             'All execution claims refer to captured guest output; conceptual explanations and predictions are labeled separately.')
    scope=('Host: Apple Silicon macOS. Guest: headless Ubuntu 26.04 LTS ARM64 under Lima/Apple VZ, '
           '2 vCPUs, 4 GiB RAM and 40 GiB sparse disk. No host folders mounted; no container ports published. '
           'Guest system and kernel details are captured in Mission 21. '
           'The Desktop/VirtualBox recommendation is adapted to this host. '
           'The missing instructor shared-memory sample is replaced with our synchronized anonymous mapping. '
           'Recorded guest platform: '+manifest['platform']+'.')
    threat=('Assets: synthetic incident/configuration records, process memory, service credentials and availability. '
            'Adversaries: an unprivileged lab user (Bob), malformed input and a compromised unprivileged application. '
            'Trusted dependencies: guest kernel, privileged administrator, compiler, baseline store and the host virtualization stack. '
            'The practice assessment tests only seeded fixtures inside /opt/securelab/practice and dedicated transient services. '
            'Host exploitation, public systems and production security certification are outside its scope.')
    limits=('The instructor Mission 22 image and separate rules remain unavailable. The final assessment here is practice only. '
            'RBAC is a conceptual comparison, not a deployed role engine. '
            'Journal markers in Mission 14 are synthetic events, explicitly labeled; they are not automatic records of earlier missions. '
            'The unsafe race has undefined behavior and varies between runs. '
            'Short successful tests do not prove complete confinement or absence of vulnerabilities. '
            'Host secure boot, storage encryption, a hardware TEE and independent forensic authenticity were not measured. '
            'Personalize the reflective answers before submission.')
    patch_log=run/'mission-19/after.txt'
    if patch_log.exists():
        pending=[line.split('/')[0] for line in patch_log.read_text(errors='replace').splitlines() if '[upgradable from:' in line]
        limits+=' Recorded pending packages after hardening: '+(', '.join(pending) if pending else 'none listed')+'. See the original apt output for deferred/phased updates.'
    improvements=('Use the instructor challenge when supplied; compare its rules before applying changes. '
                  'Export the evidence checksum to a separate trusted location; add remote/persistent audit retention and clock monitoring. '
                  'Test sandbox controls against a broader required-function matrix and review patch state after a reboot. '
                  'Consider encrypted storage and verified boot as separate extensions. '
                  'Keep Docker access restricted and review its firewall interaction before ever publishing a port.')
    header=f'# SECURELAB - CS5101\n\n## Executive summary\n\n{summary}\n\n## System profile\n\n{scope}\n\n## Threat model and attack surface\n\n{threat}\n\n'
    practice_status=manifest['missions'].get('22',{}).get('status','not run')
    md=header+'## Practice assessment findings\n\nExecution status: '+practice_status+'. The conditions, controls and retests below describe the practice design; actual completion requires verified Mission 22 evidence.\n\n'
    for f in FINDINGS:
        md+=f'### {f[0]}: {f[1]}\n\nCondition: {f[2]}\n\nRemediation: {f[3]}\n\nRetest: {f[4]}\n\n'
    md+='These are generated teaching weaknesses, not findings on the macOS host. Evidence: '+str(run.relative_to(ROOT))+'/mission-22/.\n\n'
    for r in records:
        m=r['execution']; status=m['status'].upper() if m else 'NOT RUN'
        md+=f'## Mission {r["id"]:02d}: {r["title"]}\n\nStatus: **{status}**. '
        if m: md+=f'Exit: {m["exit_code"]}; attempt {m["attempt"]}; UTC {m["started_utc"]}. Evidence: `{r["log_path"]}`.\n\n'
        else: md+='No execution evidence.\n\n'
        for k in ['question','prediction']:
            md+=f'**{k.title()}:** {r[k]}\n\n'
        md+='**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.\n\n'
        md+='**Observation (captured excerpt):**\n\n```text\n'+r['excerpt']+'\n```\n\n'
        for k in ['concept','defense','verification','reflection']:
            md+=f'**{k.title()}:** {r[k]}\n\n'
        for q,answer in r['answers'].items(): md+=f'**Q{q}.** {answer}\n\n'
    md+='## Design comparisons and inventories\n\n'
    for t in design_tables:
        md+='### '+t['title']+'\n\n'
        for row in t['rows']:
            md+='; '.join(f'{column}: {value}' for column,value in zip(t['columns'],row))+'\n\n'
    md+='## Limitations and outstanding instructor requirement\n\n'+limits+'\n\n## Future improvements\n\n'+improvements+'\n\n## References\n\n'
    for title,url in REFS: md+=f'- {title}: {url}\n'
    (out/'securelab-report.md').write_text(md)
    # Standalone HTML: no external fonts, scripts or network dependencies.
    esc=html.escape
    pieces=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SECURELAB - CS5101 report</title>',
    '''<style>:root{color-scheme:light dark}*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,sans-serif;background:#f5f7fa;color:#172333}header,main{max-width:1080px;margin:auto;padding:32px}header{border-bottom:3px solid #235879}h1{font-size:32px;margin:0}h2{font-size:24px;margin-top:2em}h3{font-size:19px}a{color:#235879}nav{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}article{padding:20px 0;border-top:1px solid #bdc9d2}pre{background:#172333;color:#eef5fa;padding:18px;overflow:auto;font:13px/1.5 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;vertical-align:top;border-bottom:1px solid #bdc9d2;padding:10px}.meta{font-size:13px;color:#485e70}.notice{border-left:4px solid #956124;padding:12px 20px;background:#f4eddf}.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}details{margin:12px 0}summary{cursor:pointer;font-weight:600}@media(max-width:700px){.grid{grid-template-columns:1fr}header,main{padding:20px}}@media(prefers-color-scheme:dark){body{background:#141b23;color:#edf1f4}a{color:#9ccce8}.meta{color:#a9bdcc}.notice{background:#322a1e}pre{background:#090e14}}@media print{nav{display:none}article{break-before:page}pre{color:#172333;background:#edf1f4}}</style>''',
    '<header><p class="meta">SECURE OPERATING SYSTEMS / CS5101</p><h1>Break it. Understand it. Secure it.</h1><p>'+esc(summary)+'</p>',
    '<p class="notice">Practice challenge only: the instructor Mission 22 rules and image were not supplied. Personalize the reflective answers before submission.</p><nav><a href="#findings">Findings</a><a href="#missions">Missions</a><a href="#limits">Limitations</a><a href="pdf/securelab-report.pdf">Printable PDF</a></nav></header><main>',
    '<div class="grid"><section><h2>System profile</h2><p>'+esc(scope)+'</p></section><section><h2>Threat model</h2><p>'+esc(threat)+'</p></section></div>',
    '<h2 id="findings">Six practice findings</h2><p>Execution status: '+esc(practice_status)+'. Retests below describe the practice design; completion requires verified evidence.</p><table><thead><tr><th>Finding</th><th>Before</th><th>Remediation</th><th>Retest</th></tr></thead><tbody>']
    for f in FINDINGS: pieces.append('<tr>'+''.join('<td>'+esc(t)+'</td>' for t in [f[0]+' / '+f[1],f[2],f[3],f[4]])+'</tr>')
    pieces.append('</tbody></table><h2 id="missions">Mission evidence</h2><nav>'+''.join(f'<a href="#m{r["id"]}">{r["id"]:02d}</a>' for r in records)+'</nav>')
    for r in records:
        m=r['execution']; status=m['status'].upper() if m else 'NOT RUN'
        pieces.append(f'<article id="m{r["id"]}"><h2>Mission {r["id"]:02d}: {esc(r["title"])}</h2><p class="meta">{status}')
        if m: pieces.append(f' / exit {m["exit_code"]} / attempt {m["attempt"]} / {esc(m["started_utc"])} / <a href="../{esc(r["log_path"])}">Full evidence log</a>')
        pieces.append('</p>')
        for k in ['question','prediction']: pieces.append(f'<p><strong>{k.title()}:</strong> {esc(r[k])}</p>')
        pieces.append('<h3>Observed output</h3><pre>'+esc(r['excerpt'])+'</pre>')
        for k in ['concept','defense','verification','reflection']: pieces.append(f'<p><strong>{k.title()}:</strong> {esc(r[k])}</p>')
        pieces.append('<details><summary>Handout answers</summary>')
        for q,answer in r['answers'].items(): pieces.append(f'<p><strong>Q{q}.</strong> {esc(answer)}</p>')
        pieces.append('</details></article>')
    pieces.append('<h2>Design comparisons and inventories</h2>')
    for t in design_tables:
        pieces.append('<h3>'+esc(t['title'])+'</h3><table><thead><tr>'+''.join('<th>'+esc(c)+'</th>' for c in t['columns'])+'</tr></thead><tbody>')
        for row in t['rows']: pieces.append('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>')
        pieces.append('</tbody></table>')
    pieces.append('<h2 id="limits">Limitations</h2><p>'+esc(limits)+'</p><h2>Future improvements</h2><p>'+esc(improvements)+'</p><h2>References</h2><ul>')
    for title,url in REFS:
        pieces.append('<li>'+ (f'<a href="{esc(url)}">{esc(title)}</a>' if url.startswith('https:') else esc(title+': '+url))+'</li>')
    pieces.append('</ul></main></html>')
    (out/'securelab-report.html').write_text(''.join(pieces))
    if not a.no_pdf: build_pdf(out,records,manifest,summary,scope,threat,limits,improvements)
    print(f'Generated report from {run}; {count}/22 verified')


def build_pdf(out,records,manifest,summary,scope,threat,limits,improvements):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,KeepTogether,Table,TableStyle
    from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyLab',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=7))
    styles.add(ParagraphStyle(name='LabelLab',fontName='Helvetica-Bold',fontSize=9.5,leading=13,spaceBefore=7,spaceAfter=3,textColor=colors.HexColor('#235879')))
    styles.add(ParagraphStyle(name='SmallLab',fontName='Helvetica',fontSize=8,leading=10.5,spaceAfter=5,textColor=colors.HexColor('#425366')))
    styles.add(ParagraphStyle(name='CodeLab',fontName='Courier',fontSize=7,leading=9,spaceBefore=5,spaceAfter=8,backColor=colors.HexColor('#f0f3f6'),borderPadding=7))
    styles['Title'].fontName='Helvetica-Bold'; styles['Title'].textColor=colors.HexColor('#173e59')
    styles['Heading1'].fontSize=20; styles['Heading1'].leading=24
    styles['Heading2'].fontSize=13; styles['Heading2'].leading=17
    pdf=out/'pdf'; pdf.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(pdf/'securelab-report.pdf'),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=46,bottomMargin=42,
                          title='SECURELAB - CS5101 evidence and security report',author='SECURELAB project workspace')
    story=[]
    def para(s,style='BodyLab'): return Paragraph(html.escape(s),styles[style])
    def h(s): story.append(para(s,'Heading2'))
    def p(s): story.append(para(s))
    def field(label,s): story.append(para(label,'LabelLab'));p(s)
    def code(s):
        lines=[]
        printable=s.encode('ascii','backslashreplace').decode('ascii')
        for x in printable.splitlines(): lines.extend(textwrap.wrap(x,100,replace_whitespace=False,drop_whitespace=False) or [''])
        story.append(Preformatted('\n'.join(lines),styles['CodeLab']))
    story.extend([Spacer(1,30),para('SECURELAB','Title'),para('Secure Operating Systems / CS5101','Heading1'),Spacer(1,14)])
    p('Project implementation, captured experiments and practice security assessment')
    field('Executive summary',summary)
    field('Evidence run',manifest['run_id']+' / '+manifest['started_utc'])
    field('Scope and substitutions',scope)
    field('Outstanding instructor requirement','Mission 22 requires a separate rules document and prepared VM that were not provided. This report includes an explicitly labeled practice assessment only.')
    field('Reproduction','See README.md. Exact source, commands, logs, all attempts and checksums are included in the submission archive. Predictions and conceptual answers are not measurements.')
    story.append(PageBreak())
    story.append(para('Assessment method and trust model','Heading1'))
    field('Threat model',threat)
    field('Attack surface','Guest services and listeners; file/path traversal permissions; unsafe C memory operations; IPC endpoints; privileged service identity; Docker daemon; AppArmor policy and guest management SSH. Root-equivalent lab administrator and host virtualization remain trusted.')
    field('Evidence discipline','The runner records UTC boundaries, shell commands, stdout/stderr and exit codes. Every success requires a mission sentinel; expected denials and sanitizer exits are asserted. All attempts are retained. SHA256SUMS covers the evidence tree. A checksum is a local integrity reference, not proof of independent authenticity.')
    field('Hardening approach','Collect baseline before remediation. Apply scoped changes with recovery available. Retest the same negative condition and retain positive behavior. Mission 19 implements default-deny incoming firewall rules, an unprivileged confined worker and a restrictive future-file umask; package state is recorded separately.')
    field('Recovery','For this VZ backend, SECURELAB-CLEAN is an APFS clone of the stopped disk, not the unsupported Lima QEMU snapshot command. Restore only while stopped. A scoped Mission 19 rollback restores UFW and removes the lab worker and umask rule; package upgrades require disk recovery for full reversal.')
    h('Execution index')
    for i in range(0,len(records),2):
        line=[]
        for r in records[i:i+2]:
            m=r['execution']; line.append(f'{r["id"]:02d} {r["title"]}: '+(m['status'] if m else 'not run'))
        p('    |    '.join(line))
    story.append(PageBreak())
    story.append(para('Practice assessment: findings','Heading1'))
    p('Mission 22 execution status: '+manifest['missions'].get('22',{}).get('status','not run')+'. These six controlled weaknesses are created by scripts/practice_challenge.sh in the disposable guest. They are not discovered vulnerabilities of the macOS host or the unavailable instructor image.')
    for f in FINDINGS:
        story.append(KeepTogether([para(f[0]+' - '+f[1],'Heading2'),para('Before: '+f[2]),para('Control: '+f[3]),para('Verification: '+f[4])]))
    p('Full baseline, command traces and after-state are in mission-22 evidence. All six markers must be present before the runner records success.')
    # Core mission sheets, one clear start per mission.
    for r in records:
        story.append(PageBreak())
        story.append(para(f'Mission {r["id"]:02d}','SmallLab'))
        story.append(para(r['title'],'Heading1'))
        m=r['execution']
        if m:
            p(f'Status: {m["status"].upper()} / exit {m["exit_code"]} / attempt {m["attempt"]}')
            story.append(para('UTC '+m['started_utc']+' to '+m['ended_utc'],'SmallLab'))
            story.append(para('Evidence: '+r['log_path'],'SmallLab'))
        else:p('NOT EXECUTED. No observed result can be claimed.')
        field('Question',r['question']);field('Prediction',r['prediction'])
        field('Experiment','The exact commands and helper invocations are in missions/run.sh and recorded in the full evidence log. Source code is under src/ and scripts/.')
        story.append(para('Observation - actual captured output','LabelLab'));code(r['excerpt'])
        field('Concept',r['concept']);field('Defense',r['defense']);field('Verification',r['verification']);field('Reflection / limits',r['reflection'])
    # Render diagrams natively so the PDF is standalone rather than depending on Mermaid.
    story.append(PageBreak());story.append(para('Protection boundaries','Heading1'))
    def stack(labels,width=470):
        d=Drawing(width,len(labels)*44)
        for i,label in enumerate(labels):
            y=(len(labels)-i-1)*44
            d.add(Rect(0,y+8,width,30,fillColor=colors.HexColor('#edf3f7'),strokeColor=colors.HexColor('#bbcbd7')))
            d.add(String(width/2,y+19,label,fontName='Helvetica',fontSize=9,textAnchor='middle',fillColor=colors.HexColor('#173e59')))
            if y>0:
                d.add(Line(width/2,y+8,width/2,y-1,strokeColor=colors.HexColor('#4f6679')))
                d.add(Polygon([width/2-3,y+1,width/2+3,y+1,width/2,y-4],fillColor=colors.HexColor('#4f6679')))
        return d
    h('Mission 2 - kernel mediation')
    story.append(stack(['Application: syscall_demo','System-call boundary: openat / write / close','Guest kernel: credentials, policy and validation','Filesystem and virtual disk']))
    h('Missions 16 and 21 - actual stack')
    story.append(stack(['Container process (namespaces and cgroups) / guest application','Ubuntu 26.04 ARM64 kernel (shared by containers)','Virtual CPU / memory / disk / NAT network','Apple Virtualization.framework / hypervisor mechanisms','macOS host kernel','Apple Silicon hardware']))
    p('Lima manages VM lifecycle and the managed SSH channel. It is not the hardware hypervisor. Containers share the Ubuntu guest kernel; the VM has its own kernel. Host compromise can undermine the guest. No host folder mounts or published container ports are used.')
    story.append(PageBreak());story.append(para('Memory and privilege diagrams','Heading1'))
    h('Mission 4 - schematic address-space isolation')
    story.append(stack(['Process A: text RX / heap RW / libraries / stack RW','Process A page tables -> MMU permission checks','Physical pages mapped for Process A']))
    p('Process B uses different page tables. The same numeric pointer can identify different data or an unmapped page. Controlled debugging APIs are exceptions enforced by kernel policy. Actual mappings are captured in mission-04/maps.txt.')
    h('Mission 9 - broad versus narrow privilege')
    story.append(stack(['Broad design: all parsing and processing as root','Narrow design: unprivileged parser -> validated helper request','Small audited helper: only the required privileged operation']))
    p('A Linux capability narrows a class of privileged kernel operations; it does not automatically make a protocol or parser secure.')
    h('Mission 10 - fixed teaching copy')
    code('buffer[16]: | valid indexes 0..15 | adjacent memory ...\n34-byte copy|XXXXXXXXXXXXXXXX|XXXXXXXXXXXXXXXXXX\n                             ^ first out-of-bounds byte\nSafe bound: 15 payload bytes + 1 NUL; reject 16 + NUL.')
    # Append conceptual answers independently from measured observations.
    story.append(PageBreak());story.append(para('Handout answers and design notes','Heading1'))
    p('These are explanatory answers. Reflection prompts are drafts grounded in the experiments; personalize them using your own learning experience. They are not invented first-person observations.')
    for r in records:
        h(f'Mission {r["id"]:02d} - {r["title"]}')
        for q,answer in r['answers'].items():
            story.append(KeepTogether([para('Q'+q,'LabelLab'),para(answer)]))
    # Comparison tables required by the handout; all content is conceptual design.
    for t in json.loads((ROOT/'docs/design-tables.json').read_text()):
        story.append(PageBreak());story.append(para(t['title'],'Heading1'))
        p('Design rationale; actual permissions and resource limits are verified in the corresponding mission logs.')
        cells=[[para(c,'SmallLab') for c in t['columns']]]+[[para(c) for c in row] for row in t['rows']]
        tab=Table(cells,colWidths=[(A4[0]-88)/len(t['columns'])]*len(t['columns']),repeatRows=1,hAlign='LEFT')
        tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#aabfcc')),('LINEBELOW',(0,1),(-1,-1),0.4,colors.HexColor('#d5dfe6'))]))
        story.append(tab)
    # Supporting comparison and permission design required by the handout.
    for name,title in [('permission-design.md','Permission design'),('resource-policy.md','Application resource policy'),('access-models.md','Access-control comparison')]:
        story.append(PageBreak());story.append(para(title,'Heading1'))
        for block in (ROOT/'docs'/name).read_text().split('\n\n'):
            if block.startswith('# '):continue
            if block.startswith('## '):h(block[3:])
            else:p(block.replace('`','').replace('\n',' '))
    story.append(PageBreak());story.append(para('Limitations and next steps','Heading1'))
    field('Limits',limits);field('Future improvements',improvements)
    h('References')
    p('Official technical references checked on 16 November 2026. The user-supplied handout defines mission scope. Linux semantics and installation guidance are supported by the following primary documentation.')
    for title,url in REFS:
        if url.startswith('https:'):
            story.append(Paragraph(html.escape(title)+': <link href="'+html.escape(url)+'">'+html.escape(url)+'</link>',styles['SmallLab']))
        else:story.append(para(title+': '+url,'SmallLab'))
    def page(c,doc):
        c.saveState(); w,h=A4
        c.setStrokeColor(colors.HexColor('#c6d2dc'));c.line(44,h-28,w-44,h-28)
        c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#496074'))
        c.drawString(44,h-22,'SECURELAB / CS5101 / evidence-based project report')
        c.drawString(44,25,'Practice assessment; instructor Mission 22 remains separate')
        c.drawRightString(w-44,25,str(doc.page));c.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)

if __name__=='__main__':main()

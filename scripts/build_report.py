#!/usr/bin/env python3
"""Build the submission PDF from recorded experiment evidence and final analysis."""
import argparse
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
 ('Ubuntu phased updates','https://ubuntu.com/server/docs/explanation/software/about-apt-upgrade-and-phased-updates/'),
]
FINDINGS=[
 ('F1','Confidentiality / authorization','Bob can read the synthetic incident record at mode 0644.','root:securelab and 0640; Alice remains an authorized reader.','Bob read denied; Alice read succeeds.'),
 ('F2','Integrity / authorization','World-writable configuration allows Bob to modify settings.','Change mode 0666 to 0640.','Bob write test changes from allowed to denied.'),
 ('F3','Integrity / isolation','A mode-0777 directory allows Bob to create entries.','Use root:securelab and 0750.','Bob creates a file before; creation is denied afterward.'),
 ('F4','Attack surface','An unnecessary HTTP listener exposes a fixture on guest loopback port 8088.','Stop the dedicated practice service.','HTTP succeeds before; connection fails and socket is absent afterward.'),
 ('F5','Authorization / isolation','A sleep worker runs as root despite requiring no privileged operations.','Run as nobody with NoNewPrivileges and ProtectSystem=strict.','Observe root UID before and nobody UID plus NoNewPrivs=1 afterward.'),
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
    a=ap.parse_args()
    run=a.run or ROOT/(ROOT/'evidence/latest.txt').read_text().strip()
    if not run.is_absolute(): run=ROOT/run
    manifest=json.loads((run/'manifest.json').read_text())
    records=[]
    for row in json.loads((ROOT/'docs/mission-notes.json').read_text()):
        m=manifest['missions'].get(f'{row["id"]:02d}')
        r=dict(row,execution=m)
        r['log_path']=str((run/m['log']).relative_to(ROOT)) if m else ''
        r['excerpt']=evidence_excerpt(row['id'],(run/m['log']).read_text(errors='replace')) if m else 'Not executed.'
        if row['id']==19 and (run/'mission-19/umask-verification.txt').exists():
            after=(run/'mission-19/after.txt').read_text()
            r['excerpt']='\n'.join(line for line in after.splitlines() if re.match(r'^(Status:|Default:|User=|NoNewPrivileges=|ProtectSystem=|MemoryMax=|TasksMax=|Uid:|NoNewPrivs:)',line))
            r['excerpt']+='\n'+(run/'mission-19/umask-verification.txt').read_text().strip()
        records.append(r)
    count=sum(v['status']=='verified' for v in manifest['missions'].values())
    core=sum(manifest['missions'].get(f'{n:02d}',{}).get('status')=='verified' for n in range(1,22))
    test_log=(ROOT/'evidence/program-tests.log').read_text()
    test_match=re.search(r'Ran (\d+) tests',test_log)
    assert test_match and '\nOK\n' in test_log,'Behavior tests must be recorded as passed'
    test_count=int(test_match.group(1))
    summary=(f'{core}/21 core mission scripts verified; the separate practice-assessment script is '
             f'{manifest["missions"].get("22",{}).get("status","not run")}. '
             f'{count}/22 laboratory scripts and {test_count} behavior tests passed in run {manifest["run_id"]}. '
             'The report includes code references, actual results, requirement mapping, hardening controls and analytical reflections. '
             'The instructor-specific Mission 22 is awaiting its separate rules and prepared image; the six-finding practice assessment does not replace it.')
    scope=('Host: Apple Silicon macOS. Guest: headless Ubuntu 26.04 LTS ARM64 under Lima/Apple VZ, '
           '2 vCPUs, 4 GiB RAM and 40 GiB sparse disk. Network: NAT, no host-folder mounts and no published container ports. '
           'The handout recommends Desktop/VirtualBox; this project uses a documented ARM64 virtualization adaptation. '
           'Its 4 GiB allocation is within the handout\'s permitted lighter-setup option. '
           'A stopped-disk APFS clone named SECURELAB-CLEAN provides the tested recovery point. '
           'The absent instructor shared-memory example is replaced by a synchronized anonymous mapping. '
           'Recorded guest platform: '+manifest['platform']+'.')
    threat=('Assets: synthetic incident/configuration records, process memory, credentials and availability. '
            'Untrusted subjects: Bob, malformed input and a compromised unprivileged application. '
            'Trusted dependencies: guest kernel, administrator, toolchain, integrity baseline and host virtualization stack. '
            'Assessment scope: lab accounts, owned processes, /opt/securelab fixtures and dedicated teaching services. '
            'The practice challenge touches only its synthetic files and transient services; public/production targets are outside scope.')
    after=(run/'mission-19/after.txt').read_text()
    pending=[line.split('/')[0] for line in after.splitlines() if '[upgradable from:' in line]
    limits=('The instructor-specific Mission 22 is the remaining external dependency: its rules and challenge image were not supplied. '
            'RBAC is a conceptual comparison, as requested, rather than a deployed role engine. '
            'Mission 14 messages are deliberately generated lab events, supported by the corresponding command trace. '
            'The unsafe C race is undefined behavior and observed counts are run-dependent. '
            'The umask baseline is an explicitly controlled file-creation fixture; it is not a reconstructed historical shell setting. '
            'Passing scoped tests does not prove absence of all vulnerabilities. Secure boot, encrypted storage and a hardware TEE were not measured. '
            'Pending packages after the final hardening audit: '+(', '.join(pending) if pending else 'none listed')+'.')
    improvements=('Apply the same baseline/control/retest method to the instructor challenge when it is provided. '
                  'Keep a trusted off-machine copy of the checksum manifest, add remote audit retention and clock monitoring, '
                  'and broaden sandbox regression coverage. Consider encrypted storage and verified boot as separate extensions. '
                  'Maintain restricted Docker access and review firewall behavior before publishing any container port.')
    out=ROOT/'output';out.mkdir(exist_ok=True)
    build_pdf(out,records,manifest,summary,scope,threat,limits,improvements)
    print(f'Generated submission PDF from {run}; {core}/21 core missions, {count}/22 lab scripts verified')


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
    field('System profile and environment adaptation',scope)
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
    rationales=[
        'Limit confidential records to the authorized analyst group while retaining Alice\'s required read access.',
        'Prevent an ordinary account from changing approved configuration without granting unnecessary root access.',
        'Protect directory entries as well as file contents; a writable directory can permit unauthorized creation or replacement.',
        'Remove an unnecessary reachable interface instead of relying only on its harmless current content.',
        'The worker needs no administrative operation. A non-root identity and no-new-privileges reduce the authority available after compromise.',
        'Detect later drift against a separately protected reference. The check establishes byte agreement, not authorship.'
    ]
    for i,f in enumerate(FINDINGS):
        if i==3:
            story.append(PageBreak());story.append(para('Practice findings - continued','Heading1'))
        story.append(KeepTogether([para(f[0]+' - '+f[1],'Heading2'),para('Before: '+f[2]),para('Remediation: '+f[3]),para('Rationale: '+rationales[i]),para('Verification: '+f[4])]))
    p('Full baseline, command traces and after-state are in mission-22 evidence. All six markers must be present before the runner records success.')
    # Explicit measured before/after hardening comparison.
    run=ROOT/'evidence/runs'/manifest['run_id']
    hardening=json.loads((ROOT/'docs/hardening-checklist.json').read_text())
    before=(run/'mission-19/before.txt').read_text()
    after=(run/'mission-19/after.txt').read_text()
    mask=(run/'mission-19/umask-verification.txt').read_text()
    initial=(run/'mission-19/attempt-1.log').read_text()
    assert 'Status: inactive' in initial
    assert re.search(r'^Uid:\s+0\s+0',before,re.M), 'Missing runtime root baseline'
    assert 'User=nobody' in after and re.search(r'^NoNewPrivs:\s+1',after,re.M)
    for marker in ['CONTROLLED_BASELINE_UMASK=0022','CONTROLLED_BASELINE_MODE=644','PROJECT_UMASK=0077','SECURED_FILE_MODE=600']:
        assert marker in mask,marker
    pending=[line for line in after.splitlines() if '[upgradable from:' in line]
    hardening['rows'][-1][2]=str(len(pending))+' pending packages listed in the final captured inventory.'
    story.append(PageBreak());story.append(para(hardening['title'],'Heading1'))
    p(hardening['baseline_note'])
    def grid(columns,rows,widths):
        cells=[[para(c,'SmallLab') for c in columns]]+[[para(c,'SmallLab') for c in row] for row in rows]
        tab=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#ccd9e3'))]))
        story.append(tab)
    grid(hardening['columns'],hardening['rows'],[82,120,130,A4[0]-432])
    field('Observed ordinary-file creation', 'The controlled baseline produces mode 0644. Loading the project policy produces mode 0600. Both assertions are checked on files created with touch inside a private directory.')
    field('Rollback',hardening['rollback'])
    story.append(para('Evidence: mission-19 initial/latest attempt logs, before.txt, after.txt and umask-verification.txt; evidence/provisioning/submission-patch-completion.log.','SmallLab'))
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
    p('These answers explain the captured results. Reflective answers analyze those results and their security implications; they do not invent unrecorded personal experience.')
    for r in records:
        h(f'Mission {r["id"]:02d} - {r["title"]}')
        for q,answer in r['answers'].items():
            story.append(KeepTogether([para('Q'+q,'LabelLab'),para(answer)]))
    story.append(PageBreak());story.append(para('Reflection on the recorded experiments','Heading1'))
    p('The following analysis connects the observed results to the final reflection questions in the handout.')
    for title,body in json.loads((ROOT/'docs/project-reflection.json').read_text()):
        h(title);p(body)
    story.append(PageBreak());story.append(para('Requirements-to-evidence map','Heading1'))
    p('Handout pages refer to the 35-page specification supplied for CS5101. All core mission entries below include the required evidence and explanations. Full logs live under evidence/runs/'+manifest['run_id']+'/; selected output and the eight evidence-template fields appear in each mission sheet.')
    mapped=[]
    for row in json.loads((ROOT/'docs/requirements-map.json').read_text()):
        n=row['mission'];execution=manifest['missions'][f'{n:02d}']
        artifacts=[execution['log'],*row['artifacts']]
        mapped.append([f'M{n:02d} / p'+row['handout_pages'],row['required'],'; '.join(artifacts),'Verified' if execution['status']=='verified' else execution['status']])
    grid(['Mission / page','Required submission evidence','Included artifacts','Core result'],mapped,[54,154,233,A4[0]-541])
    h('External dependency: instructor Mission 22')
    p('Handout page 29 requires a separately supplied challenge VM and rules document. These resources remain unavailable. The repository includes six verified practice findings with baseline, classification, control and retest evidence, but the official independent assessment is not marked completed.')
    h('Environment and report requirements')
    p('The guest uses Linux/Ubuntu 26.04 ARM64, 2 vCPUs, 4 GiB RAM, a 40 GiB sparse disk and NAT. Four GiB is the lighter-setup option permitted on handout page 3. The Desktop/VirtualBox recommendation is adapted to headless Lima/Apple virtualization. SECURELAB-CLEAN and FINAL-HARDENED stopped-disk copies were restore-tested. The project contains source, notes, command/output evidence and the required report topics: executive summary, system profile, threat model, attack surface, findings, remediation/rationale, verification, reflection and future improvements.')
    # Comparison tables required by the handout; all content is conceptual design.
    for t in json.loads((ROOT/'docs/design-tables.json').read_text()):
        story.append(PageBreak());story.append(para(t['title'],'Heading1'))
        p('Design rationale; actual permissions and resource limits are verified in the corresponding mission logs.')
        cells=[[para(c,'SmallLab') for c in t['columns']]]+[[para(c) for c in row] for row in t['rows']]
        tab=Table(cells,colWidths=[(A4[0]-100)/len(t['columns'])]*len(t['columns']),repeatRows=1,hAlign='LEFT')
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
        c.drawString(44,25,'SECURELAB / CS5101 / recorded laboratory evidence')
        c.drawRightString(w-44,25,str(doc.page));c.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)

if __name__=='__main__':main()
